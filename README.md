# Person + Banner Detection Pipeline

This repository contains a pipeline to detect people and textual banners/signs in images, generate bounding boxes, extract text, and produce visualizations and statistics.

Usage:
- Install dependencies: pip install -r requirements.txt
- Run: python -m src.detect_all --input images --output outputs/detections.json
- Annotated images saved to `output_images/`.

Features:
- Person detection (YOLOv8)
- Text detection and OCR (EasyOCR)
- Grouping of detected text into banners
- JSON output with people and banners per image
- Annotated images with overlays

Notes:
- `requirements.txt` and `Dockerfile` are included for reproducibility.
- Tests are provided using pytest under `tests/`.

Additional configuration:
- Pass `--person-conf` and `--banner-conf` to control detection thresholds.
- Use `--device` to specify `cpu` or `gpu` if available.

Testing & CI:
- Run `pytest -q` to execute automated tests.
- Use `run_test.bat` on Windows, or `bash setup.sh` to set up environment and `pytest` to run tests.