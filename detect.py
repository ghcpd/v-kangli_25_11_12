#!/usr/bin/env python3
"""
Computer Vision Detection System
Detects human figures and textual banners/signs in images using YOLOv8 and EasyOCR.
"""

import os
import json
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('detection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class DetectionBox:
    """Represents a detected object's bounding box"""
    x_min: int
    y_min: int
    x_max: int
    y_max: int
    confidence: float

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TextBanner(DetectionBox):
    """Represents a detected text banner/sign"""
    text: str = ""

    def to_dict(self) -> Dict:
        d = asdict(self)
        return d


class PersonDetector:
    """Detects human figures in images using YOLOv8"""
    
    def __init__(self, model_name: str = "yolov8n.pt", confidence_threshold: float = 0.3):
        """
        Initialize the person detector.
        
        Args:
            model_name: YOLOv8 model to use
            confidence_threshold: Confidence threshold for detections
        """
        try:
            from ultralytics import YOLO
            self.model = YOLO(model_name)
            self.confidence_threshold = confidence_threshold
            self.person_class_id = 0  # Person class in COCO dataset
            logger.info(f"Loaded YOLOv8 model: {model_name}")
        except ImportError:
            logger.error("ultralytics not installed. Install with: pip install ultralytics")
            raise

    def detect(self, image: np.ndarray) -> List[DetectionBox]:
        """
        Detect persons in an image.
        
        Args:
            image: Input image as numpy array (BGR format)
            
        Returns:
            List of DetectionBox objects for detected persons
        """
        try:
            results = self.model(image, conf=self.confidence_threshold, verbose=False)
            detections = []
            
            for result in results:
                for box in result.boxes:
                    if int(box.cls[0]) == self.person_class_id:
                        x_min, y_min, x_max, y_max = map(int, box.xyxy[0])
                        confidence = float(box.conf[0])
                        detections.append(DetectionBox(
                            x_min=x_min,
                            y_min=y_min,
                            x_max=x_max,
                            y_max=y_max,
                            confidence=confidence
                        ))
            
            return detections
        except Exception as e:
            logger.error(f"Error detecting persons: {e}")
            return []


class TextDetector:
    """Detects and recognizes text in images using EasyOCR"""
    
    def __init__(self, languages: List[str] = ['en'], gpu: bool = False, 
                 confidence_threshold: float = 0.1):
        """
        Initialize the text detector.
        
        Args:
            languages: List of language codes to recognize
            gpu: Whether to use GPU
            confidence_threshold: Confidence threshold for text detection
        """
        try:
            import easyocr
            self.reader = easyocr.Reader(languages, gpu=gpu)
            self.confidence_threshold = confidence_threshold
            logger.info(f"Loaded EasyOCR reader for languages: {languages}")
        except ImportError:
            logger.error("easyocr not installed. Install with: pip install easyocr")
            raise

    def detect(self, image: np.ndarray) -> List[TextBanner]:
        """
        Detect text regions and extract text content.
        
        Args:
            image: Input image as numpy array (BGR format)
            
        Returns:
            List of TextBanner objects with detected text
        """
        try:
            # Convert BGR to RGB for EasyOCR
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.reader.readtext(image_rgb)
            
            banners = []
            for result in results:
                bbox_points = result[0]  # 4 corner points
                text = result[1]
                confidence = float(result[2])
                
                if confidence >= self.confidence_threshold:
                    # Convert corner points to axis-aligned bbox
                    x_coords = [int(point[0]) for point in bbox_points]
                    y_coords = [int(point[1]) for point in bbox_points]
                    
                    x_min, x_max = min(x_coords), max(x_coords)
                    y_min, y_max = min(y_coords), max(y_coords)
                    
                    # Filter very small detections (likely noise)
                    width = x_max - x_min
                    height = y_max - y_min
                    if width > 10 and height > 10:  # Minimum size threshold
                        banners.append(TextBanner(
                            x_min=x_min,
                            y_min=y_min,
                            x_max=x_max,
                            y_max=y_max,
                            confidence=confidence,
                            text=text
                        ))
            
            return banners
        except Exception as e:
            logger.error(f"Error detecting text: {e}")
            return []


class ImageProcessor:
    """Main processor for detecting objects in images"""
    
    def __init__(self, person_confidence: float = 0.3, 
                 text_confidence: float = 0.1):
        """
        Initialize the image processor.
        
        Args:
            person_confidence: Confidence threshold for person detection
            text_confidence: Confidence threshold for text detection
        """
        self.person_detector = PersonDetector(confidence_threshold=person_confidence)
        self.text_detector = TextDetector(confidence_threshold=text_confidence)
        self.processed_images = []
        self.failed_images = []

    def process_image(self, image_path: str) -> Optional[Dict[str, Any]]:
        """
        Process a single image to detect persons and text.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with detection results or None if processing failed
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Unable to read image")
            
            image_name = Path(image_path).name
            logger.info(f"Processing: {image_name}")
            
            # Detect persons
            persons = self.person_detector.detect(image)
            
            # Detect text
            banners = self.text_detector.detect(image)
            
            result = {
                "image_id": image_name,
                "image_path": image_path,
                "image_size": {"width": image.shape[1], "height": image.shape[0]},
                "detections": {
                    "people": [p.to_dict() for p in persons],
                    "banners": [b.to_dict() for b in banners]
                },
                "person_count": len(persons),
                "banner_count": len(banners),
                "timestamp": datetime.now().isoformat()
            }
            
            self.processed_images.append(result)
            logger.info(f"Detected {len(persons)} persons and {len(banners)} banners")
            return result
            
        except Exception as e:
            logger.error(f"Error processing {image_path}: {e}")
            self.failed_images.append({
                "image_path": image_path,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            return None

    def process_folder(self, folder_path: str) -> List[Dict[str, Any]]:
        """
        Process all images in a folder.
        
        Args:
            folder_path: Path to folder containing images
            
        Returns:
            List of detection results
        """
        folder = Path(folder_path)
        results = []
        
        # Supported image formats
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        image_files = [f for f in folder.iterdir() 
                       if f.suffix.lower() in image_extensions]
        
        logger.info(f"Found {len(image_files)} images in {folder_path}")
        
        for image_file in sorted(image_files):
            result = self.process_image(str(image_file))
            if result:
                results.append(result)
        
        return results

    def get_statistics(self) -> Dict[str, Any]:
        """
        Calculate detection statistics from processed images.
        
        Returns:
            Dictionary containing detailed statistics
        """
        if not self.processed_images:
            return {
                "total_images": 0,
                "total_people": 0,
                "total_banners": 0,
                "note": "No images processed"
            }
        
        total_images = len(self.processed_images)
        total_people = sum(img["person_count"] for img in self.processed_images)
        total_banners = sum(img["banner_count"] for img in self.processed_images)
        
        # Collect all confidences
        person_confidences = []
        banner_confidences = []
        
        for img in self.processed_images:
            for person in img["detections"]["people"]:
                person_confidences.append(person["confidence"])
            for banner in img["detections"]["banners"]:
                banner_confidences.append(banner["confidence"])
        
        # Calculate statistics
        stats = {
            "total_images_processed": total_images,
            "failed_images": len(self.failed_images),
            "total_people_detected": total_people,
            "total_banners_detected": total_banners,
            "average_people_per_image": round(total_people / total_images, 2) if total_images > 0 else 0,
            "average_banners_per_image": round(total_banners / total_images, 2) if total_images > 0 else 0,
            "average_confidence_people": round(np.mean(person_confidences), 4) if person_confidences else 0,
            "average_confidence_banners": round(np.mean(banner_confidences), 4) if banner_confidences else 0,
            "max_people_in_single_image": max([img["person_count"] for img in self.processed_images], default=0),
            "min_people_in_single_image": min([img["person_count"] for img in self.processed_images], default=0),
            "max_banners_in_single_image": max([img["banner_count"] for img in self.processed_images], default=0),
            "min_banners_in_single_image": min([img["banner_count"] for img in self.processed_images], default=0),
            "images_with_people": sum(1 for img in self.processed_images if img["person_count"] > 0),
            "images_with_banners": sum(1 for img in self.processed_images if img["banner_count"] > 0),
            "timestamp": datetime.now().isoformat()
        }
        
        return stats


class Visualizer:
    """Creates annotated images with detection visualization"""
    
    @staticmethod
    def draw_detections(image: np.ndarray, 
                       persons: List[DetectionBox],
                       banners: List[TextBanner]) -> np.ndarray:
        """
        Draw bounding boxes and text on image.
        
        Args:
            image: Input image (BGR)
            persons: List of detected persons
            banners: List of detected banners
            
        Returns:
            Annotated image
        """
        annotated = image.copy()
        
        # Draw person detections (blue boxes)
        for person in persons:
            cv2.rectangle(annotated, 
                         (person.x_min, person.y_min),
                         (person.x_max, person.y_max),
                         (255, 0, 0), 2)  # Blue
            label = f"Person {person.confidence:.2f}"
            cv2.putText(annotated, label,
                       (person.x_min, person.y_min - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        
        # Draw text banner detections (green boxes with text)
        for banner in banners:
            cv2.rectangle(annotated,
                         (banner.x_min, banner.y_min),
                         (banner.x_max, banner.y_max),
                         (0, 255, 0), 2)  # Green
            
            # Draw text above the box
            label = f"Text: {banner.text[:20]} ({banner.confidence:.2f})"
            y_offset = banner.y_min - 10
            cv2.putText(annotated, label,
                       (banner.x_min, max(y_offset, 20)),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        return annotated

    @staticmethod
    def save_annotated_images(results: List[Dict[str, Any]], 
                             output_folder: str) -> None:
        """
        Save annotated images to output folder.
        
        Args:
            results: List of detection results
            output_folder: Path to output folder
        """
        os.makedirs(output_folder, exist_ok=True)
        
        for result in results:
            try:
                image = cv2.imread(result["image_path"])
                if image is None:
                    continue
                
                persons = [DetectionBox(**d) for d in result["detections"]["people"]]
                banners = [TextBanner(**d) for d in result["detections"]["banners"]]
                
                annotated = Visualizer.draw_detections(image, persons, banners)
                
                output_path = os.path.join(output_folder, f"annotated_{result['image_id']}")
                cv2.imwrite(output_path, annotated)
                logger.info(f"Saved annotated image: {output_path}")
                
            except Exception as e:
                logger.error(f"Error saving annotated image for {result['image_id']}: {e}")


def main(input_folder: str = "images",
         output_json: str = "detections.json",
         output_stats: str = "statistics.json",
         output_images: str = "output_images",
         person_confidence: float = 0.3,
         text_confidence: float = 0.1):
    """
    Main function to run the detection pipeline.
    
    Args:
        input_folder: Path to input images folder
        output_json: Path to output detections JSON
        output_stats: Path to output statistics JSON
        output_images: Path to output annotated images folder
        person_confidence: Confidence threshold for person detection
        text_confidence: Confidence threshold for text detection
    """
    logger.info("=" * 60)
    logger.info("Starting Computer Vision Detection Pipeline")
    logger.info("=" * 60)
    
    # Initialize processor
    processor = ImageProcessor(
        person_confidence=person_confidence,
        text_confidence=text_confidence
    )
    
    # Process images
    results = processor.process_folder(input_folder)
    
    # Get statistics
    stats = processor.get_statistics()
    
    # Save results to JSON
    os.makedirs(os.path.dirname(output_json) or ".", exist_ok=True)
    with open(output_json, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"Saved detections to: {output_json}")
    
    # Save statistics to JSON
    with open(output_stats, 'w') as f:
        json.dump(stats, f, indent=2)
    logger.info(f"Saved statistics to: {output_stats}")
    
    # Save annotated images
    Visualizer.save_annotated_images(results, output_images)
    
    # Print summary
    logger.info("=" * 60)
    logger.info("Detection Summary")
    logger.info("=" * 60)
    logger.info(f"Total images processed: {stats['total_images_processed']}")
    logger.info(f"Total people detected: {stats['total_people_detected']}")
    logger.info(f"Total banners detected: {stats['total_banners_detected']}")
    logger.info(f"Failed images: {stats['failed_images']}")
    logger.info(f"Average people per image: {stats['average_people_per_image']}")
    logger.info(f"Average banners per image: {stats['average_banners_per_image']}")
    logger.info(f"Average confidence (people): {stats['average_confidence_people']}")
    logger.info(f"Average confidence (banners): {stats['average_confidence_banners']}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
