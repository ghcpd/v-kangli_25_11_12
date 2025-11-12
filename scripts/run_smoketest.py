"""
A quick smoke test runner for the detection pipeline. Useful in CI.
"""
import subprocess
import sys

cmd = ["python", "scripts/detect.py", "--images_dir", "images", "--output_dir", "outputs", "--output_images_dir", "output_images"]
proc = subprocess.run(cmd)
if proc.returncode != 0:
    print("Smoke test failed", file=sys.stderr)
    sys.exit(1)
else:
    print("Smoke test passed")
