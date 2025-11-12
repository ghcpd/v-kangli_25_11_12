"""
Example usage script demonstrating how to use the detection system programmatically
"""

from detector import DetectionPipeline
import json

def main():
    """Example usage of the detection pipeline"""
    
    # Initialize the pipeline with custom settings
    pipeline = DetectionPipeline(
        person_confidence=0.25,  # Lower threshold = more detections
        banner_confidence=0.5,   # OCR confidence threshold
        yolo_model='yolov8n.pt', # YOLO model (nano version)
        ocr_languages=['en']      # OCR languages
    )
    
    # Process a single image
    print("Processing single image...")
    result = pipeline.process_image('images/images_1.jpg')
    
    if result:
        print(f"\nImage: {result.image_id}")
        print(f"People detected: {len(result.detections['people'])}")
        print(f"Banners detected: {len(result.detections['banners'])}")
        
        # Print detection details
        for i, person in enumerate(result.detections['people'], 1):
            print(f"\nPerson {i}:")
            print(f"  Bounding box: ({person['x_min']}, {person['y_min']}) to ({person['x_max']}, {person['y_max']})")
            print(f"  Confidence: {person['confidence']}")
        
        for i, banner in enumerate(result.detections['banners'], 1):
            print(f"\nBanner {i}:")
            print(f"  Bounding box: ({banner['x_min']}, {banner['y_min']}) to ({banner['x_max']}, {banner['y_max']})")
            print(f"  Confidence: {banner['confidence']}")
            print(f"  Text: {banner['text']}")
    
    # Process entire folder
    print("\n\nProcessing folder...")
    results = pipeline.process_folder('images/')
    
    # Compute statistics
    stats = pipeline.compute_statistics()
    
    print("\n" + "="*50)
    print("STATISTICS")
    print("="*50)
    for key, value in stats.items():
        if key != 'failed_image_paths':  # Skip long paths list
            print(f"{key}: {value}")
    
    # Save results
    output_data = {
        "results": [
            {
                "image_id": r.image_id,
                "detections": r.detections
            }
            for r in results
        ]
    }
    
    with open('example_results.json', 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print("\nResults saved to example_results.json")
    
    # Create visualizations
    print("\nCreating visualizations...")
    for result in results:
        image_path = f"images/{result.image_id}"
        output_path = f"output_images/{result.image_id}"
        pipeline.visualize_detections(image_path, result, output_path)
    
    print("Done!")

if __name__ == "__main__":
    main()

