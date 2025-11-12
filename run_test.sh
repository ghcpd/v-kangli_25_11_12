#!/bin/bash
# Run test script for Computer Vision Detection System

set -e

echo "================================"
echo "CV Detection System - Test Suite"
echo "================================"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Virtual environment activated"
fi

# Run detection on sample images
echo "Running detection pipeline on sample images..."
python detect.py

echo ""
echo "Checking output files..."
if [ -f "detections.json" ]; then
    echo "✓ Detection results saved to detections.json"
    echo "  Sample detection count:"
    python -c "import json; data=json.load(open('detections.json')); print(f'  - Total images: {len(data)}')"
else
    echo "✗ detections.json not found"
fi

if [ -f "statistics.json" ]; then
    echo "✓ Statistics saved to statistics.json"
    python -c "import json; data=json.load(open('statistics.json')); print(f'  - Total people detected: {data.get(\"total_people_detected\", 0)}'); print(f'  - Total banners detected: {data.get(\"total_banners_detected\", 0)}')"
else
    echo "✗ statistics.json not found"
fi

if [ -d "output_images" ] && [ "$(ls -A output_images)" ]; then
    echo "✓ Annotated images saved to output_images/"
    count=$(ls output_images | wc -l)
    echo "  - Number of annotated images: $count"
else
    echo "✗ output_images is empty or not found"
fi

echo ""
echo "Running unit tests..."
pytest test_detection.py -v --tb=short

echo ""
echo "================================"
echo "Test Suite Completed!"
echo "================================"
