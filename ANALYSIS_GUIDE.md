# Image Analysis Guide

## Quick Start

### Method 1: Using Automatic Script (Recommended)

Simply double-click `run_analysis.bat`, the script will automatically:
1. Check Python environment
2. Install dependencies (if needed)
3. Analyze all images in the images folder
4. Generate result files

### Method 2: Manual Execution

1. **Set up environment first** (if not already set up):
   ```cmd
   setup.bat
   ```

2. **Activate virtual environment**:
   ```cmd
   venv\Scripts\activate
   ```

3. **Run detector**:
   ```cmd
   python detector.py
   ```

## Output Results

After analysis completes, the following files will be generated:

1. **results.json** - Contains detailed detection results for each image:
   - Person detection: coordinates and confidence
   - Banner/sign detection: coordinates, confidence, and recognized text

2. **statistics.json** - Statistical information:
   - Total number of images processed
   - Total number of people detected
   - Total number of banners detected
   - Averages, maximums, minimums, etc.

3. **output_images/** - Annotated images:
   - Green boxes: detected people
   - Red boxes: detected banners/signs
   - Display confidence and recognized text

## Custom Configuration

If you need to adjust detection parameters, you can use:

```cmd
python detector.py --person-conf 0.3 --banner-conf 0.6
```

Parameter description:
- `--person-conf`: Person detection confidence threshold (default 0.25, lower = more detections)
- `--banner-conf`: Banner detection confidence threshold (default 0.5)
- `--languages`: OCR languages (default en, can add ch_sim for Chinese support)

## Important Notes

1. **First run**: Will automatically download YOLO model and OCR model, requires internet connection, may take a few minutes
2. **Processing time**: Processing time per image depends on image size and complexity
3. **Memory requirements**: Recommend at least 4GB available memory
4. **GPU acceleration**: If you have an NVIDIA GPU, it will automatically use GPU acceleration

## Troubleshooting

**Issue: Python not found**
- Solution: Install Python 3.8+, ensure it's added to PATH

**Issue: Dependency installation failed**
- Solution: Check network connection, or use domestic mirror:
  ```
  pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
  ```

**Issue: No detections found**
- Solution: Lower confidence thresholds:
  ```
  python detector.py --person-conf 0.2 --banner-conf 0.4
  ```

**Issue: OCR recognition inaccurate**
- Solution: Add Chinese support:
  ```
  python detector.py --languages en ch_sim
  ```

