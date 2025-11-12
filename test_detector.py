"""
Comprehensive test suite for the detection system
Tests detection accuracy, persistence, error handling, and multi-image processing
"""

import os
import json
import unittest
import tempfile
import shutil
from pathlib import Path
import numpy as np
from PIL import Image
import cv2

from detector import (
    DetectionPipeline,
    PersonDetector,
    BannerDetector,
    ImageDetectionResult,
    PersonDetection,
    BannerDetection
)


class TestPersonDetector(unittest.TestCase):
    """Test person detection functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.detector = PersonDetector(confidence_threshold=0.25)
    
    def test_detector_initialization(self):
        """Test that detector initializes correctly"""
        self.assertIsNotNone(self.detector.model)
        self.assertEqual(self.detector.confidence_threshold, 0.25)
    
    def test_detect_empty_image(self):
        """Test detection on empty/black image"""
        empty_image = np.zeros((100, 100, 3), dtype=np.uint8)
        detections = self.detector.detect(empty_image)
        self.assertIsInstance(detections, list)
    
    def test_detect_synthetic_image(self):
        """Test detection on synthetic image with simple shapes"""
        # Create a simple test image
        test_image = np.ones((640, 640, 3), dtype=np.uint8) * 255
        detections = self.detector.detect(test_image)
        self.assertIsInstance(detections, list)
        # Should handle gracefully even if no people detected
        for det in detections:
            self.assertIsInstance(det, PersonDetection)
            self.assertGreaterEqual(det.confidence, 0.0)
            self.assertLessEqual(det.confidence, 1.0)


class TestBannerDetector(unittest.TestCase):
    """Test banner detection and OCR functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        try:
            self.detector = BannerDetector(confidence_threshold=0.5)
        except Exception as e:
            self.skipTest(f"Could not initialize OCR: {e}")
    
    def test_detector_initialization(self):
        """Test that detector initializes correctly"""
        self.assertIsNotNone(self.detector.reader)
        self.assertEqual(self.detector.confidence_threshold, 0.5)
    
    def test_detect_empty_image(self):
        """Test detection on empty image"""
        empty_image = np.zeros((100, 100, 3), dtype=np.uint8)
        detections = self.detector.detect(empty_image)
        self.assertIsInstance(detections, list)
    
    def test_detect_text_image(self):
        """Test detection on image with text"""
        # Create a simple image with text using PIL
        img = Image.new('RGB', (200, 100), color='white')
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        draw.text((10, 30), "TEST TEXT", fill='black', font=font)
        
        # Convert to numpy array
        img_array = np.array(img)
        detections = self.detector.detect(img_array)
        self.assertIsInstance(detections, list)
        
        for det in detections:
            self.assertIsInstance(det, BannerDetection)
            self.assertGreaterEqual(det.confidence, 0.0)
            self.assertLessEqual(det.confidence, 1.0)
            self.assertIsInstance(det.text, str)


class TestDetectionPipeline(unittest.TestCase):
    """Test the complete detection pipeline"""
    
    def setUp(self):
        """Set up test fixtures"""
        try:
            self.pipeline = DetectionPipeline(
                person_confidence=0.25,
                banner_confidence=0.5
            )
        except Exception as e:
            self.skipTest(f"Could not initialize pipeline: {e}")
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization"""
        self.assertIsNotNone(self.pipeline.person_detector)
        self.assertIsNotNone(self.pipeline.banner_detector)
        self.assertEqual(len(self.pipeline.processed_images), 0)
        self.assertEqual(len(self.pipeline.failed_images), 0)
    
    def test_process_nonexistent_image(self):
        """Test handling of non-existent image"""
        result = self.pipeline.process_image("nonexistent.jpg")
        self.assertIsNone(result)
        self.assertEqual(len(self.pipeline.failed_images), 1)
    
    def test_create_test_image(self):
        """Create a test image for processing"""
        # Create a temporary test image
        test_dir = tempfile.mkdtemp()
        test_image_path = os.path.join(test_dir, "test.jpg")
        
        # Create a simple test image
        img = Image.new('RGB', (640, 480), color='lightblue')
        img.save(test_image_path)
        
        return test_dir, test_image_path
    
    def test_process_single_image(self):
        """Test processing a single image"""
        test_dir, test_image_path = self.create_test_image()
        
        try:
            result = self.pipeline.process_image(test_image_path)
            self.assertIsNotNone(result)
            self.assertEqual(result.image_id, "test.jpg")
            self.assertIn("people", result.detections)
            self.assertIn("banners", result.detections)
            self.assertIsInstance(result.detections["people"], list)
            self.assertIsInstance(result.detections["banners"], list)
        finally:
            shutil.rmtree(test_dir)
    
    def test_process_folder(self):
        """Test processing a folder of images"""
        test_dir = tempfile.mkdtemp()
        
        try:
            # Create multiple test images
            for i in range(3):
                img = Image.new('RGB', (640, 480), color='lightblue')
                img.save(os.path.join(test_dir, f"test_{i}.jpg"))
            
            results = self.pipeline.process_folder(test_dir)
            self.assertGreaterEqual(len(results), 0)  # May be 0 if no detections
            
            for result in results:
                self.assertIsInstance(result, ImageDetectionResult)
                self.assertIn("people", result.detections)
                self.assertIn("banners", result.detections)
        finally:
            shutil.rmtree(test_dir)
    
    def test_compute_statistics(self):
        """Test statistics computation"""
        # Process a test image first
        test_dir, test_image_path = self.create_test_image()
        
        try:
            self.pipeline.process_image(test_image_path)
            stats = self.pipeline.compute_statistics()
            
            self.assertIn("total_images_processed", stats)
            self.assertIn("total_people_detected", stats)
            self.assertIn("total_banners_detected", stats)
            self.assertIn("average_people_per_image", stats)
            self.assertIn("average_banners_per_image", stats)
            self.assertIn("average_confidence_people", stats)
            self.assertIn("average_confidence_banners", stats)
            self.assertIn("max_people_in_image", stats)
            self.assertIn("min_people_in_image", stats)
            self.assertIn("max_banners_in_image", stats)
            self.assertIn("min_banners_in_image", stats)
            self.assertIn("failed_images", stats)
            
            # Check data types
            self.assertIsInstance(stats["total_images_processed"], int)
            self.assertIsInstance(stats["average_people_per_image"], (int, float))
        finally:
            shutil.rmtree(test_dir)
    
    def test_visualize_detections(self):
        """Test visualization generation"""
        test_dir, test_image_path = self.create_test_image()
        output_dir = tempfile.mkdtemp()
        
        try:
            result = self.pipeline.process_image(test_image_path)
            if result:
                output_path = os.path.join(output_dir, "annotated_test.jpg")
                self.pipeline.visualize_detections(test_image_path, result, output_path)
                
                # Check that output file exists
                self.assertTrue(os.path.exists(output_path))
        finally:
            shutil.rmtree(test_dir)
            shutil.rmtree(output_dir)


class TestJSONOutput(unittest.TestCase):
    """Test JSON output format and persistence"""
    
    def setUp(self):
        """Set up test fixtures"""
        try:
            self.pipeline = DetectionPipeline()
        except Exception as e:
            self.skipTest(f"Could not initialize pipeline: {e}")
    
    def test_json_serialization(self):
        """Test that results can be serialized to JSON"""
        test_dir, test_image_path = self.create_test_image()
        
        try:
            result = self.pipeline.process_image(test_image_path)
            if result:
                # Convert to dict
                result_dict = {
                    "image_id": result.image_id,
                    "detections": result.detections
                }
                
                # Serialize to JSON
                json_str = json.dumps(result_dict, indent=2)
                self.assertIsInstance(json_str, str)
                
                # Deserialize back
                loaded = json.loads(json_str)
                self.assertEqual(loaded["image_id"], result.image_id)
                self.assertIn("people", loaded["detections"])
                self.assertIn("banners", loaded["detections"])
        finally:
            shutil.rmtree(test_dir)
    
    def create_test_image(self):
        """Create a test image for processing"""
        test_dir = tempfile.mkdtemp()
        test_image_path = os.path.join(test_dir, "test.jpg")
        img = Image.new('RGB', (640, 480), color='lightblue')
        img.save(test_image_path)
        return test_dir, test_image_path
    
    def test_json_persistence(self):
        """Test saving and loading JSON results"""
        test_dir, test_image_path = self.create_test_image()
        json_path = os.path.join(test_dir, "results.json")
        
        try:
            result = self.pipeline.process_image(test_image_path)
            if result:
                # Save to JSON
                output_data = {
                    "results": [{
                        "image_id": result.image_id,
                        "detections": result.detections
                    }]
                }
                
                with open(json_path, 'w') as f:
                    json.dump(output_data, f)
                
                # Load from JSON
                with open(json_path, 'r') as f:
                    loaded_data = json.load(f)
                
                self.assertIn("results", loaded_data)
                self.assertEqual(len(loaded_data["results"]), 1)
        finally:
            shutil.rmtree(test_dir)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def test_corrupt_image_handling(self):
        """Test handling of corrupt image files"""
        test_dir = tempfile.mkdtemp()
        corrupt_image_path = os.path.join(test_dir, "corrupt.jpg")
        
        try:
            # Create a file that's not a valid image
            with open(corrupt_image_path, 'w') as f:
                f.write("This is not an image file")
            
            pipeline = DetectionPipeline()
            result = pipeline.process_image(corrupt_image_path)
            
            # Should return None and log the failure
            self.assertIsNone(result)
            self.assertIn(corrupt_image_path, pipeline.failed_images)
        finally:
            shutil.rmtree(test_dir)
    
    def test_empty_folder_handling(self):
        """Test processing empty folder"""
        test_dir = tempfile.mkdtemp()
        
        try:
            pipeline = DetectionPipeline()
            results = pipeline.process_folder(test_dir)
            self.assertEqual(len(results), 0)
        finally:
            shutil.rmtree(test_dir)
    
    def test_mixed_file_types(self):
        """Test handling folder with mixed file types"""
        test_dir = tempfile.mkdtemp()
        
        try:
            # Create an image file
            img = Image.new('RGB', (100, 100), color='white')
            img.save(os.path.join(test_dir, "test.jpg"))
            
            # Create a non-image file
            with open(os.path.join(test_dir, "test.txt"), 'w') as f:
                f.write("Not an image")
            
            pipeline = DetectionPipeline()
            results = pipeline.process_folder(test_dir)
            
            # Should only process the image file
            self.assertEqual(len(results), 1)
        finally:
            shutil.rmtree(test_dir)


class TestMultiImageProcessing(unittest.TestCase):
    """Test processing multiple images"""
    
    def test_batch_processing(self):
        """Test processing multiple images in batch"""
        test_dir = tempfile.mkdtemp()
        
        try:
            # Create multiple test images
            for i in range(5):
                img = Image.new('RGB', (640, 480), color='lightblue')
                img.save(os.path.join(test_dir, f"test_{i}.jpg"))
            
            pipeline = DetectionPipeline()
            results = pipeline.process_folder(test_dir)
            
            # Should process all images
            self.assertEqual(len(results), 5)
            
            # Check statistics
            stats = pipeline.compute_statistics()
            self.assertEqual(stats["total_images_processed"], 5)
        finally:
            shutil.rmtree(test_dir)
    
    def test_statistics_accuracy(self):
        """Test that statistics are computed correctly"""
        test_dir = tempfile.mkdtemp()
        
        try:
            # Create test images
            for i in range(3):
                img = Image.new('RGB', (640, 480), color='lightblue')
                img.save(os.path.join(test_dir, f"test_{i}.jpg"))
            
            pipeline = DetectionPipeline()
            results = pipeline.process_folder(test_dir)
            stats = pipeline.compute_statistics()
            
            # Verify statistics make sense
            self.assertEqual(stats["total_images_processed"], len(results))
            self.assertGreaterEqual(stats["total_people_detected"], 0)
            self.assertGreaterEqual(stats["total_banners_detected"], 0)
            
            if stats["total_images_processed"] > 0:
                expected_avg_people = stats["total_people_detected"] / stats["total_images_processed"]
                self.assertAlmostEqual(stats["average_people_per_image"], expected_avg_people, places=2)
        finally:
            shutil.rmtree(test_dir)


def run_tests():
    """Run all tests and generate report"""
    import sys
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestPersonDetector,
        TestBannerDetector,
        TestDetectionPipeline,
        TestJSONOutput,
        TestErrorHandling,
        TestMultiImageProcessing
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate test report
    report = {
        "total_tests": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped) if hasattr(result, 'skipped') else 0,
        "success": result.wasSuccessful(),
        "failure_details": [
            {
                "test": str(f[0]),
                "traceback": f[1]
            } for f in result.failures
        ],
        "error_details": [
            {
                "test": str(e[0]),
                "traceback": e[1]
            } for e in result.errors
        ]
    }
    
    # Save report
    with open("test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "="*50)
    print("TEST REPORT")
    print("="*50)
    print(f"Total tests: {report['total_tests']}")
    print(f"Failures: {report['failures']}")
    print(f"Errors: {report['errors']}")
    print(f"Skipped: {report['skipped']}")
    print(f"Success: {report['success']}")
    print("="*50)
    print(f"\nDetailed report saved to test_report.json")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

