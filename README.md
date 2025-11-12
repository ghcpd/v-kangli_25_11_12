# People and Banner Detection Pipeline

This repository contains a small pipeline to detect people (human figures) and textual banners/signs in images. It outputs per-image JSON, annotated images with bounding boxes, and a summary statistics JSON.

## Usage

- Install dependencies using the provided scripts or Dockerfile.

Local (Linux/macOS):

1. Setup venv and install requirements:

   ```bash
   ./setup.sh
   source .venv/bin/activate
   ```

2. Run detection on the `images/` folder:

   ```bash
   python scripts/detect.py --images_dir images --output_dir outputs --output_images_dir output_images --weights yolov8n.pt
   ```

Docker:

1. Build Docker image:

   ```bash
   docker build -t people-banner-detect .
   ```

2. Run container:

   ```bash
   docker run --rm -v $PWD:/app people-banner-detect
   ```

## Testing

- On Linux/macOS:
  - Run `./run_test.sh`
- On Windows:
  - Run `run_test.bat`
  - Or run tests via pytest: `pytest -q`

## Configuration

- You can adjust confidence thresholds and NMS IOU using CLI args:
  - `--person_conf`: Confidence threshold for person detection (default 0.25)
  - `--iou`: IOU threshold for NMS (default 0.45)
  - `--ocr_conf`: OCR confidence threshold 0-1 (default 0.5)
  - `--min_banner_area`: Minimum pixel area to treat as a valid banner

## Notes

- The pipeline uses Ultralytics YOLOv8 for person detection. Ensure you have a compatible GPU or the model will run in CPU mode.
- OCR uses Tesseract via `pytesseract`. Install `tesseract-ocr` on your system (Dockerfile includes this).

## Outputs

- JSON per image: `outputs/<image_stem>.json` containing cluster of person and banner detections.
- Annotated images in `output_images/`.
- `outputs/summary.json` contains overall statistics.