#!/bin/bash

# Setup script for Linux/Mac

set -e

echo "Setting up Computer Vision Detection System..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p images output_images

# Download YOLO model (will be downloaded automatically on first run)
echo "Setup complete!"
echo ""
echo "To use the system:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Place images in the 'images/' directory"
echo "3. Run: python detector.py"
echo ""
echo "For testing:"
echo "python test_detector.py"

