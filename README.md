# People and Banner Detection

This repository detects people and textual banners in images and outputs JSON files as well as annotated images.

Quick start

- Install environment (Linux/macOS):
  - ./setup.sh
- Or for Windows:
  - setup_windows.bat

- Run detection:
  - python src/detect.py --input_dir images --output_dir output_images --output_json output_json --people_conf 0.5 --text_conf 0.3 --visualize

Outputs

- For each image, a JSON is created in `output_json/<image_stem>.json` and summary in `output_json/summary.json`.
- Annotated images are saved in `output_images/` with boxes and text overlay.

Requirements and reproducibility

- `requirements.txt` lists required Python packages.
- `Dockerfile` builds a minimal runtime image for the application.
- `run_test.sh` runs detection followed by `pytest`.

Testing

- Run `pytest` to execute unit tests in `tests/`.
- A concurrency test is provided but skipped by default; it can be enabled to verify concurrent writes.

Notes

- Person detection uses YOLOv8 (`ultralytics`) with the pretrained `yolov8n.pt` weights.
- OCR uses EasyOCR to detect text boxes and extract text.
- The script handles large images by resizing for inference (configurable) while mapping detections back to original coordinates.
- Corrupt/unreadable images are skipped and logged in per-image JSON.

