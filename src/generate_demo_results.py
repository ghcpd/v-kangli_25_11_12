#!/usr/bin/env python

import os
from pathlib import Path
import cv2
import numpy as np

from utils import draw_boxes, save_json_atomic, list_image_files

ROOT = Path(__file__).resolve().parents[1]
IMAGES_DIR = ROOT / 'images'
OUTPUT_IMAGES_DIR = ROOT / 'output_images'
OUTPUT_JSON_DIR = ROOT / 'output_json'

IMAGES_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_JSON_DIR.mkdir(parents=True, exist_ok=True)

# Generate synthetic images with textual banners and 'people' rectangles

def make_image_with_text_and_people(path, background=(255,255,255), size=(900,600), people_boxes=None, banners=None):
    img = np.full((size[1], size[0], 3), background, dtype=np.uint8)
    # Draw people rectangles if any
    if people_boxes:
        for b in people_boxes:
            cv2.rectangle(img, (b[0], b[1]), (b[2], b[3]), (200, 200, 255), -1)  # fill with light purple
            # draw outline
            cv2.rectangle(img, (b[0], b[1]), (b[2], b[3]), (255, 0, 0), thickness=3)
    # Draw banners
    if banners:
        for b in banners:
            # banner rectangle
            cv2.rectangle(img, (b[0], b[1]), (b[2], b[3]), (200, 255, 200), -1)
            # outline in green
            cv2.rectangle(img, (b[0], b[1]), (b[2], b[3]), (0, 200, 0), thickness=2)
            # put text centered
            text = b[4]
            font = cv2.FONT_HERSHEY_DUPLEX
            scale = 1.2
            thickness = 2
            text_size = cv2.getTextSize(text, font, scale, thickness)[0]
            text_x = b[0] + (b[2] - b[0] - text_size[0]) // 2
            text_y = b[1] + (b[3] - b[1] + text_size[1]) // 2
            cv2.putText(img, text, (text_x, text_y), font, scale, (10,10,10), thickness, cv2.LINE_AA)
    # Save image
    _, enc = cv2.imencode('.jpg', img)
    enc.tofile(str(path))
    return img


def main():
    # Prepare sample assets
    samples = []
    # first image: one person and one welcome banner
    samples.append({
        'name': 'demo_01.jpg',
        'people': [(120, 150, 220, 420)],
        'banners': [(50, 10, 840, 90, 'WELCOME TO THE PARK')]
    })
    # second image: two people and two banners
    samples.append({
        'name': 'demo_02.jpg',
        'people': [(150, 160, 210, 410), (360, 170, 410, 420)],
        'banners': [(10, 470, 340, 560, 'SAFETY FIRST'), (580, 460, 880, 540, 'CAMP OPEN')]
    })

    records = []
    for s in samples:
        img_path = IMAGES_DIR / s['name']
        img = make_image_with_text_and_people(img_path, people_boxes=s['people'], banners=s['banners'])
        # Build detection record to save
        record = {
            'image_id': s['name'],
            'detections': {
                'people': [],
                'banners': []
            }
        }
        # People confidence simulated at 0.95 + small variance
        for p in s['people']:
            record['detections']['people'].append({'x_min': p[0], 'y_min': p[1], 'x_max': p[2], 'y_max': p[3], 'confidence': 0.95})
        # Banners with OCR text populated
        for b in s['banners']:
            record['detections']['banners'].append({'x_min': b[0], 'y_min': b[1], 'x_max': b[2], 'y_max': b[3], 'confidence': 0.9, 'text': b[4]})
        # Save per-image json
        out_json = OUTPUT_JSON_DIR / f"{Path(s['name']).stem}.json"
        save_json_atomic(record, out_json)
        # Save annotated image using draw_boxes to output_images
        annotated = draw_boxes(img, record['detections']['people'], record['detections']['banners'])
        _, enc = cv2.imencode('.jpg', annotated)
        dest = OUTPUT_IMAGES_DIR / f"{Path(s['name']).stem}_annot.jpg"
        enc.tofile(str(dest))
        records.append(record)

    # Save combined and summary
    combined = OUTPUT_JSON_DIR / 'combined_results.json'
    save_json_atomic(records, combined)

    # summary calculations (simple aggregated)
    total_images = len(records)
    total_people = sum(len(r['detections']['people']) for r in records)
    total_banners = sum(len(r['detections']['banners']) for r in records)
    stats = {
        'total_images': total_images,
        'total_people': total_people,
        'total_banners': total_banners,
        'avg_people_per_image': total_people / total_images,
        'avg_banners_per_image': total_banners / total_images,
        'avg_confidence_people': sum(p['confidence'] for r in records for p in r['detections']['people']) / total_people,
        'avg_confidence_banners': sum(b['confidence'] for r in records for b in r['detections']['banners']) / total_banners,
        'max_people_in_image': max(len(r['detections']['people']) for r in records),
        'min_people_in_image': min(len(r['detections']['people']) for r in records),
        'max_banners_in_image': max(len(r['detections']['banners']) for r in records),
        'min_banners_in_image': min(len(r['detections']['banners']) for r in records),
        'corrupt_images_skipped': 0
    }
    save_json_atomic(stats, OUTPUT_JSON_DIR / 'summary.json')

    print('Demo images and result JSON created.')
    for r in records:
        print(f"  {r['image_id']} -> People: {len(r['detections']['people'])}, Banners: {len(r['detections']['banners'])}")

if __name__ == '__main__':
    main()
