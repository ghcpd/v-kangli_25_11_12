# Computer Vision Detection System

A comprehensive computer vision system for detecting people and textual banners/signs in images using YOLO for person detection and EasyOCR for text detection and recognition.

## Features

- **Person Detection**: Detects all human figures in images using YOLOv8
- **Banner/Sign Detection**: Detects and extracts text from banners, signs, and slogans using OCR
- **Bounding Boxes**: Provides precise coordinates (x_min, y_min, x_max, y_max) for each detection
- **Confidence Scores**: Returns detection confidence for each detected entity
- **Statistics**: Comprehensive statistics including averages, min/max counts, and confidence metrics
- **Visualization**: Generates annotated images with bounding boxes and text overlays
- **JSON Output**: Structured JSON output for easy integration
- **Error Handling**: Gracefully handles corrupt or unreadable images
- **Configurable Thresholds**: Adjustable confidence thresholds for both people and banners

## Requirements

- Python 3.8 or higher
- CUDA-capable GPU (optional, for faster processing)
- At least 4GB RAM
- 2GB+ disk space for models

## Quick Start

### Option 1: Using Setup Scripts

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
source venv/bin/activate
python detector.py
```

**Windows:**
```cmd
setup.bat
venv\Scripts\activate
python detector.py
```

### Option 2: Manual Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the detector:
```bash
python detector.py
```

### Option 3: Using Docker

```bash
# Build the Docker image
docker build -t cv-detector .

# Run the container
docker run -v $(pwd)/images:/app/images -v $(pwd)/output_images:/app/output_images cv-detector
```

## Usage

### Basic Usage

Place your images in the `images/` directory and run:

```bash
python detector.py
```

### Command Line Options

```bash
python detector.py [OPTIONS]

Options:
  --input PATH              Input folder with images (default: images/)
  --output PATH             Output folder for annotated images (default: output_images/)
  --results PATH            Output JSON file for results (default: results.json)
  --stats PATH              Output JSON file for statistics (default: statistics.json)
  --person-conf FLOAT       Person detection confidence threshold (default: 0.25)
  --banner-conf FLOAT       Banner detection confidence threshold (default: 0.5)
  --yolo-model PATH         YOLO model path (default: yolov8n.pt)
  --languages LANG [LANG]   OCR languages (default: en)
  --no-visualize            Skip visualization generation
```

### Examples

**Process images with custom thresholds:**
```bash
python detector.py --person-conf 0.3 --banner-conf 0.6
```

**Process images with multiple OCR languages:**
```bash
python detector.py --languages en ch_sim ja
```

**Skip visualization:**
```bash
python detector.py --no-visualize
```

**Custom input/output paths:**
```bash
python detector.py --input my_images/ --output my_output/ --results my_results.json
```

## Output Format

### Detection Results (results.json)

```json
{
  "results": [
    {
      "image_id": "street_001.jpg",
      "detections": {
        "people": [
          {
            "x_min": 34,
            "y_min": 50,
            "x_max": 120,
            "y_max": 310,
            "confidence": 0.95
          }
        ],
        "banners": [
          {
            "x_min": 50,
            "y_min": 400,
            "x_max": 400,
            "y_max": 480,
            "confidence": 0.92,
            "text": "Welcome to the park"
          }
        ]
      }
    }
  ]
}
```

### Statistics (statistics.json)

```json
{
  "total_images_processed": 10,
  "total_people_detected": 25,
  "total_banners_detected": 15,
  "average_people_per_image": 2.5,
  "average_banners_per_image": 1.5,
  "average_confidence_people": 0.87,
  "average_confidence_banners": 0.82,
  "max_people_in_image": 5,
  "min_people_in_image": 0,
  "max_banners_in_image": 3,
  "min_banners_in_image": 0,
  "failed_images": 0,
  "failed_image_paths": []
}
```

## Testing

### Run All Tests

**Linux/Mac:**
```bash
chmod +x run_test.sh
./run_test.sh
```

**Windows:**
```cmd
run_test.bat
```

### Manual Test Execution

```bash
python test_detector.py
```

Test results will be saved to `test_report.json`.

### Test Coverage

The test suite includes:
- Person detection functionality
- Banner detection and OCR
- Pipeline integration
- JSON serialization and persistence
- Error handling (corrupt images, empty folders)
- Multi-image batch processing
- Statistics computation

## Project Structure

```
.
├── detector.py              # Main detection script
├── test_detector.py         # Comprehensive test suite
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── setup.sh                # Linux/Mac setup script
├── setup.bat               # Windows setup script
├── run_test.sh             # Linux/Mac test runner
├── run_test.bat            # Windows test runner
├── test_report_template.json  # Test report template
├── images/                 # Input images directory
├── output_images/          # Annotated output images
├── results.json            # Detection results (generated)
└── statistics.json         # Statistics (generated)
```

## Performance Considerations

- **Image Resolution**: The system handles varying image resolutions automatically
- **GPU Acceleration**: EasyOCR and YOLO can use GPU if available (automatically detected)
- **Memory Usage**: Large images are processed efficiently
- **Batch Processing**: Multiple images are processed sequentially
- **Error Recovery**: Corrupt images are skipped and logged

## Model Information

- **Person Detection**: Uses YOLOv8 (nano version by default)
  - Model is automatically downloaded on first run
  - Supports other YOLOv8 variants (s, m, l, x)
  
- **Text Detection**: Uses EasyOCR
  - Supports 80+ languages
  - Pre-trained models downloaded automatically
  - Can be configured for multiple languages simultaneously

## Troubleshooting

### Common Issues

**Issue**: "CUDA out of memory"
- **Solution**: Use CPU mode or reduce batch size. EasyOCR defaults to CPU if GPU memory is insufficient.

**Issue**: "Model download failed"
- **Solution**: Check internet connection. Models are downloaded automatically on first run.

**Issue**: "No detections found"
- **Solution**: Lower confidence thresholds using `--person-conf` and `--banner-conf` options.

**Issue**: "OCR not detecting text"
- **Solution**: 
  - Ensure text is clearly visible and not too small
  - Try different language codes with `--languages`
  - Lower banner confidence threshold

### Performance Tips

1. **Use GPU**: Install CUDA-enabled PyTorch for faster processing
2. **Adjust Thresholds**: Lower thresholds for more detections, higher for precision
3. **Image Preprocessing**: Ensure images are well-lit and text is readable
4. **Batch Processing**: Process multiple images in one run for efficiency

## Development

### Adding New Features

The codebase is modular and extensible:

- `PersonDetector`: Handles person detection
- `BannerDetector`: Handles text detection and OCR
- `DetectionPipeline`: Orchestrates the detection process

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is provided as-is for computer vision detection tasks.

## Acknowledgments

- YOLOv8 by Ultralytics
- EasyOCR for text detection and recognition
- OpenCV for image processing

## Support

For issues or questions, please check:
1. Test results in `test_report.json`
2. Log output for detailed error messages
3. Statistics file for processing summary
