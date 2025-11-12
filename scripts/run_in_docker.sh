#!/usr/bin/env bash
set -e
NAME=people-banner-detector
# Mount repo into container and run tutorial commandnames
docker run --rm -it -v $(pwd):/app ${NAME}:latest python src/detect.py --input_dir images --output_dir output_images --output_json output_json --visualize
