# Quick Start Guide

## Installation (Choose One Method)

### Method 1: Automated Setup (Recommended)

**Windows:**
```cmd
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

### Method 2: Manual Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Method 3: Docker

```bash
docker build -t cv-detector .
docker run -v $(pwd)/images:/app/images -v $(pwd)/output_images:/app/output_images cv-detector
```

## Basic Usage

1. **Place images** in the `images/` folder (jpg or png format)

2. **Run detection:**
```bash
python detector.py
```

3. **View results:**
   - `results.json` - Detection results with bounding boxes
   - `statistics.json` - Summary statistics
   - `output_images/` - Annotated images with bounding boxes

## Custom Configuration

```bash
# Lower thresholds for more detections
python detector.py --person-conf 0.2 --banner-conf 0.4

# Multiple languages for OCR
python detector.py --languages en ch_sim ja

# Custom paths
python detector.py --input my_images/ --output my_output/
```

## Testing

**Windows:**
```cmd
run_test.bat
```

**Linux/Mac:**
```bash
chmod +x run_test.sh
./run_test.sh
```

## Output Files

- `results.json` - All detections with coordinates and confidence
- `statistics.json` - Processing statistics
- `output_images/*` - Visualized results with bounding boxes
- `test_report.json` - Test execution results (after running tests)

## Troubleshooting

**No detections?** → Lower confidence thresholds
**OCR not working?** → Check image quality, try different languages
**Out of memory?** → System automatically falls back to CPU mode
**Model download issues?** → Check internet connection

For detailed documentation, see README.md

