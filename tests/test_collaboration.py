# This file contains a simple concurrency test template for collaboration/persistence/conflict handling.
# It's a skeleton to simulate two parallel runs writing to different output folders and checking atomic file writes.

import os
import shutil
import threading
import subprocess


def run_instance(instance_id):
    out_dir = f"outputs_instance_{instance_id}"
    out_img_dir = f"output_images_instance_{instance_id}"
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(out_img_dir, exist_ok=True)
    cmd = ["python", "scripts/detect.py", "--images_dir", "images", "--output_dir", out_dir, "--output_images_dir", out_img_dir]
    subprocess.run(cmd, check=True)


def test_parallel_runs(tmp_path):
    # Run two threads in parallel to simulate concurrent access
    t1 = threading.Thread(target=run_instance, args=(1,))
    t2 = threading.Thread(target=run_instance, args=(2,))
    t1.start(); t2.start()
    t1.join(); t2.join()
    # Check outputs exist for both
    assert os.path.exists('outputs_instance_1/summary.json')
    assert os.path.exists('outputs_instance_2/summary.json')
