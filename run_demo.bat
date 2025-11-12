@echo off
REM Run pipeline on images folder
python -m src.detect_all --input images --output outputs/detections.json --out-images output_images
