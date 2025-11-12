#!/usr/bin/env python3
"""
Example usage of the Computer Vision Detection System
Demonstrates various use cases and configurations
"""

import json
from pathlib import Path
from detect import ImageProcessor, Visualizer
from config import Config, PresetConfig


def example_1_basic_detection():
    """Example 1: Basic detection with default settings"""
    print("\n" + "=" * 60)
    print("Example 1: Basic Detection")
    print("=" * 60)
    
    # Create processor with default settings
    processor = ImageProcessor()
    
    # Process all images in the folder
    print("Processing images...")
    results = processor.process_folder("images/")
    
    # Print results
    print(f"\nProcessed {len(results)} images")
    for result in results:
        people = len(result["detections"]["people"])
        banners = len(result["detections"]["banners"])
        print(f"  {result['image_id']}: {people} people, {banners} banners")
    
    # Get statistics
    stats = processor.get_statistics()
    print(f"\nStatistics:")
    print(f"  Total people: {stats['total_people_detected']}")
    print(f"  Total banners: {stats['total_banners_detected']}")
    print(f"  Average confidence (people): {stats['average_confidence_people']:.2%}")


def example_2_custom_thresholds():
    """Example 2: Detection with custom confidence thresholds"""
    print("\n" + "=" * 60)
    print("Example 2: Custom Confidence Thresholds")
    print("=" * 60)
    
    # Create processor with custom thresholds
    processor = ImageProcessor(
        person_confidence=0.5,  # Higher threshold = fewer false positives
        text_confidence=0.2
    )
    
    print(f"Person confidence threshold: {processor.person_detector.confidence_threshold}")
    print(f"Text confidence threshold: {processor.text_detector.confidence_threshold}")
    
    # Process a single image
    image_path = "images/images_1.jpg"
    print(f"\nProcessing single image: {image_path}")
    result = processor.process_image(image_path)
    
    if result:
        print(f"Found {result['person_count']} people and {result['banner_count']} banners")


def example_3_preset_configurations():
    """Example 3: Using preset configurations"""
    print("\n" + "=" * 60)
    print("Example 3: Preset Configurations")
    print("=" * 60)
    
    presets = ["balanced", "high_accuracy", "high_speed", "gpu_enabled"]
    
    for preset_name in presets:
        print(f"\n{preset_name.upper()} Preset:")
        preset_config = getattr(PresetConfig, preset_name)()
        for key, value in preset_config.items():
            print(f"  {key}: {value}")


def example_4_export_results():
    """Example 4: Export results in various formats"""
    print("\n" + "=" * 60)
    print("Example 4: Export Results")
    print("=" * 60)
    
    processor = ImageProcessor()
    results = processor.process_folder("images/")
    stats = processor.get_statistics()
    
    # Save results to JSON
    with open("results/detections.json", 'w') as f:
        json.dump(results, f, indent=2)
    print("Saved detections to: results/detections.json")
    
    # Save statistics
    with open("results/statistics.json", 'w') as f:
        json.dump(stats, f, indent=2)
    print("Saved statistics to: results/statistics.json")
    
    # Show summary
    print("\nDetection Summary:")
    print(f"  Images: {stats['total_images_processed']}")
    print(f"  People: {stats['total_people_detected']}")
    print(f"  Banners: {stats['total_banners_detected']}")
    print(f"  Success rate: {(1 - stats['failed_images']/stats['total_images_processed'])*100:.1f}%")


def example_5_visualization():
    """Example 5: Create annotated images"""
    print("\n" + "=" * 60)
    print("Example 5: Visualization")
    print("=" * 60)
    
    processor = ImageProcessor()
    results = processor.process_folder("images/")
    
    print("Creating annotated images...")
    Visualizer.save_annotated_images(results, "output_images/")
    print(f"Saved {len(results)} annotated images to: output_images/")


def example_6_batch_processing():
    """Example 6: Process multiple image folders"""
    print("\n" + "=" * 60)
    print("Example 6: Batch Processing Multiple Folders")
    print("=" * 60)
    
    folders = ["images/"]  # Add more folders as needed
    all_results = []
    
    for folder in folders:
        if Path(folder).exists():
            print(f"\nProcessing folder: {folder}")
            processor = ImageProcessor()
            results = processor.process_folder(folder)
            all_results.extend(results)
            
            stats = processor.get_statistics()
            print(f"  ✓ {len(results)} images processed")
            print(f"  ✓ {stats['total_people_detected']} people detected")
            print(f"  ✓ {stats['total_banners_detected']} banners detected")
    
    # Save combined results
    with open("results/combined_detections.json", 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\nTotal results: {len(all_results)} images")


def example_7_error_handling():
    """Example 7: Error handling and logging"""
    print("\n" + "=" * 60)
    print("Example 7: Error Handling")
    print("=" * 60)
    
    processor = ImageProcessor()
    
    # Try to process non-existent folder
    print("\nProcessing non-existent folder...")
    results = processor.process_folder("/nonexistent/path/")
    print(f"Results: {len(results)} images (expected 0)")
    
    # Try to process file instead of folder
    print("\nProcessing single file...")
    result = processor.process_image("images/images_1.jpg")
    if result:
        print(f"✓ File processed successfully")
        print(f"  People: {result['person_count']}")
        print(f"  Banners: {result['banner_count']}")
    
    # Check failed images
    if processor.failed_images:
        print(f"\nFailed images: {len(processor.failed_images)}")
        for failed in processor.failed_images:
            print(f"  - {failed['image_path']}: {failed['error']}")


def example_8_configuration_management():
    """Example 8: Configuration management"""
    print("\n" + "=" * 60)
    print("Example 8: Configuration Management")
    print("=" * 60)
    
    # Show current configuration
    print("\nCurrent Configuration:")
    config_dict = Config.get_all()
    for key in sorted(config_dict.keys()):
        if not key.startswith('_'):
            print(f"  {key}: {config_dict[key]}")
    
    # Save configuration
    print("\nSaving configuration...")
    Config.save_to_file("config_backup.json")
    print("✓ Configuration saved to: config_backup.json")
    
    # Validate configuration
    print("\nValidating configuration...")
    if Config.validate():
        print("✓ Configuration is valid")
    else:
        print("✗ Configuration has errors")


def example_9_performance_analysis():
    """Example 9: Performance analysis"""
    print("\n" + "=" * 60)
    print("Example 9: Performance Analysis")
    print("=" * 60)
    
    import time
    
    processor = ImageProcessor()
    
    print("Running performance analysis...")
    start_time = time.time()
    results = processor.process_folder("images/")
    elapsed_time = time.time() - start_time
    
    stats = processor.get_statistics()
    
    print(f"\nPerformance Metrics:")
    print(f"  Total images: {len(results)}")
    print(f"  Total time: {elapsed_time:.2f}s")
    if len(results) > 0:
        print(f"  Time per image: {elapsed_time/len(results):.2f}s")
        print(f"  Images per second: {len(results)/elapsed_time:.2f}")
    
    print(f"\nDetection Statistics:")
    print(f"  People detected: {stats['total_people_detected']}")
    print(f"  Banners detected: {stats['total_banners_detected']}")
    print(f"  Avg people per image: {stats['average_people_per_image']}")
    print(f"  Avg banners per image: {stats['average_banners_per_image']}")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("COMPUTER VISION DETECTION SYSTEM - EXAMPLES")
    print("=" * 60)
    
    try:
        # Run examples
        example_1_basic_detection()
        example_2_custom_thresholds()
        example_3_preset_configurations()
        example_4_export_results()
        example_5_visualization()
        example_6_batch_processing()
        example_7_error_handling()
        example_8_configuration_management()
        example_9_performance_analysis()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
