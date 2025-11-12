# 🖼️ Image Analysis Guide

## ⚠️ Current Status

Your system **does not have Python installed**, you need to complete environment setup before analyzing images.

## 📋 Step 1: Install Python

1. **Download Python**:
   - Visit https://www.python.org/downloads/
   - Download Python 3.8 or higher (recommended 3.10+)
   - Run the installer

2. **Important installation options**:
   - ✅ **Check "Add Python to PATH"** (add to environment variables)
   - Choose "Install Now" or custom installation path

3. **Verify installation**:
   - Open a new command prompt (cmd)
   - Run: `python --version`
   - Should display Python version number

## 📋 Step 2: Set Up Project Environment

After installing Python, run:

```cmd
setup.bat
```

This script will:
- Create virtual environment
- Install all required dependency packages (YOLO, EasyOCR, etc.)
- May take a few minutes (first-time model download)

## 📋 Step 3: Run Image Analysis

After environment setup is complete, there are two ways:

### Method 1: Using Automatic Script (Recommended)
```cmd
run_analysis.bat
```

### Method 2: Manual Execution
```cmd
venv\Scripts\activate
python detector.py
```

## 📊 Analysis Results

After analysis completes, you will get:

1. **results.json** - Detection results for each image
   ```json
   {
     "image_id": "images_1.jpg",
     "detections": {
       "people": [
         {"x_min": 100, "y_min": 50, "x_max": 200, "y_max": 400, "confidence": 0.95}
       ],
       "banners": [
         {"x_min": 50, "y_min": 10, "x_max": 300, "y_max": 60, "confidence": 0.92, "text": "Detected text"}
       ]
     }
   }
   ```

2. **statistics.json** - Statistical summary
   - Number of images processed
   - Total number of people detected
   - Total number of banners detected
   - Average confidence, etc.

3. **output_images/** - Annotated images
   - Green boxes = People
   - Red boxes = Banners/signs
   - Display confidence and recognized text

## 🎯 Quick Command Reference

```cmd
# Set up environment (first run)
setup.bat

# Run analysis
run_analysis.bat

# Or run manually
venv\Scripts\activate
python detector.py

# Custom parameters (lower threshold to detect more)
python detector.py --person-conf 0.2 --banner-conf 0.4

# Support Chinese OCR
python detector.py --languages en ch_sim
```

## 💡 Tips

- **First run**: Will automatically download AI models (~500MB-1GB), requires internet connection
- **Processing time**: About 5-30 seconds per image (depends on image size)
- **Memory requirements**: Recommend at least 4GB available memory
- **Image formats**: Supports JPG and PNG formats

## ❓ Need Help?

If you encounter problems, please check:
1. Is Python correctly installed and added to PATH?
2. Is network connection normal? (First run needs to download models)
3. Check error messages and solve problems according to prompts

---

**When ready, please follow steps 1→2→3 in order!**

