# API Documentation

Computer Vision Detection System - Complete API Reference

## Table of Contents
1. [ImageProcessor](#imageprocessor)
2. [PersonDetector](#persondetector)
3. [TextDetector](#textdetector)
4. [Visualizer](#visualizer)
5. [Data Classes](#data-classes)
6. [Configuration](#configuration)
7. [Examples](#examples)

---

## ImageProcessor

Main orchestrator class for the detection pipeline.

### Constructor

```python
ImageProcessor(person_confidence: float = 0.3, 
               text_confidence: float = 0.1)
```

**Parameters:**
- `person_confidence` (float): Confidence threshold for person detection (0.0-1.0)
- `text_confidence` (float): Confidence threshold for text detection (0.0-1.0)

**Example:**
```python
from detect import ImageProcessor

# Default settings
processor = ImageProcessor()

# Custom settings
processor = ImageProcessor(person_confidence=0.5, text_confidence=0.2)
```

### Methods

#### process_image

```python
process_image(image_path: str) -> Optional[Dict[str, Any]]
```

Process a single image and detect persons and text.

**Parameters:**
- `image_path` (str): Path to the image file

**Returns:**
- Dictionary with detection results or None if processing failed

**Example:**
```python
result = processor.process_image("images/photo.jpg")
if result:
    people = len(result["detections"]["people"])
    banners = len(result["detections"]["banners"])
    print(f"Found {people} people and {banners} banners")
```

**Return Structure:**
```python
{
    "image_id": str,
    "image_path": str,
    "image_size": {"width": int, "height": int},
    "detections": {
        "people": [DetectionBox, ...],
        "banners": [TextBanner, ...]
    },
    "person_count": int,
    "banner_count": int,
    "timestamp": str
}
```

#### process_folder

```python
process_folder(folder_path: str) -> List[Dict[str, Any]]
```

Process all images in a folder.

**Parameters:**
- `folder_path` (str): Path to folder containing images

**Returns:**
- List of detection results for all processed images

**Example:**
```python
results = processor.process_folder("images/")
print(f"Processed {len(results)} images")
```

#### get_statistics

```python
get_statistics() -> Dict[str, Any]
```

Calculate statistics from processed images.

**Returns:**
- Dictionary with aggregated statistics

**Example:**
```python
stats = processor.get_statistics()
print(f"Total people: {stats['total_people_detected']}")
print(f"Average confidence: {stats['average_confidence_people']:.2%}")
```

**Statistics Keys:**
```python
{
    "total_images_processed": int,
    "failed_images": int,
    "total_people_detected": int,
    "total_banners_detected": int,
    "average_people_per_image": float,
    "average_banners_per_image": float,
    "average_confidence_people": float,
    "average_confidence_banners": float,
    "max_people_in_single_image": int,
    "min_people_in_single_image": int,
    "max_banners_in_single_image": int,
    "min_banners_in_single_image": int,
    "images_with_people": int,
    "images_with_banners": int,
    "timestamp": str
}
```

### Properties

- `person_detector` (PersonDetector): The person detection model
- `text_detector` (TextDetector): The text detection model
- `processed_images` (List): Results from processed images
- `failed_images` (List): Failed image processing records

---

## PersonDetector

Detects human figures using YOLOv8.

### Constructor

```python
PersonDetector(model_name: str = "yolov8n.pt", 
               confidence_threshold: float = 0.3)
```

**Parameters:**
- `model_name` (str): YOLOv8 model to use
  - "yolov8n.pt" (nano - fastest)
  - "yolov8s.pt" (small)
  - "yolov8m.pt" (medium)
  - "yolov8l.pt" (large)
  - "yolov8x.pt" (extra large - most accurate)
- `confidence_threshold` (float): Detection confidence threshold (0.0-1.0)

**Example:**
```python
from detect import PersonDetector

# Default (nano model, fast)
detector = PersonDetector()

# Medium model for better accuracy
detector = PersonDetector(model_name="yolov8m.pt", confidence_threshold=0.4)
```

### Methods

#### detect

```python
detect(image: np.ndarray) -> List[DetectionBox]
```

Detect persons in an image.

**Parameters:**
- `image` (np.ndarray): Image in BGR format (from cv2.imread)

**Returns:**
- List of DetectionBox objects for detected persons

**Example:**
```python
import cv2

image = cv2.imread("photo.jpg")
detections = detector.detect(image)

for detection in detections:
    print(f"Person at ({detection.x_min}, {detection.y_min})")
    print(f"Confidence: {detection.confidence:.2%}")
```

---

## TextDetector

Detects and recognizes text using EasyOCR.

### Constructor

```python
TextDetector(languages: List[str] = ['en'], 
             gpu: bool = False,
             confidence_threshold: float = 0.1)
```

**Parameters:**
- `languages` (List[str]): Language codes for OCR
- `gpu` (bool): Enable GPU acceleration
- `confidence_threshold` (float): Detection confidence threshold (0.0-1.0)

**Example:**
```python
from detect import TextDetector

# English only, CPU
detector = TextDetector()

# Multiple languages, GPU enabled
detector = TextDetector(languages=['en', 'zh', 'ja'], gpu=True)
```

### Methods

#### detect

```python
detect(image: np.ndarray) -> List[TextBanner]
```

Detect and extract text from image.

**Parameters:**
- `image` (np.ndarray): Image in BGR format

**Returns:**
- List of TextBanner objects with detected text

**Example:**
```python
import cv2

image = cv2.imread("poster.jpg")
banners = detector.detect(image)

for banner in banners:
    print(f"Text: '{banner.text}'")
    print(f"Position: ({banner.x_min}, {banner.y_min}) to ({banner.x_max}, {banner.y_max})")
    print(f"Confidence: {banner.confidence:.2%}")
```

---

## Visualizer

Creates annotated images with detection visualization.

### Methods

#### draw_detections

```python
@staticmethod
draw_detections(image: np.ndarray,
                persons: List[DetectionBox],
                banners: List[TextBanner]) -> np.ndarray
```

Draw bounding boxes on image.

**Parameters:**
- `image` (np.ndarray): Input image in BGR format
- `persons` (List[DetectionBox]): Detected persons
- `banners` (List[TextBanner]): Detected banners

**Returns:**
- Annotated image with bounding boxes

**Example:**
```python
from detect import Visualizer, DetectionBox, TextBanner
import cv2

image = cv2.imread("photo.jpg")
persons = [DetectionBox(10, 20, 100, 200, 0.95)]
banners = [TextBanner(50, 300, 200, 350, 0.92, "Hello")]

annotated = Visualizer.draw_detections(image, persons, banners)
cv2.imwrite("annotated.jpg", annotated)
```

#### save_annotated_images

```python
@staticmethod
save_annotated_images(results: List[Dict[str, Any]],
                     output_folder: str) -> None
```

Save annotated images to folder.

**Parameters:**
- `results` (List): Detection results from ImageProcessor
- `output_folder` (str): Path to output folder

**Example:**
```python
processor = ImageProcessor()
results = processor.process_folder("images/")
Visualizer.save_annotated_images(results, "output_images/")
```

---

## Data Classes

### DetectionBox

Represents a detected object's bounding box.

```python
@dataclass
class DetectionBox:
    x_min: int           # Left coordinate
    y_min: int           # Top coordinate
    x_max: int           # Right coordinate
    y_max: int           # Bottom coordinate
    confidence: float    # Detection confidence (0.0-1.0)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
```

**Example:**
```python
from detect import DetectionBox

box = DetectionBox(x_min=10, y_min=20, x_max=100, y_max=150, confidence=0.95)
print(f"Box coordinates: ({box.x_min}, {box.y_min}) to ({box.x_max}, {box.y_max})")
print(f"Width: {box.x_max - box.x_min}")
print(f"Height: {box.y_max - box.y_min}")
```

### TextBanner

Represents detected text with bounding box.

```python
@dataclass
class TextBanner(DetectionBox):
    text: str = ""  # Extracted text content
```

**Example:**
```python
from detect import TextBanner

banner = TextBanner(
    x_min=50, y_min=300, x_max=200, y_max=350,
    confidence=0.92, text="Welcome"
)
print(f"Text: '{banner.text}'")
print(f"Location: ({banner.x_min}, {banner.y_min})")
```

---

## Configuration

### Config Class

Centralized configuration management.

```python
from config import Config

# Get all configuration
config = Config.get_all()

# Modify configuration
Config.PERSON_CONFIDENCE_THRESHOLD = 0.5
Config.TEXT_CONFIDENCE_THRESHOLD = 0.2

# Save configuration
Config.save_to_file("config.json")

# Load configuration
Config.load_from_file("config.json")

# Validate configuration
if Config.validate():
    print("Configuration is valid")
```

### Available Configuration Options

```python
# Detection thresholds
PERSON_CONFIDENCE_THRESHOLD = 0.3
TEXT_CONFIDENCE_THRESHOLD = 0.1

# Model configuration
PERSON_MODEL = "yolov8n.pt"
TEXT_LANGUAGES = ['en']
USE_GPU = False

# Paths
IMAGES_DIR = "images"
OUTPUT_DIR = "results"
OUTPUT_IMAGES_DIR = "output_images"
LOGS_DIR = "logs"

# Visualization
PERSON_BOX_COLOR = (255, 0, 0)  # BGR
TEXT_BOX_COLOR = (0, 255, 0)
BOX_THICKNESS = 2
FONT_SCALE = 0.5
```

### Preset Configurations

```python
from config import PresetConfig

# Apply preset
PresetConfig.apply_preset("high_accuracy")

# Available presets
# - high_accuracy: Slower, fewer false positives
# - high_speed: Faster, more false positives
# - balanced: Default settings
# - gpu_enabled: GPU accelerated
```

---

## Examples

### Basic Detection

```python
from detect import ImageProcessor, Visualizer

# Create processor
processor = ImageProcessor()

# Process folder
results = processor.process_folder("images/")

# Get statistics
stats = processor.get_statistics()
print(f"Processed {stats['total_images_processed']} images")
print(f"Found {stats['total_people_detected']} people")

# Create annotated images
Visualizer.save_annotated_images(results, "output_images/")
```

### Advanced Detection

```python
from detect import ImageProcessor, PersonDetector, TextDetector

# Create custom detectors
person_detector = PersonDetector(model_name="yolov8m.pt", confidence_threshold=0.5)
text_detector = TextDetector(languages=['en', 'zh'], gpu=True)

# Create processor with custom detectors
processor = ImageProcessor()
processor.person_detector = person_detector
processor.text_detector = text_detector

# Process image
result = processor.process_image("photo.jpg")
```

### Custom Processing

```python
from detect import PersonDetector, TextDetector
import cv2

# Load image
image = cv2.imread("photo.jpg")

# Detect persons
person_detector = PersonDetector()
persons = person_detector.detect(image)

# Detect text
text_detector = TextDetector()
banners = text_detector.detect(image)

# Process results
for person in persons:
    print(f"Person with {person.confidence:.1%} confidence")

for banner in banners:
    print(f"Text: {banner.text}")
```

---

**Last Updated**: November 12, 2025  
**API Version**: 1.0.0
