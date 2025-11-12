import os
import json

def test_output_json_structure():
    summary_path = os.path.join('outputs', 'summary.json')
    assert os.path.exists(summary_path)

    with open(summary_path, 'r') as f:
        s = json.load(f)
    assert 'total_images' in s
    assert 'per_image' in s
    # pick a per-image file
    for f in os.listdir('images'):
        if f.lower().endswith(('.jpg', '.png')):
            jfile = os.path.join('outputs', os.path.splitext(f)[0] + '.json')
            assert os.path.exists(jfile)
            with open(jfile, 'r') as j:
                data = json.load(j)
            assert 'image_id' in data
            assert 'detections' in data
            assert 'people' in data['detections']
            assert 'banners' in data['detections']
            # People items should have expected keys if present
            for p in data['detections']['people']:
                assert set(p.keys()) >= {'x_min', 'y_min', 'x_max', 'y_max', 'confidence'}
            for b in data['detections']['banners']:
                assert set(b.keys()) >= {'x_min', 'y_min', 'x_max', 'y_max', 'confidence', 'text'}
