import os
import json
from glob import glob
import cv2
import numpy as np
from pathlib import Path
from tqdm import tqdm

from src.person_detector import PersonDetector
from src.text_detector import TextDetector
from src.visualize import draw_boxes
from src.config import DEFAULTS


def process_image(path, person_detector, text_detector, confs):
    try:
        img = cv2.imread(path)
        if img is None:
            raise IOError("image read failed")
    except Exception as e:
        return None, {'error': str(e)}

    people = person_detector.detect(img)
    banners = text_detector.detect(img)

    # filter by conf thresholds
    people = [p for p in people if p['confidence'] >= confs['people']]
    banners = [b for b in banners if b['confidence'] >= confs['banners']]

    return {'people': people, 'banners': banners}, None


def compute_stats(results):
    n_images = len(results)
    total_people = sum(len(r['people']) for r in results)
    total_banners = sum(len(r['banners']) for r in results)
    avg_people = total_people / n_images if n_images else 0
    avg_banners = total_banners / n_images if n_images else 0
    avg_conf_people = (sum(p['confidence'] for r in results for p in r['people']) / total_people) if total_people else 0
    avg_conf_banners = (sum(b['confidence'] for r in results for b in r['banners']) / total_banners) if total_banners else 0
    max_people = max((len(r['people']) for r in results), default=0)
    min_people = min((len(r['people']) for r in results), default=0)
    max_banners = max((len(r['banners']) for r in results), default=0)
    min_banners = min((len(r['banners']) for r in results), default=0)
    return {
        'total_images': n_images,
        'total_people': total_people,
        'total_banners': total_banners,
        'avg_people_per_image': avg_people,
        'avg_banners_per_image': avg_banners,
        'avg_conf_people': avg_conf_people,
        'avg_conf_banners': avg_conf_banners,
        'max_people_in_image': max_people,
        'min_people_in_image': min_people,
        'max_banners_in_image': max_banners,
        'min_banners_in_image': min_banners
    }


def main(input_dir='images', output_json='outputs/detections.json', output_images_dir='output_images', person_conf=0.25, banner_conf=0.3, device='cpu'):
    os.makedirs(output_images_dir, exist_ok=True)
    os.makedirs(os.path.dirname(output_json), exist_ok=True)

    person_detector = PersonDetector(device=device, conf_thresh=person_conf)
    text_detector = TextDetector(gpu=False, conf_thresh=banner_conf)

    confs = {'people': person_conf, 'banners': banner_conf}

    image_paths = glob(os.path.join(input_dir, '*.*'))
    processed = []
    errors = []

    for p in tqdm(image_paths, desc='Processing images'):
        res, err = process_image(p, person_detector, text_detector, confs)
        image_id = os.path.basename(p)
        if err:
            errors.append({'image_id': image_id, 'error': err})
            continue
        processed.append({'image_id': image_id, 'detections': res})

        # annotate image
        img = cv2.imread(p)
        ann = draw_boxes(img, people=res['people'], banners=res['banners'])
        out_path = os.path.join(output_images_dir, image_id)
        cv2.imwrite(out_path, ann)

    stats = compute_stats([r['detections'] for r in processed])

    out = {'images': processed, 'stats': stats, 'errors': errors}
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2)

    print('Done. Results written to', output_json)
    return out

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='images', help='Input image directory')
    parser.add_argument('--output', default='outputs/detections.json', help='Output JSON file')
    parser.add_argument('--out-images', default='output_images', help='Output annotated images dir')
    parser.add_argument('--person-conf', type=float, default=0.25)
    parser.add_argument('--banner-conf', type=float, default=0.3)
    parser.add_argument('--device', default='cpu')
    args = parser.parse_args()
    main(input_dir=args.input, output_json=args.output, output_images_dir=args.out_images, person_conf=args.person_conf, banner_conf=args.banner_conf, device=args.device)
