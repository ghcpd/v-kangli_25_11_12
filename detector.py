"""
Computer Vision Detection System
Detects people and textual banners/signs in images with OCR
"""

import os
import json
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
import logging
from ultralytics import YOLO
import easyocr
from PIL import Image, ImageDraw, ImageFont
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class PersonDetection:
    """Person detection result"""
    x_min: int
    y_min: int
    x_max: int
    y_max: int
    confidence: float


@dataclass
class BannerDetection:
    """Banner/sign detection result with OCR text"""
    x_min: int
    y_min: int
    x_max: int
    y_max: int
    confidence: float
    text: str


@dataclass
class ImageDetectionResult:
    """Detection results for a single image"""
    image_id: str
    detections: Dict[str, List]


class PersonDetector:
    """Detects people in images using YOLO"""
    
    def __init__(self, model_path: str = 'yolov8n.pt', confidence_threshold: float = 0.25):
        """
        Initialize person detector
        
        Args:
            model_path: Path to YOLO model weights
            confidence_threshold: Minimum confidence for detections
        """
        self.confidence_threshold = confidence_threshold
        logger.info(f"Loading YOLO model from {model_path}")
        try:
            self.model = YOLO(model_path)
            logger.info("YOLO model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise
    
    def detect(self, image: np.ndarray) -> List[PersonDetection]:
        """
        Detect people in an image
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of PersonDetection objects
        """
        try:
            # YOLO class 0 is 'person'
            results = self.model(image, conf=self.confidence_threshold, classes=[0], verbose=False)
            
            detections = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0].cpu().numpy())
                    
                    detections.append(PersonDetection(
                        x_min=int(x1),
                        y_min=int(y1),
                        x_max=int(x2),
                        y_max=int(y2),
                        confidence=round(confidence, 3)
                    ))
            
            return detections
        except Exception as e:
            logger.error(f"Error detecting people: {e}")
            return []


class BannerDetector:
    """Detects textual banners and signs using OCR"""
    
    def __init__(self, confidence_threshold: float = 0.5, languages: List[str] = ['en']):
        """
        Initialize banner detector with OCR
        
        Args:
            confidence_threshold: Minimum confidence for text detections
            languages: List of language codes for OCR (e.g., ['en', 'ch_sim'])
        """
        self.confidence_threshold = confidence_threshold
        logger.info(f"Initializing EasyOCR reader for languages: {languages}")
        try:
            self.reader = easyocr.Reader(languages, gpu=False)
            logger.info("EasyOCR reader initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {e}")
            raise
    
    def detect(self, image: np.ndarray) -> List[BannerDetection]:
        """
        Detect textual banners/signs in an image
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of BannerDetection objects
        """
        try:
            # EasyOCR returns list of (bbox, text, confidence)
            results = self.reader.readtext(image)
            
            detections = []
            for (bbox, text, confidence) in results:
                if confidence >= self.confidence_threshold:
                    # bbox is list of 4 points: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                    # Convert to x_min, y_min, x_max, y_max
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]
                    
                    x_min = int(min(x_coords))
                    y_min = int(min(y_coords))
                    x_max = int(max(x_coords))
                    y_max = int(max(y_coords))
                    
                    # Clean up text
                    text = text.strip()
                    
                    detections.append(BannerDetection(
                        x_min=x_min,
                        y_min=y_min,
                        x_max=x_max,
                        y_max=y_max,
                        confidence=round(confidence, 3),
                        text=text
                    ))
            
            return detections
        except Exception as e:
            logger.error(f"Error detecting banners: {e}")
            return []


class DetectionPipeline:
    """Main pipeline for detecting people and banners"""
    
    def __init__(
        self,
        person_confidence: float = 0.25,
        banner_confidence: float = 0.5,
        yolo_model: str = 'yolov8n.pt',
        ocr_languages: List[str] = ['en']
    ):
        """
        Initialize detection pipeline
        
        Args:
            person_confidence: Confidence threshold for person detection
            banner_confidence: Confidence threshold for banner detection
            yolo_model: Path to YOLO model
            ocr_languages: Languages for OCR
        """
        self.person_detector = PersonDetector(yolo_model, person_confidence)
        self.banner_detector = BannerDetector(banner_confidence, ocr_languages)
        self.processed_images = []
        self.failed_images = []
    
    def process_image(self, image_path: str) -> Optional[ImageDetectionResult]:
        """
        Process a single image
        
        Args:
            image_path: Path to image file
            
        Returns:
            ImageDetectionResult or None if processing failed
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                logger.warning(f"Could not read image: {image_path}")
                self.failed_images.append(image_path)
                return None
            
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect people
            people = self.person_detector.detect(image_rgb)
            
            # Detect banners
            banners = self.banner_detector.detect(image_rgb)
            
            # Create result
            image_id = os.path.basename(image_path)
            result = ImageDetectionResult(
                image_id=image_id,
                detections={
                    "people": [asdict(p) for p in people],
                    "banners": [asdict(b) for b in banners]
                }
            )
            
            self.processed_images.append(result)
            logger.info(f"Processed {image_id}: {len(people)} people, {len(banners)} banners")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing {image_path}: {e}")
            self.failed_images.append(image_path)
            return None
    
    def process_folder(self, folder_path: str) -> List[ImageDetectionResult]:
        """
        Process all images in a folder
        
        Args:
            folder_path: Path to folder containing images
            
        Returns:
            List of ImageDetectionResult objects
        """
        folder = Path(folder_path)
        image_extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
        
        image_files = [
            str(f) for f in folder.iterdir()
            if f.suffix in image_extensions
        ]
        
        logger.info(f"Found {len(image_files)} images in {folder_path}")
        
        results = []
        for image_path in image_files:
            result = self.process_image(image_path)
            if result:
                results.append(result)
        
        return results
    
    def compute_statistics(self) -> Dict:
        """
        Compute detection statistics
        
        Returns:
            Dictionary with statistics
        """
        if not self.processed_images:
            return {
                "total_images_processed": 0,
                "total_people_detected": 0,
                "total_banners_detected": 0,
                "average_people_per_image": 0.0,
                "average_banners_per_image": 0.0,
                "average_confidence_people": 0.0,
                "average_confidence_banners": 0.0,
                "max_people_in_image": 0,
                "min_people_in_image": 0,
                "max_banners_in_image": 0,
                "min_banners_in_image": 0,
                "failed_images": len(self.failed_images)
            }
        
        total_people = sum(len(img.detections["people"]) for img in self.processed_images)
        total_banners = sum(len(img.detections["banners"]) for img in self.processed_images)
        
        # Confidence scores
        all_people_confidences = []
        all_banner_confidences = []
        
        for img in self.processed_images:
            for person in img.detections["people"]:
                all_people_confidences.append(person["confidence"])
            for banner in img.detections["banners"]:
                all_banner_confidences.append(banner["confidence"])
        
        people_per_image = [len(img.detections["people"]) for img in self.processed_images]
        banners_per_image = [len(img.detections["banners"]) for img in self.processed_images]
        
        stats = {
            "total_images_processed": len(self.processed_images),
            "total_people_detected": total_people,
            "total_banners_detected": total_banners,
            "average_people_per_image": round(total_people / len(self.processed_images), 2) if self.processed_images else 0.0,
            "average_banners_per_image": round(total_banners / len(self.processed_images), 2) if self.processed_images else 0.0,
            "average_confidence_people": round(np.mean(all_people_confidences), 3) if all_people_confidences else 0.0,
            "average_confidence_banners": round(np.mean(all_banner_confidences), 3) if all_banner_confidences else 0.0,
            "max_people_in_image": max(people_per_image) if people_per_image else 0,
            "min_people_in_image": min(people_per_image) if people_per_image else 0,
            "max_banners_in_image": max(banners_per_image) if banners_per_image else 0,
            "min_banners_in_image": min(banners_per_image) if banners_per_image else 0,
            "failed_images": len(self.failed_images),
            "failed_image_paths": self.failed_images
        }
        
        return stats
    
    def visualize_detections(self, image_path: str, result: ImageDetectionResult, output_path: str):
        """
        Create annotated visualization of detections
        
        Args:
            image_path: Path to original image
            result: Detection result for the image
            output_path: Path to save annotated image
        """
        try:
            # Load image
            image = Image.open(image_path).convert('RGB')
            draw = ImageDraw.Draw(image)
            
            # Try to load a font with better size, fallback to default if not available
            font_size = max(16, min(image.width, image.height) // 40)  # Adaptive font size
            try:
                # Try Windows fonts
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
                except:
                    try:
                        # Try Linux fonts
                        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
                    except:
                        try:
                            # Try macOS fonts
                            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
                        except:
                            font = ImageFont.load_default()
            
            # Colors (RGB format for PIL)
            person_color = (0, 255, 0)  # Green
            banner_color = (255, 0, 0)   # Red
            text_bg_color = (0, 0, 0)     # Black background
            
            # Draw person bounding boxes (green)
            for idx, person in enumerate(result.detections["people"], 1):
                x_min = person["x_min"]
                y_min = person["y_min"]
                x_max = person["x_max"]
                y_max = person["y_max"]
                conf = person["confidence"]
                
                # Draw bounding box
                draw.rectangle([x_min, y_min, x_max, y_max], outline=person_color, width=3)
                
                # Prepare label
                label = f"Person #{idx} ({conf:.2f})"
                
                # Get text size for background box
                try:
                    bbox = draw.textbbox((0, 0), label, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                except:
                    # Fallback for older PIL versions
                    text_width = len(label) * 8
                    text_height = 16
                
                # Draw text background for better visibility
                label_y = max(0, y_min - text_height - 5)
                draw.rectangle(
                    [x_min, label_y, x_min + text_width + 4, label_y + text_height + 2],
                    fill=text_bg_color
                )
                draw.text((x_min + 2, label_y + 1), label, fill=person_color, font=font)
            
            # Draw banner bounding boxes (red) with text
            for idx, banner in enumerate(result.detections["banners"], 1):
                x_min = banner["x_min"]
                y_min = banner["y_min"]
                x_max = banner["x_max"]
                y_max = banner["y_max"]
                conf = banner["confidence"]
                text = banner["text"]
                
                # Draw bounding box
                draw.rectangle([x_min, y_min, x_max, y_max], outline=banner_color, width=3)
                
                # Prepare label with detected text
                display_text = text[:50] + "..." if len(text) > 50 else text
                label = f"Banner #{idx} ({conf:.2f}): {display_text}"
                
                # Get text size
                try:
                    bbox = draw.textbbox((0, 0), label, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                except:
                    text_width = len(label) * 8
                    text_height = 16
                
                # Draw text below the box with background
                label_y = min(image.height - text_height - 5, y_max + 5)
                draw.rectangle(
                    [x_min, label_y, min(x_min + text_width + 4, image.width), label_y + text_height + 2],
                    fill=text_bg_color
                )
                draw.text((x_min + 2, label_y + 1), label, fill=banner_color, font=font)
            
            # Add summary legend in top-left corner
            summary_lines = [
                f"Image: {result.image_id}",
                f"People: {len(result.detections['people'])}",
                f"Banners: {len(result.detections['banners'])}"
            ]
            
            legend_y = 10
            for line in summary_lines:
                try:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                except:
                    text_width = len(line) * 8
                    text_height = 16
                
                # Background for legend
                draw.rectangle(
                    [10, legend_y, 10 + text_width + 4, legend_y + text_height + 2],
                    fill=text_bg_color
                )
                draw.text((12, legend_y + 1), line, fill=(255, 255, 255), font=font)
                legend_y += text_height + 5
            
            # Save annotated image
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            image.save(output_path, quality=95)
            logger.info(f"Saved annotated image to {output_path}")
            
        except Exception as e:
            logger.error(f"Error visualizing {image_path}: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Detect people and banners in images')
    parser.add_argument('--input', type=str, default='images/', help='Input folder with images')
    parser.add_argument('--output', type=str, default='output_images/', help='Output folder for annotated images')
    parser.add_argument('--results', type=str, default='results.json', help='Output JSON file for results')
    parser.add_argument('--stats', type=str, default='statistics.json', help='Output JSON file for statistics')
    parser.add_argument('--person-conf', type=float, default=0.25, help='Person detection confidence threshold')
    parser.add_argument('--banner-conf', type=float, default=0.5, help='Banner detection confidence threshold')
    parser.add_argument('--yolo-model', type=str, default='yolov8n.pt', help='YOLO model path')
    parser.add_argument('--languages', type=str, nargs='+', default=['en'], help='OCR languages')
    parser.add_argument('--no-visualize', action='store_true', help='Skip visualization')
    
    args = parser.parse_args()
    
    # Initialize pipeline
    logger.info("Initializing detection pipeline...")
    pipeline = DetectionPipeline(
        person_confidence=args.person_conf,
        banner_confidence=args.banner_conf,
        yolo_model=args.yolo_model,
        ocr_languages=args.languages
    )
    
    # Process images
    logger.info(f"Processing images from {args.input}...")
    results = pipeline.process_folder(args.input)
    
    # Prepare output data
    output_data = {
        "results": [asdict(r) for r in results]
    }
    
    # Save results JSON
    with open(args.results, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved results to {args.results}")
    
    # Compute and save statistics
    stats = pipeline.compute_statistics()
    with open(args.stats, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved statistics to {args.stats}")
    
    # Print statistics
    print("\n" + "="*50)
    print("DETECTION STATISTICS")
    print("="*50)
    print(f"Total images processed: {stats['total_images_processed']}")
    print(f"Total people detected: {stats['total_people_detected']}")
    print(f"Total banners detected: {stats['total_banners_detected']}")
    print(f"Average people per image: {stats['average_people_per_image']}")
    print(f"Average banners per image: {stats['average_banners_per_image']}")
    print(f"Average confidence (people): {stats['average_confidence_people']}")
    print(f"Average confidence (banners): {stats['average_confidence_banners']}")
    print(f"Max people in single image: {stats['max_people_in_image']}")
    print(f"Min people in single image: {stats['min_people_in_image']}")
    print(f"Max banners in single image: {stats['max_banners_in_image']}")
    print(f"Min banners in single image: {stats['min_banners_in_image']}")
    print(f"Failed images: {stats['failed_images']}")
    print("="*50 + "\n")
    
    # Visualize detections
    if not args.no_visualize:
        logger.info(f"Creating visualizations in {args.output}...")
        for result in results:
            image_path = os.path.join(args.input, result.image_id)
            output_path = os.path.join(args.output, result.image_id)
            pipeline.visualize_detections(image_path, result, output_path)
    
    logger.info("Processing complete!")


if __name__ == "__main__":
    main()

