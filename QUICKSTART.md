# Quick Start Guide

## 5-Minute Setup & First Run

### Prerequisites
- Python 3.8 or higher
- 2-4 GB free disk space (for model weights)
- 2-6 GB RAM

### Option 1: Windows (Easiest)

1. **Open Command Prompt** in the project folder
2. **Run setup**: `setup.bat`
3. **Start detection**: `python detect.py`

Done! Check `results/detections.json` for results.

### Option 2: Linux/Mac

1. **Open Terminal** in the project folder
2. **Run setup**: `chmod +x setup.sh && ./setup.sh`
3. **Activate environment**: `source venv/bin/activate`
4. **Start detection**: `python detect.py`

Done! Check `results/detections.json` for results.

### Option 3: Docker

1. **Build image**: `docker build -t cv-detection .`
2. **Run detection**:
```bash
docker run --rm \
  -v $(pwd)/images:/app/images \
  -v $(pwd)/output:/app/output \
  cv-detection:latest python detect.py
```

Done! Check `output/detections.json` for results.

---

## What Happens When You Run?

1. **Initialization** - Loads YOLOv8 and EasyOCR models (~2 GB download on first run)
2. **Image Processing** - Scans all images in the `images/` folder
3. **Detection** - Finds persons and text in each image
4. **Output Generation** - Creates:
   - `detections.json` - All detections with coordinates
   - `statistics.json` - Summary statistics
   - `output_images/` - Annotated images

---

## Output Files Explained

### detections.json
```json
[
  {
    "image_id": "images_1.jpg",
    "detections": {
      "people": [
        {"x_min": 34, "y_min": 50, "x_max": 120, "y_max": 310, "confidence": 0.95}
      ],
      "banners": [
        {"x_min": 50, "y_min": 400, "x_max": 400, "y_max": 480, "confidence": 0.92, "text": "Sign text"}
      ]
    }
  }
]
```

### statistics.json
```json
{
  "total_images_processed": 5,
  "total_people_detected": 12,
  "total_banners_detected": 8,
  "average_people_per_image": 2.4,
  "average_confidence_people": 0.92
}
```

---

## Common Customizations

### Change Detection Sensitivity

Edit `detect.py` and change line ~800:
```python
main(person_confidence=0.5, text_confidence=0.2)  # Stricter
main(person_confidence=0.2, text_confidence=0.05)  # Looser
```

### Disable Annotated Images

Edit `detect.py` line ~800:
```python
# Comment out this line:
# Visualizer.save_annotated_images(results, output_images)
```

### Use GPU for Text Detection

Edit `detect.py` line ~35:
```python
self.reader = easyocr.Reader(languages, gpu=True)  # Change to True
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "No module named 'ultralytics'" | Run: `pip install -r requirements.txt` |
| "Out of memory" | Use nano model: Edit detect.py and change `"yolov8n.pt"` (already default) |
| "No detections found" | Increase sensitivity: `person_confidence=0.2` |
| "Very slow" | Use GPU or reduce image resolution |
| "CUDA out of memory" | Use smaller model `yolov8n.pt` or reduce batch size |

---

## Next Steps

1. **Review Results**
   - Open `detections.json` to see raw detections
   - Open `output_images/` folder to see annotated images

2. **Configure Settings**
   - Edit `config.py` for persistent configuration
   - Use presets: `PresetConfig.apply_preset("high_accuracy")`

3. **Run Tests**
   - Windows: `run_test.bat`
   - Linux/Mac: `chmod +x run_test.sh && ./run_test.sh`

4. **Explore Examples**
   - Run: `python examples.py`
   - Shows 9 different usage patterns

5. **Read Documentation**
   - `README.md` - Full documentation
   - `API.md` - API reference
   - `CHANGELOG.md` - Version history

---

## Performance Tips

### Speed Up Processing
- Use `yolov8n.pt` model (default)
- Set `person_confidence=0.2` to detect faster
- Reduce image resolution in preprocessing

### Improve Accuracy
- Use `yolov8m.pt` or `yolov8l.pt` model
- Set `person_confidence=0.5` or higher
- Enable GPU

### Reduce Memory Usage
- Use `yolov8n.pt` (uses ~2 GB)
- Process images one at a time
- Close other applications

---

## File Structure After First Run

```
v-kangli_25_11_12/
├── images/
│   ├── images_1.jpg
│   ├── images_2.png
│   └── ... (your images)
├── output_images/           ← Generated
│   ├── annotated_images_1.jpg
│   └── ... (annotated images)
├── results/                 ← Generated
│   ├── detections.json
│   └── statistics.json
├── logs/                    ← Generated
│   └── detection.log
├── venv/                    ← Generated
│   └── (virtual environment)
└── detect.py, test_detection.py, etc.
```

---

## Key Keyboard Shortcuts

| Action | Command |
|--------|---------|
| Stop processing | Press `Ctrl+C` |
| Activate venv (Windows) | `venv\Scripts\activate.bat` |
| Activate venv (Linux/Mac) | `source venv/bin/activate` |
| Deactivate venv | `deactivate` |
| View logs | `cat detection.log` (Linux/Mac) or `type detection.log` (Windows) |

---

## Need Help?

1. Check `README.md` for comprehensive documentation
2. Check `API.md` for API reference
3. Check `examples.py` for usage examples
4. Run tests to verify installation: `python -m pytest test_detection.py -v`

---

**Happy Detecting! 🎉**

*Computer Vision Detection System v1.0.0*
