#!/usr/bin/env python3

import argparse
import json
import sys
import os
from pathlib import Path
from typing import List
import cv2
import numpy as np
from tqdm import tqdm

from config import IMAGES_DIR, OUTPUT_IMAGES_DIR, OUTPUT_JSON_DIR, DEFAULT_PEOPLE_CONF, DEFAULT_TEXT_CONF, MAX_IMAGE_SIDE
from utils import list_image_files, safe_imread, easyocr_box_to_bbox, draw_boxes, save_json_atomic, agg_stats

try:
    from ultralytics import YOLO
except Exception as e:
    print("Warning: ultralytics not installed or failed to import. Please install requirements.")
    YOLO = None

try:
    import easyocr
except Exception as e:
    print("Warning: EasyOCR not installed. Please install requirements.")
    easyocr = None


def parse_args():
    parser = argparse.ArgumentParser(description="Detect human figures and textual banners in images.")
    parser.add_argument("--input_dir", default=str(IMAGES_DIR), help="Directory with input images")
    parser.add_argument("--output_dir", default=str(OUTPUT_IMAGES_DIR), help="Directory to save annotated images")
    parser.add_argument("--output_json", default=str(OUTPUT_JSON_DIR), help="Directory to save JSON outputs")
    parser.add_argument("--people_conf", default=DEFAULT_PEOPLE_CONF, type=float, help="Confidence threshold for people detection")
    parser.add_argument("--text_conf", default=DEFAULT_TEXT_CONF, type=float, help="Confidence threshold for OCR text boxes")
    parser.add_argument("--visualize", action='store_true', help="Save annotated images with bounding boxes")
    parser.add_argument("--max_side", default=MAX_IMAGE_SIDE, type=int, help="Max side to resize images for faster inference")
    return parser.parse_args()


def scale_down_if_needed(img, max_side):
    h, w = img.shape[:2]
    max_dim = max(h, w)
    if max_dim <= max_side:
        return img, 1.0
    scale = max_side / max_dim
    new_w = int(w * scale)
    new_h = int(h * scale)
    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return resized, scale


def run_detection_on_image(img_path: Path, model, reader, people_conf: float, text_conf: float, visualize: bool, out_img_dir: Path, out_json_dir: Path, max_side: int):
    record = {
        'image_id': img_path.name,
        'detections': {
            'people': [],
            'banners': []
        }
    }
    try:
        img = safe_imread(img_path)
    except Exception as e:
        # return record with error note
        record['error'] = str(e)
        return record

    # scale image for faster inference, but remember scale factor
    orig_h, orig_w = img.shape[:2]
    scaled_img, scale = scale_down_if_needed(img, max_side)

    people_detections = []
    if model is not None:
        try:
            results = model.predict(source=scaled_img, imgsz=None, conf=people_conf, verbose=False)
            # ultralytics returns list results, pick first
            if isinstance(results, list):
                res = results[0]
            else:
                res = results
            # res.boxes returns Boxes object; res.boxes.data is an ndarray of shape (N,6): x1,y1,x2,y2,conf,class
            boxes_tensor = getattr(res.boxes, 'xyxy', None)
            boxes_data = None
            try:
                # The structure may vary by ultralytics version; fall back to .boxes.data
                if hasattr(res.boxes, 'data'):
                    boxes_data = res.boxes.data.cpu().numpy()
                else:
                    # may be a tensor
                    boxes_data = np.array(res.boxes.xyxy.cpu())
            except Exception:
                # fallback parse - try using res.boxes.xyxy
                try:
                    boxes_data = np.array(res.boxes.xyxy)
                except Exception:
                    boxes_data = None
            if boxes_data is not None:
                # boxes_data: N x 6 -> x1,y1,x2,y2,confidence,class
                for item in boxes_data:
                    x1, y1, x2, y2, conf, cls = item.tolist()
                    # Only person class (COCO class 0) is selected
                    if int(cls) == 0 and conf >= people_conf:
                        # scale back to original image coordinates
                        scale_factor = 1.0 / scale
                        x1o = int(max(0, min(orig_w, int(x1 * scale_factor))))
                        y1o = int(max(0, min(orig_h, int(y1 * scale_factor))))
                        x2o = int(max(0, min(orig_w, int(x2 * scale_factor))))
                        y2o = int(max(0, min(orig_h, int(y2 * scale_factor))))
                        people_detections.append({'x_min': x1o, 'y_min': y1o, 'x_max': x2o, 'y_max': y2o, 'confidence': float(conf)})
        except Exception as e:
            # detection failed for this image, log small note
            record['people_detection_error'] = str(e)
            people_detections = []

    # OCR text detection
    banners = []
    if reader is not None:
        try:
                # EasyOCR expects RGB; convert from OpenCV BGR
            scaled_img_rgb = cv2.cvtColor(scaled_img, cv2.COLOR_BGR2RGB)
            results = reader.readtext(scaled_img_rgb)
            # results is list of (bbox, text, confidence)
            for bbox_quad, text, conf in results:
                if conf < text_conf:
                    continue
                # bbox_quad coords correspond to scaled image
                xmin, ymin, xmax, ymax = easyocr_box_to_bbox(bbox_quad)
                # scale back
                scale_factor = 1.0 / scale
                x1o = int(max(0, min(orig_w, int(xmin * scale_factor))))
                y1o = int(max(0, min(orig_h, int(ymin * scale_factor))))
                x2o = int(max(0, min(orig_w, int(xmax * scale_factor))))
                y2o = int(max(0, min(orig_h, int(ymax * scale_factor))))
                banners.append({'x_min': x1o, 'y_min': y1o, 'x_max': x2o, 'y_max': y2o, 'confidence': float(conf), 'text': text})
        except Exception as e:
            record['text_detection_error'] = str(e)
            banners = []

    # fill record
    record['detections']['people'] = people_detections
    record['detections']['banners'] = banners

    # Save annotated image and per-image JSON
    out_json_dir = Path(out_json_dir)
    out_img_dir = Path(out_img_dir)
    out_img_dir.mkdir(parents=True, exist_ok=True)
    out_json_dir.mkdir(parents=True, exist_ok=True)
    image_json_name = out_json_dir / f"{img_path.stem}.json"

    # Save image annotation if needed
    if visualize:
        annotated = draw_boxes(img, people_detections, banners, thickness=2)
        # cv2.imwrite lacks support for non-ascii paths on Windows, use imencode & write
        ext = '.' + img_path.suffix.lstrip('.')
        dst_path = out_img_dir / f"{img_path.stem}_annot{ext}"
        # Write file using imencode and tofile to support unicode path
        _, enc = cv2.imencode(ext, annotated)
        enc.tofile(str(dst_path))

    # Save json atomic
    save_json_atomic(record, image_json_name)

    return record


def main():
    args = parse_args()

    image_files = list_image_files(args.input_dir)
    model = None
    reader = None
    if YOLO is not None:
        try:
            model = YOLO('yolov8n.pt')
        except Exception as e:
            print('Failed to initialize YOLO model; person detection will be skipped', e)
            model = None
    if easyocr is not None:
        try:
            reader = easyocr.Reader(['en'])
        except Exception as e:
            print('Failed to initialize EasyOCR reader; text detection will be skipped', e)
            reader = None

    per_image_records = []
    corrupted_count = 0

    for img_path in tqdm(image_files, desc='Processing'): 
        record = run_detection_on_image(Path(img_path), model, reader, args.people_conf, args.text_conf, args.visualize, args.output_dir, args.output_json, args.max_side)
        per_image_records.append(record)
        if 'error' in record:
            corrupted_count += 1

    # Save combined results and summary
    combined_out = Path(args.output_json) / 'combined_results.json'
    save_json_atomic(per_image_records, combined_out)

    stats = agg_stats([r for r in per_image_records if 'error' not in r])
    stats['corrupt_images_skipped'] = corrupted_count
    stats_path = Path(args.output_json) / 'summary.json'
    save_json_atomic(stats, stats_path)

    # Print concise summary
    print('\nRun summary:')
    print(f"Processed {len(image_files)} images; corrupted: {corrupted_count}")
    print(f"Total people: {stats['total_people']}")
    print(f"Total banners: {stats['total_banners']}")
    print(f"Avg people per image: {stats['avg_people_per_image']:.2f}")
    print(f"Avg banners per image: {stats['avg_banners_per_image']:.2f}")


if __name__ == '__main__':
    main()
