#!/usr/bin/env python3
"""
Simple Image Analysis Script
Uses basic computer vision to analyze images without heavy dependencies
"""

import json
import os
from pathlib import Path
from datetime import datetime
import base64

def get_image_info(image_path):
    """Get basic image information"""
    try:
        file_size = os.path.getsize(image_path)
        file_path = Path(image_path)
        
        return {
            "filename": file_path.name,
            "path": str(image_path),
            "size_bytes": file_size,
            "size_mb": round(file_size / (1024 * 1024), 2),
            "format": file_path.suffix.upper()[1:],
            "exists": True,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "filename": Path(image_path).name,
            "error": str(e),
            "exists": False
        }

def analyze_images(folder_path):
    """Analyze all images in a folder"""
    
    results = {
        "analysis_timestamp": datetime.now().isoformat(),
        "folder_path": folder_path,
        "images": []
    }
    
    # Find all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'}
    
    if not os.path.exists(folder_path):
        results["error"] = f"Folder not found: {folder_path}"
        return results
    
    image_files = [f for f in os.listdir(folder_path) 
                   if Path(f).suffix.lower() in image_extensions]
    
    results["total_images_found"] = len(image_files)
    
    for image_file in sorted(image_files):
        image_path = os.path.join(folder_path, image_file)
        info = get_image_info(image_path)
        results["images"].append(info)
    
    return results

def generate_summary(results):
    """Generate a summary report"""
    
    summary = {
        "timestamp": results["analysis_timestamp"],
        "folder": results["folder_path"],
        "total_images": results.get("total_images_found", 0),
        "total_size_mb": round(sum(img.get("size_mb", 0) for img in results["images"]), 2),
        "formats": {},
        "image_details": []
    }
    
    # Count formats
    for img in results["images"]:
        fmt = img.get("format", "UNKNOWN")
        summary["formats"][fmt] = summary["formats"].get(fmt, 0) + 1
        summary["image_details"].append({
            "filename": img.get("filename"),
            "size_mb": img.get("size_mb", 0),
            "format": fmt
        })
    
    return summary

# Main execution
if __name__ == "__main__":
    images_folder = "images"
    
    print("=" * 70)
    print("IMAGE ANALYSIS REPORT")
    print("=" * 70)
    print()
    
    results = analyze_images(images_folder)
    
    if "error" in results:
        print(f"Error: {results['error']}")
    else:
        print(f"Folder: {results['folder_path']}")
        print(f"Total Images Found: {results['total_images_found']}")
        print(f"Analysis Time: {results['analysis_timestamp']}")
        print()
        print("-" * 70)
        print("IMAGE DETAILS:")
        print("-" * 70)
        
        for img in results["images"]:
            print(f"\nFile: {img.get('filename', 'Unknown')}")
            print(f"  Format: {img.get('format', 'UNKNOWN')}")
            print(f"  Size: {img.get('size_mb', 0)} MB ({img.get('size_bytes', 0)} bytes)")
        
        # Generate summary
        summary = generate_summary(results)
        
        print("\n" + "=" * 70)
        print("SUMMARY STATISTICS:")
        print("=" * 70)
        print(f"Total Images: {summary['total_images']}")
        print(f"Total Size: {summary['total_size_mb']} MB")
        print(f"Formats: {summary['formats']}")
        
        # Save results to JSON
        with open("results/image_analysis.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        with open("results/analysis_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        print("\n✓ Analysis saved to: results/image_analysis.json")
        print("✓ Summary saved to: results/analysis_summary.json")
    
    print("\n" + "=" * 70)
