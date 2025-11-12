import os
import json
import cv2
import numpy as np
from pathlib import Path
from tempfile import NamedTemporaryFile


def list_image_files(input_dir):
    image_files = []
    input_dir = Path(input_dir)
    for ext in ["*.jpg", "*.jpeg", "*.png", "*.bmp"]:
        image_files.extend(input_dir.glob(ext))
    return sorted(image_files)


def safe_imread(path):
    try:
        img = cv2.imdecode(np.fromfile(str(path), dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Failed to decode image")
        return img
    except Exception as e:
        raise RuntimeError(f"Unable to read image {path}: {e}")


def easyocr_box_to_bbox(bbox_quad):
    # bbox_quad is a list of 4 points [(x1,y1),(x2,y2),(x3,y3),(x4,y4)]
    x_coords = [p[0] for p in bbox_quad]
    y_coords = [p[1] for p in bbox_quad]
    xmin = int(min(x_coords))
    ymin = int(min(y_coords))
    xmax = int(max(x_coords))
    ymax = int(max(y_coords))
    return xmin, ymin, xmax, ymax


def draw_boxes(image, people, banners, thickness=2):
    img = image.copy()
    # People - blue boxes
    for p in people:
        x1, y1, x2, y2 = p['x_min'], p['y_min'], p['x_max'], p['y_max']
        conf = p['confidence']
        cv2.rectangle(img, (x1,y1), (x2,y2), (255,0,0), thickness)
        label = f"person {conf:.2f}"
        cv2.putText(img, label, (x1, max(10, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)

    # Banners - green boxes and text
    for b in banners:
        x1, y1, x2, y2 = b['x_min'], b['y_min'], b['x_max'], b['y_max']
        conf = b['confidence']
        txt = b.get('text', '')
        cv2.rectangle(img, (x1,y1), (x2,y2), (0,255,0), thickness)
        label = f"{txt} ({conf:.2f})"
        # put text just above the top-left corner
        cv2.putText(img, label, (x1, max(10, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
    return img


def save_json_atomic(data, out_path):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile('w', delete=False, dir=str(out_path.parent), prefix=out_path.stem, suffix='.tmp', encoding='utf-8') as tmpf:
        json.dump(data, tmpf, ensure_ascii=False, indent=2)
        tmp_name = tmpf.name
    # Replace atomically
    os.replace(tmp_name, out_path)


def agg_stats(per_image_records):
    stats = {
        'total_images': 0,
        'total_people': 0,
        'total_banners': 0,
        'avg_people_per_image': 0.0,
        'avg_banners_per_image': 0.0,
        'avg_confidence_people': 0.0,
        'avg_confidence_banners': 0.0,
        'max_people_in_image': 0,
        'min_people_in_image': None,
        'max_banners_in_image': 0,
        'min_banners_in_image': None,
    }
    if not per_image_records:
        return stats
    total_images = len(per_image_records)
    total_people = sum(len(r['detections']['people']) for r in per_image_records)
    total_banners = sum(len(r['detections']['banners']) for r in per_image_records)
    people_confs = [p['confidence'] for r in per_image_records for p in r['detections']['people']]
    banners_confs = [b['confidence'] for r in per_image_records for b in r['detections']['banners']]

    stats['total_images'] = total_images
    stats['total_people'] = total_people
    stats['total_banners'] = total_banners
    stats['avg_people_per_image'] = total_people / total_images
    stats['avg_banners_per_image'] = total_banners / total_images
    stats['avg_confidence_people'] = (sum(people_confs) / len(people_confs)) if people_confs else 0.0
    stats['avg_confidence_banners'] = (sum(banners_confs) / len(banners_confs)) if banners_confs else 0.0
    people_counts = [len(r['detections']['people']) for r in per_image_records]
    banner_counts = [len(r['detections']['banners']) for r in per_image_records]
    stats['max_people_in_image'] = max(people_counts)
    stats['min_people_in_image'] = min(people_counts)
    stats['max_banners_in_image'] = max(banner_counts)
    stats['min_banners_in_image'] = min(banner_counts)
    return stats

