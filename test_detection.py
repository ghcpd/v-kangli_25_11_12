#!/usr/bin/env python3
"""
Automated Test Suite for Computer Vision Detection System
Tests detection accuracy, JSON format compliance, and persistence
"""

import unittest
import json
import os
import tempfile
import shutil
import numpy as np
import cv2
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Import the detection module
from detect import (
    PersonDetector, TextDetector, ImageProcessor, 
    Visualizer, DetectionBox, TextBanner
)


class TestDetectionFormat(unittest.TestCase):
    """Test detection output format compliance"""
    
    def test_detection_box_structure(self):
        """Test DetectionBox has required fields"""
        box = DetectionBox(x_min=10, y_min=20, x_max=100, y_max=150, confidence=0.95)
        box_dict = box.to_dict()
        
        required_fields = {'x_min', 'y_min', 'x_max', 'y_max', 'confidence'}
        self.assertTrue(required_fields.issubset(set(box_dict.keys())))
        self.assertEqual(box_dict['confidence'], 0.95)
        self.assertGreaterEqual(box_dict['confidence'], 0.0)
        self.assertLessEqual(box_dict['confidence'], 1.0)
    
    def test_text_banner_structure(self):
        """Test TextBanner has required fields"""
        banner = TextBanner(x_min=50, y_min=60, x_max=200, y_max=100, 
                           confidence=0.88, text="Hello World")
        banner_dict = banner.to_dict()
        
        required_fields = {'x_min', 'y_min', 'x_max', 'y_max', 'confidence', 'text'}
        self.assertTrue(required_fields.issubset(set(banner_dict.keys())))
        self.assertEqual(banner_dict['text'], "Hello World")
    
    def test_detection_json_structure(self):
        """Test detection result JSON structure"""
        result = {
            "image_id": "test.jpg",
            "detections": {
                "people": [
                    {"x_min": 10, "y_min": 20, "x_max": 100, "y_max": 150, "confidence": 0.95}
                ],
                "banners": [
                    {"x_min": 50, "y_min": 60, "x_max": 200, "y_max": 100, 
                     "confidence": 0.88, "text": "Test"}
                ]
            }
        }
        
        # Validate JSON structure
        self.assertIn("image_id", result)
        self.assertIn("detections", result)
        self.assertIn("people", result["detections"])
        self.assertIn("banners", result["detections"])
        
        # Validate people
        for person in result["detections"]["people"]:
            self.assertIn("x_min", person)
            self.assertIn("y_min", person)
            self.assertIn("x_max", person)
            self.assertIn("y_max", person)
            self.assertIn("confidence", person)
        
        # Validate banners
        for banner in result["detections"]["banners"]:
            self.assertIn("x_min", banner)
            self.assertIn("y_min", banner)
            self.assertIn("x_max", banner)
            self.assertIn("y_max", banner)
            self.assertIn("confidence", banner)
            self.assertIn("text", banner)


class TestStatistics(unittest.TestCase):
    """Test statistics calculation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = ImageProcessor()
        
        # Manually add test results
        self.processor.processed_images = [
            {
                "image_id": "test1.jpg",
                "person_count": 2,
                "banner_count": 1,
                "detections": {
                    "people": [
                        {"confidence": 0.95},
                        {"confidence": 0.87}
                    ],
                    "banners": [
                        {"confidence": 0.92}
                    ]
                }
            },
            {
                "image_id": "test2.jpg",
                "person_count": 1,
                "banner_count": 2,
                "detections": {
                    "people": [
                        {"confidence": 0.91}
                    ],
                    "banners": [
                        {"confidence": 0.88},
                        {"confidence": 0.85}
                    ]
                }
            }
        ]
    
    def test_statistics_generation(self):
        """Test statistics are generated correctly"""
        stats = self.processor.get_statistics()
        
        required_fields = {
            'total_images_processed',
            'total_people_detected',
            'total_banners_detected',
            'average_people_per_image',
            'average_banners_per_image',
            'average_confidence_people',
            'average_confidence_banners'
        }
        
        self.assertTrue(required_fields.issubset(set(stats.keys())))
    
    def test_statistics_accuracy(self):
        """Test statistics calculations are correct"""
        stats = self.processor.get_statistics()
        
        # Verify totals
        self.assertEqual(stats['total_images_processed'], 2)
        self.assertEqual(stats['total_people_detected'], 3)
        self.assertEqual(stats['total_banners_detected'], 3)
        
        # Verify averages
        self.assertAlmostEqual(stats['average_people_per_image'], 1.5, places=1)
        self.assertAlmostEqual(stats['average_banners_per_image'], 1.5, places=1)
        
        # Verify min/max
        self.assertEqual(stats['max_people_in_single_image'], 2)
        self.assertEqual(stats['min_people_in_single_image'], 1)


class TestImageProcessing(unittest.TestCase):
    """Test image processing functionality"""
    
    def setUp(self):
        """Create temporary test images"""
        self.test_dir = tempfile.mkdtemp()
        self.processor = ImageProcessor()
    
    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def create_test_image(self, filename: str, width: int = 640, height: int = 480):
        """Create a simple test image"""
        image = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        filepath = os.path.join(self.test_dir, filename)
        cv2.imwrite(filepath, image)
        return filepath
    
    def test_image_reading(self):
        """Test that images can be read"""
        test_image = self.create_test_image("test.jpg")
        image = cv2.imread(test_image)
        self.assertIsNotNone(image)
        self.assertEqual(image.shape[2], 3)  # BGR channels
    
    def test_folder_processing(self):
        """Test folder processing with multiple images"""
        # Create test images
        self.create_test_image("test1.jpg")
        self.create_test_image("test2.png")
        
        # Process folder
        results = self.processor.process_folder(self.test_dir)
        self.assertEqual(len(results), 2)
        
        # Verify results structure
        for result in results:
            self.assertIn("image_id", result)
            self.assertIn("detections", result)
            self.assertIn("person_count", result)
            self.assertIn("banner_count", result)
    
    def test_corrupt_image_handling(self):
        """Test handling of corrupt images"""
        # Create a corrupt image file
        corrupt_path = os.path.join(self.test_dir, "corrupt.jpg")
        with open(corrupt_path, 'w') as f:
            f.write("This is not an image")
        
        # Create a valid image too
        self.create_test_image("valid.jpg")
        
        # Process folder
        results = self.processor.process_folder(self.test_dir)
        
        # Should only process valid images
        self.assertEqual(len(results), 1)
        self.assertEqual(len(self.processor.failed_images), 1)


class TestVisualization(unittest.TestCase):
    """Test visualization functionality"""
    
    def setUp(self):
        """Set up test images"""
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        shutil.rmtree(self.output_dir, ignore_errors=True)
    
    def test_draw_detections(self):
        """Test annotation drawing"""
        # Create test image
        image = np.ones((480, 640, 3), dtype=np.uint8) * 255
        
        # Create test detections
        persons = [DetectionBox(50, 50, 150, 200, 0.95)]
        banners = [TextBanner(200, 300, 400, 350, 0.88, "Test Banner")]
        
        # Draw detections
        annotated = Visualizer.draw_detections(image, persons, banners)
        
        # Verify output
        self.assertEqual(annotated.shape, image.shape)
        # Check that image is different after annotation
        self.assertFalse(np.array_equal(annotated, image))


class TestConfidenceThresholds(unittest.TestCase):
    """Test confidence threshold filtering"""
    
    def test_person_confidence_threshold(self):
        """Test person detection respects confidence threshold"""
        detector = PersonDetector(confidence_threshold=0.5)
        self.assertEqual(detector.confidence_threshold, 0.5)
    
    def test_text_confidence_threshold(self):
        """Test text detection respects confidence threshold"""
        detector = TextDetector(confidence_threshold=0.2)
        self.assertEqual(detector.confidence_threshold, 0.2)
    
    def test_processor_confidence_thresholds(self):
        """Test processor respects both thresholds"""
        processor = ImageProcessor(person_confidence=0.4, text_confidence=0.3)
        self.assertEqual(processor.person_detector.confidence_threshold, 0.4)
        self.assertEqual(processor.text_detector.confidence_threshold, 0.3)


class TestJSONPersistence(unittest.TestCase):
    """Test JSON file operations"""
    
    def setUp(self):
        """Set up test directory"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_json_write_read(self):
        """Test writing and reading JSON files"""
        test_data = {
            "image_id": "test.jpg",
            "detections": {
                "people": [{"x_min": 10, "y_min": 20, "x_max": 100, "y_max": 150, "confidence": 0.95}],
                "banners": [{"x_min": 50, "y_min": 60, "x_max": 200, "y_max": 100, "confidence": 0.88, "text": "Test"}]
            }
        }
        
        filepath = os.path.join(self.test_dir, "test.json")
        
        # Write
        with open(filepath, 'w') as f:
            json.dump(test_data, f)
        
        # Read
        with open(filepath, 'r') as f:
            loaded_data = json.load(f)
        
        # Verify
        self.assertEqual(loaded_data['image_id'], test_data['image_id'])
        self.assertEqual(len(loaded_data['detections']['people']), 1)
        self.assertEqual(len(loaded_data['detections']['banners']), 1)
    
    def test_json_array_persistence(self):
        """Test writing array of results"""
        results = [
            {"image_id": f"test{i}.jpg", "detections": {"people": [], "banners": []}}
            for i in range(3)
        ]
        
        filepath = os.path.join(self.test_dir, "results.json")
        
        # Write
        with open(filepath, 'w') as f:
            json.dump(results, f)
        
        # Read
        with open(filepath, 'r') as f:
            loaded = json.load(f)
        
        self.assertEqual(len(loaded), 3)
        self.assertEqual(loaded[0]['image_id'], 'test0.jpg')


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def setUp(self):
        """Set up test environment"""
        self.processor = ImageProcessor()
    
    def test_empty_folder_processing(self):
        """Test processing empty folder"""
        with tempfile.TemporaryDirectory() as tmpdir:
            results = self.processor.process_folder(tmpdir)
            self.assertEqual(len(results), 0)
    
    def test_nonexistent_folder(self):
        """Test handling of nonexistent folder"""
        results = self.processor.process_folder("/nonexistent/path/to/folder")
        self.assertEqual(len(results), 0)
    
    def test_statistics_empty_processor(self):
        """Test statistics when no images processed"""
        empty_processor = ImageProcessor()
        stats = empty_processor.get_statistics()
        
        self.assertEqual(stats['total_images_processed'], 0)
        self.assertEqual(stats['total_people_detected'], 0)


class TestBoundingBoxValidity(unittest.TestCase):
    """Test bounding box validity"""
    
    def test_box_coordinates_order(self):
        """Test that x_min <= x_max and y_min <= y_max"""
        box = DetectionBox(10, 20, 100, 150, 0.95)
        
        self.assertLessEqual(box.x_min, box.x_max)
        self.assertLessEqual(box.y_min, box.y_max)
    
    def test_positive_coordinates(self):
        """Test that coordinates are non-negative"""
        box = DetectionBox(0, 0, 100, 150, 0.95)
        
        self.assertGreaterEqual(box.x_min, 0)
        self.assertGreaterEqual(box.y_min, 0)
        self.assertGreaterEqual(box.x_max, 0)
        self.assertGreaterEqual(box.y_max, 0)
    
    def test_confidence_range(self):
        """Test confidence is between 0 and 1"""
        for confidence in [0.0, 0.5, 0.95, 1.0]:
            box = DetectionBox(10, 20, 100, 150, confidence)
            self.assertGreaterEqual(box.confidence, 0.0)
            self.assertLessEqual(box.confidence, 1.0)


def run_test_suite():
    """Run all tests and generate report"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDetectionFormat))
    suite.addTests(loader.loadTestsFromTestCase(TestStatistics))
    suite.addTests(loader.loadTestsFromTestCase(TestImageProcessing))
    suite.addTests(loader.loadTestsFromTestCase(TestVisualization))
    suite.addTests(loader.loadTestsFromTestCase(TestConfidenceThresholds))
    suite.addTests(loader.loadTestsFromTestCase(TestJSONPersistence))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestBoundingBoxValidity))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    result = run_test_suite()
    exit(0 if result.wasSuccessful() else 1)
