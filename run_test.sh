#!/usr/bin/env bash
set -e

# Run the detection script and then pytest
python src/detect.py --input_dir images --output_dir output_images --output_json output_json --people_conf 0.5 --text_conf 0.45 --visualize True
pytest -q
