#!/bin/bash

# One-click test runner script

set -e

echo "=========================================="
echo "Computer Vision Detection System - Tests"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup first..."
    bash setup.sh
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Run tests
echo "Running test suite..."
echo ""
python test_detector.py

echo ""
echo "=========================================="
echo "Tests completed!"
echo "Check test_report.json for detailed results"
echo "=========================================="

