#!/usr/bin/env bash
set -e
# Run the detection script and validate outputs exist
python scripts/detect.py --images_dir images --output_dir outputs --output_images_dir output_images --weights yolov8n.pt

if [ -f outputs/summary.json ]; then
  echo "Summary file created"
else
  echo "Missing summary.json"; exit 1
fi

# Check at least outputs for each image
for f in images/*.jpg images/*.png; do
  b=$(basename "$f")
  j=outputs/${b%.*}.json
  if [ -f "$j" ]; then
    echo "$j exists"
  else
    echo "Missing $j"; exit 1
  fi
done

echo "All tests passed."
