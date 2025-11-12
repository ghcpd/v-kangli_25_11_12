#!/usr/bin/env bash
set -e
NAME=people-banner-detector
# Build minimal image; tag local
docker build -t ${NAME}:latest .

echo "Built ${NAME}:latest"
