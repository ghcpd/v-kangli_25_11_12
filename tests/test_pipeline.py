import os
import json
import cv2
import numpy as np
import tempfile

from src.detect_all import main

class DummyPersonDetector:
    def __init__(self):
        pass
    def detect(self, image):
        # pretend there's one person in center
        h,w = image.shape[:2]
        return [{'x_min': w//3, 'y_min': h//3, 'x_max': 2*w//3, 'y_max': 2*h//3, 'confidence': 0.9}]

class DummyTextDetector:
    def __init__(self):
        pass
    def detect(self, image):
        h,w = image.shape[:2]
        return [{'x_min': int(w*0.1), 'y_min': int(h*0.1), 'x_max': int(w*0.9), 'y_max': int(h*0.2), 'confidence': 0.95, 'text': 'Hello'}]


def test_pipeline_basic(monkeypatch, tmp_path):
    # create temporary image dir
    img_dir = tmp_path / 'images'
    img_dir.mkdir()
    # create a simple synthetic image
    img = 255 * np.ones((480,640,3), dtype=np.uint8)
    path1 = str(img_dir / 'img1.jpg')
    cv2.imwrite(path1, img)

    # create a corrupt image file
    with open(str(img_dir / 'corrupt.jpg'), 'wb') as f:
        f.write(b'not-an-image')

    monkeypatch.setattr('src.detect_all.PersonDetector', lambda device, conf_thresh: DummyPersonDetector())
    monkeypatch.setattr('src.detect_all.TextDetector', lambda gpu, conf_thresh: DummyTextDetector())

    out_json = str(tmp_path / 'out.json')
    out_images = str(tmp_path / 'output_images')
    res = main(input_dir=str(img_dir), output_json=out_json, output_images_dir=out_images, person_conf=0.2, banner_conf=0.2)

    assert os.path.exists(out_json)
    with open(out_json, 'r') as f:
        data = json.load(f)
    assert 'images' in data
    # one good image processed, one corrupt logged
    assert data['stats']['total_images'] == 1
    assert data['stats']['total_people'] == 1
    assert data['stats']['total_banners'] == 1
    assert len(data['errors']) == 1


def test_stats_edge_cases(monkeypatch, tmp_path):
    # empty dir
    img_dir = tmp_path / 'images'
    img_dir.mkdir()
    monkeypatch.setattr('src.detect_all.PersonDetector', lambda device, conf_thresh: DummyPersonDetector())
    monkeypatch.setattr('src.detect_all.TextDetector', lambda gpu, conf_thresh: DummyTextDetector())
    out_json = str(tmp_path / 'out.json')
    out_images = str(tmp_path / 'output_images')
    res = main(input_dir=str(img_dir), output_json=out_json, output_images_dir=out_images)
    with open(out_json, 'r') as f:
        data = json.load(f)
    assert data['stats']['total_images'] == 0
    assert data['stats']['total_people'] == 0
    assert data['stats']['total_banners'] == 0

