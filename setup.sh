#!/bin/bash
# Setup script for Computer Vision Detection System

set -e  # Exit on error

echo "================================"
echo "CV Detection System Setup"
echo "================================"

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Found Python: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Create output directories
echo "Creating output directories..."
mkdir -p output_images
mkdir -p results
mkdir -p logs

echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "To activate the environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the detection pipeline, execute:"
echo "  python detect.py"
echo ""
echo "To run tests, execute:"
echo "  pytest test_detection.py -v"
echo ""
