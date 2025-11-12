#!/usr/bin/env bash
# Setup virtual environment and install dependencies
python -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup complete. Activate the venv with: source .venv/bin/activate"
