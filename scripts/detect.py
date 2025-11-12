"""
Detect people and textual banners in images using YOLO (people) and pytesseract (text).
Produces per-image JSON, annotated images, and a summary JSON.
"""
import argparse
import json
import os
import sys
import traceback
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# We import lazily so that users without dependencies can get helpful errors
try:
    from ultralytics import YOLO
except Exception:
    YOLO = None

try:
    import pytesseract
except Exception:
    pytesseract = None


def load_yolo_model(weights: str = 'yolov8n.pt'):
    if YOLO is None:
        raise RuntimeError("ultralytics is not installed. See requirements.txt or use setup.sh to install dependencies.")
    model = YOLO(weights)
    return model


def detect_people(image_bgr, model, conf_threshold=0.25, iou_threshold=0.45):
    # YOLO model expects RGB images
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    results = model.predict(source=image_rgb, imgsz=640, conf=conf_threshold, iou=iou_threshold, verbose=False)
    people = []
    # COCO class for person is 0
    for r in results:
        boxes = r.boxes
        for b in boxes:
            cls = int(b.cls.cpu().numpy())
            conf = float(b.conf.cpu().numpy())
            if cls == 0 and conf >= conf_threshold:
                x1, y1, x2, y2 = map(int, b.xyxy[0].cpu().numpy())
                people.append({"x_min": int(x1), "y_min": int(y1), "x_max": int(x2), "y_max": int(y2), "confidence": float(conf)})
    return people


def detect_text_regions(image_bgr, ocr_conf_threshold=50):
    if pytesseract is None:
        raise RuntimeError("pytesseract is not installed. See requirements.txt or use setup.sh to install dependencies.")
    # Convert to RGB PIL image (pytesseract expects RGB)
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(image_rgb)
    data = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DICT)
    n_boxes = len(data['level'])
    words = []
    for i in range(n_boxes):
        conf = int(data['conf'][i]) if data['conf'][i] != '-1' else -1
        text = data['text'][i].strip()
        if conf >= ocr_conf_threshold and text:
            (x, y, w, h) = (int(data['left'][i]), int(data['top'][i]), int(data['width'][i]), int(data['height'][i]))
            words.append({"x_min": x, "y_min": y, "x_max": x + w, "y_max": y + h, "confidence": conf / 100.0, "text": text})
    # Group words into lines/banners by y coordinate proximity
    if not words:
        return []
    words = sorted(words, key=lambda w: (w['y_min'], w['x_min']))
    banners = []
    current = words[0].copy()
    for w in words[1:]:
        # if nearly same line (y overlap), merge into current
        y_overlap = min(current['y_max'], w['y_max']) - max(current['y_min'], w['y_min'])
        if y_overlap > 0 or abs(w['y_min'] - current['y_min']) < 10:
            current['x_min'] = min(current['x_min'], w['x_min'])
            current['y_min'] = min(current['y_min'], w['y_min'])
            current['x_max'] = max(current['x_max'], w['x_max'])
            current['y_max'] = max(current['y_max'], w['y_max'])
            current['confidence'] = max(current.get('confidence', 0), w['confidence'])
            current['text'] = (current.get('text', '') + ' ' + w['text']).strip()
        else:
            banners.append(current)
            current = w.copy()
    banners.append(current)
    return banners


def annotate_and_save(image_bgr, people, banners, output_path):
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    pil = Image.fromarray(image_rgb)
    draw = ImageDraw.Draw(pil)
    # try to pick a reasonable font
    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except Exception:
        font = ImageFont.load_default()
    # Draw people
    for p in people:
        draw.rectangle([p['x_min'], p['y_min'], p['x_max'], p['y_max']], outline="red", width=3)
        text = f"Person {p['confidence']:.2f}"
        draw.text((p['x_min'] + 2, p['y_min'] - 16), text, fill="red", font=font)
    # Draw banners
    for b in banners:
        draw.rectangle([b['x_min'], b['y_min'], b['x_max'], b['y_max']], outline="green", width=3)
        text = f"{b.get('text','')} {b['confidence']:.2f}"
        draw.text((b['x_min'] + 2, b['y_min'] - 16), text[:80], fill="green", font=font)
    # Save as RGB
    pil.save(output_path)


def process_images(images_dir: Path, output_dir: Path, output_images_dir: Path, model, args):
    images_dir = Path(images_dir)
    output_dir = Path(output_dir)
    output_images_dir = Path(output_images_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_images_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "total_images": 0,
        "total_people": 0,
        "total_banners": 0,
        "people_confidences": [],
        "banner_confidences": [],
        "per_image": []
    }

    for img_path in sorted(images_dir.glob("*.jpg")) + sorted(images_dir.glob("*.png")):
        summary['total_images'] += 1
        try:
            img = cv2.imread(str(img_path))
            if img is None:
                raise ValueError("Unreadable/Corrupt image")
            people = detect_people(img, model, conf_threshold=args.person_conf, iou_threshold=args.iou)
            banners = detect_text_regions(img, ocr_conf_threshold=int(args.ocr_conf * 100))

            # Filter banners by OCR confidence threshold (already applied) and optionally min size
            if args.min_banner_area > 0:
                filtered_banners = []
                for b in banners:
                    area = (b['x_max'] - b['x_min']) * (b['y_max'] - b['y_min'])
                    if area >= args.min_banner_area:
                        filtered_banners.append(b)
                banners = filtered_banners

            # collect stats
            summary['total_people'] += len(people)
            summary['total_banners'] += len(banners)
            summary['people_confidences'].extend([p['confidence'] for p in people])
            summary['banner_confidences'].extend([b['confidence'] for b in banners])
            per_image = {
                "image_id": img_path.name,
                "people_count": len(people),
                "banner_count": len(banners)
            }
            summary['per_image'].append(per_image)

            # Save per-image JSON
            out = {
                "image_id": img_path.name,
                "detections": {
                    "people": people,
                    "banners": banners
                }
            }
            json_out_path = output_dir / (img_path.stem + ".json")
            with open(json_out_path, 'w', encoding='utf-8') as f:
                json.dump(out, f, indent=2)

            # Annotate and save
            annotate_and_save(img, people, banners, output_images_dir / img_path.name)

        except Exception as e:
            # Log errors and continue
            err_msg = f"Error processing {img_path.name}: {e}"
            print(err_msg, file=sys.stderr)
            try:
                with open(output_dir / 'errors.log', 'a', encoding='utf-8') as ef:
                    ef.write(err_msg + "\n")
            except Exception:
                pass
            traceback.print_exc()
            continue

    # finalize summary
    summary_out = {
        "total_images": summary['total_images'],
        "total_people": summary['total_people'],
        "total_banners": summary['total_banners'],
        "avg_people_per_image": (summary['total_people'] / summary['total_images']) if summary['total_images'] else 0,
        "avg_banners_per_image": (summary['total_banners'] / summary['total_images']) if summary['total_images'] else 0,
        "avg_confidence_people": (float(np.mean(summary['people_confidences'])) if summary['people_confidences'] else 0.0),
        "avg_confidence_banners": (float(np.mean(summary['banner_confidences'])) if summary['banner_confidences'] else 0.0),
        "max_people_in_image": max([p['people_count'] for p in summary['per_image']]) if summary['per_image'] else 0,
        "min_people_in_image": min([p['people_count'] for p in summary['per_image']]) if summary['per_image'] else 0,
        "max_banners_in_image": max([p['banner_count'] for p in summary['per_image']]) if summary['per_image'] else 0,
        "min_banners_in_image": min([p['banner_count'] for p in summary['per_image']]) if summary['per_image'] else 0,
        "per_image": summary['per_image']
    }
    with open(output_dir / "summary.json", 'w', encoding='utf-8') as f:
        json.dump(summary_out, f, indent=2)
    return summary_out


def parse_args():
    parser = argparse.ArgumentParser(description="Detect people and textual banners/signs in images")
    parser.add_argument('--images_dir', type=str, default='images', help='Path to images folder')
    parser.add_argument('--output_dir', type=str, default='outputs', help='Path to JSON outputs')
    parser.add_argument('--output_images_dir', type=str, default='output_images', help='Path to annotated images')
    parser.add_argument('--weights', type=str, default='yolov8n.pt', help='YOLO weights')
    parser.add_argument('--person_conf', type=float, default=0.25, help='Confidence threshold for person detection')
    parser.add_argument('--iou', type=float, default=0.45, help='IOU threshold for NMS')
    parser.add_argument('--ocr_conf', type=float, default=0.5, help='OCR confidence threshold (0-1)')
    parser.add_argument('--min_banner_area', type=int, default=0, help='Minimum banner area in pixels')
    return parser.parse_args()


def main():
    args = parse_args()
    print("Loading YOLO model...")
    model = load_yolo_model(args.weights)
    out = process_images(args.images_dir, args.output_dir, args.output_images_dir, model, args)
    print("Done. Summary:")
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
