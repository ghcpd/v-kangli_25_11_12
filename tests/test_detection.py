import os
import json
import subprocess
import time
import shutil
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
IMAGES_DIR = ROOT / 'images'
OUTPUT_IMAGES_DIR = ROOT / 'output_images'
OUTPUT_JSON_DIR = ROOT / 'output_json'


def run_detection_once(extra_args=None):
    cmd = ['python', str(ROOT / 'src' / 'detect.py'), '--input_dir', str(IMAGES_DIR), '--output_dir', str(OUTPUT_IMAGES_DIR), '--output_json', str(OUTPUT_JSON_DIR), '--visualize']
    if extra_args:
        cmd.extend(extra_args)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc


@pytest.mark.skipif(not IMAGES_DIR.exists() or not any(IMAGES_DIR.glob('*.*')), reason='No input images available')
def test_detection_outputs_created(tmp_path):
    # Clean outputs
    if OUTPUT_IMAGES_DIR.exists():
        shutil.rmtree(OUTPUT_IMAGES_DIR)
    if OUTPUT_JSON_DIR.exists():
        shutil.rmtree(OUTPUT_JSON_DIR)
    OUTPUT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON_DIR.mkdir(parents=True, exist_ok=True)

    proc = run_detection_once(['--people_conf', '0.35', '--text_conf', '0.2', '--max_side', '800'])
    assert proc.returncode == 0, f"Detect returned non-zero; stderr: {proc.stderr}"
    # Verify combined results and summary exist
    combined = OUTPUT_JSON_DIR / 'combined_results.json'
    summary = OUTPUT_JSON_DIR / 'summary.json'
    assert combined.exists() and summary.exists()

    with combined.open('r', encoding='utf-8') as f:
        data = json.load(f)
    assert isinstance(data, list)

    with summary.open('r', encoding='utf-8') as f:
        s = json.load(f)
    assert 'total_images' in s


@pytest.mark.skip(reason='Concurrency test may use additional resources; run explicitly')
def test_concurrent_runs(tmp_path):
    # Spawn a few processes simultaneously that share the same output folder; ensure resulting summary.json is valid
    procs = []
    for i in range(3):
        p = subprocess.Popen(['python', str(ROOT / 'src' / 'detect.py'), '--input_dir', str(IMAGES_DIR), '--output_dir', str(OUTPUT_IMAGES_DIR), '--output_json', str(OUTPUT_JSON_DIR)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        procs.append(p)
    for p in procs:
        p.wait(timeout=300)
    summary = OUTPUT_JSON_DIR / 'summary.json'
    assert summary.exists()
    with summary.open('r', encoding='utf-8') as f:
        s = json.load(f)
    assert 'total_images' in s

