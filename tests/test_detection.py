import os
import json
import subprocess


def test_run_detection():
    # Run detection script
    cmd = ["python", "scripts/detect.py", "--images_dir", "images", "--output_dir", "outputs", "--output_images_dir", "output_images"]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    assert proc.returncode == 0, f"detect.py failed: {proc.stderr}"

    # Check summary
    assert os.path.exists("outputs/summary.json")
    with open("outputs/summary.json", 'r') as f:
        data = json.load(f)
    assert 'total_images' in data
    # check per image jsons
    for f in os.listdir('images'):
        if f.lower().endswith(('.jpg', '.png')):
            assert os.path.exists(os.path.join('outputs', os.path.splitext(f)[0] + '.json'))
