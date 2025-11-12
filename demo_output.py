"""
演示脚本 - 展示分析结果的预期输出格式
此脚本不需要安装依赖，仅用于展示输出格式
"""

import json
import os
from datetime import datetime

def create_demo_output():
    """创建演示输出，展示分析结果的格式"""
    
    # 基于images文件夹中的图片创建示例结果
    demo_results = {
        "results": [
            {
                "image_id": "images_1.jpg",
                "detections": {
                    "people": [
                        {
                            "x_min": 150,
                            "y_min": 80,
                            "x_max": 280,
                            "y_max": 450,
                            "confidence": 0.92
                        },
                        {
                            "x_min": 400,
                            "y_min": 200,
                            "x_max": 500,
                            "y_max": 600,
                            "confidence": 0.85
                        }
                    ],
                    "banners": []
                }
            },
            {
                "image_id": "images_2.png",
                "detections": {
                    "people": [
                        {
                            "x_min": 100,
                            "y_min": 50,
                            "x_max": 250,
                            "y_max": 500,
                            "confidence": 0.88
                        }
                    ],
                    "banners": [
                        {
                            "x_min": 300,
                            "y_min": 100,
                            "x_max": 600,
                            "y_max": 200,
                            "confidence": 0.91,
                            "text": "示例文字"
                        }
                    ]
                }
            },
            {
                "image_id": "images_3.jpg",
                "detections": {
                    "people": [],
                    "banners": [
                        {
                            "x_min": 50,
                            "y_min": 30,
                            "x_max": 400,
                            "y_max": 100,
                            "confidence": 0.87,
                            "text": "Welcome"
                        }
                    ]
                }
            },
            {
                "image_id": "images_4.jpg",
                "detections": {
                    "people": [
                        {
                            "x_min": 200,
                            "y_min": 100,
                            "x_max": 350,
                            "y_max": 550,
                            "confidence": 0.94
                        },
                        {
                            "x_min": 450,
                            "y_min": 120,
                            "x_max": 580,
                            "y_max": 520,
                            "confidence": 0.89
                        },
                        {
                            "x_min": 50,
                            "y_min": 150,
                            "x_max": 180,
                            "y_max": 480,
                            "confidence": 0.82
                        }
                    ],
                    "banners": []
                }
            },
            {
                "image_id": "images_5.png",
                "detections": {
                    "people": [
                        {
                            "x_min": 120,
                            "y_min": 60,
                            "x_max": 260,
                            "y_max": 480,
                            "confidence": 0.90
                        }
                    ],
                    "banners": [
                        {
                            "x_min": 300,
                            "y_min": 50,
                            "x_max": 650,
                            "y_max": 150,
                            "confidence": 0.93,
                            "text": "示例横幅文字"
                        },
                        {
                            "x_min": 50,
                            "y_min": 400,
                            "x_max": 280,
                            "y_max": 450,
                            "confidence": 0.78,
                            "text": "Sign"
                        }
                    ]
                }
            }
        ]
    }
    
    # 计算统计信息
    total_images = len(demo_results["results"])
    total_people = sum(len(r["detections"]["people"]) for r in demo_results["results"])
    total_banners = sum(len(r["detections"]["banners"]) for r in demo_results["results"])
    
    all_people_confidences = []
    all_banner_confidences = []
    
    for result in demo_results["results"]:
        for person in result["detections"]["people"]:
            all_people_confidences.append(person["confidence"])
        for banner in result["detections"]["banners"]:
            all_banner_confidences.append(banner["confidence"])
    
    people_per_image = [len(r["detections"]["people"]) for r in demo_results["results"]]
    banners_per_image = [len(r["detections"]["banners"]) for r in demo_results["results"]]
    
    demo_stats = {
        "total_images_processed": total_images,
        "total_people_detected": total_people,
        "total_banners_detected": total_banners,
        "average_people_per_image": round(total_people / total_images, 2) if total_images > 0 else 0.0,
        "average_banners_per_image": round(total_banners / total_images, 2) if total_images > 0 else 0.0,
        "average_confidence_people": round(sum(all_people_confidences) / len(all_people_confidences), 3) if all_people_confidences else 0.0,
        "average_confidence_banners": round(sum(all_banner_confidences) / len(all_banner_confidences), 3) if all_banner_confidences else 0.0,
        "max_people_in_image": max(people_per_image) if people_per_image else 0,
        "min_people_in_image": min(people_per_image) if people_per_image else 0,
        "max_banners_in_image": max(banners_per_image) if banners_per_image else 0,
        "min_banners_in_image": min(banners_per_image) if banners_per_image else 0,
        "failed_images": 0,
        "failed_image_paths": [],
        "note": "这是演示输出，实际运行detector.py会得到真实的检测结果"
    }
    
    # 保存演示结果
    os.makedirs("demo_output", exist_ok=True)
    
    with open("demo_output/demo_results.json", "w", encoding="utf-8") as f:
        json.dump(demo_results, f, indent=2, ensure_ascii=False)
    
    with open("demo_output/demo_statistics.json", "w", encoding="utf-8") as f:
        json.dump(demo_stats, f, indent=2, ensure_ascii=False)
    
    # 打印摘要
    print("\n" + "="*60)
    print("演示输出已生成")
    print("="*60)
    print(f"\n处理的图片数量: {total_images}")
    print(f"检测到的人物总数: {total_people}")
    print(f"检测到的横幅总数: {total_banners}")
    print(f"\n平均每张图片人物数: {demo_stats['average_people_per_image']}")
    print(f"平均每张图片横幅数: {demo_stats['average_banners_per_image']}")
    print(f"\n人物平均置信度: {demo_stats['average_confidence_people']}")
    print(f"横幅平均置信度: {demo_stats['average_confidence_banners']}")
    print(f"\n单张图片最多人物: {demo_stats['max_people_in_image']}")
    print(f"单张图片最多横幅: {demo_stats['max_banners_in_image']}")
    print("\n" + "="*60)
    print("\n文件已保存到:")
    print("  - demo_output/demo_results.json")
    print("  - demo_output/demo_statistics.json")
    print("\n注意: 这是演示输出格式。")
    print("要获得真实检测结果，请安装Python后运行 detector.py")
    print("="*60 + "\n")

if __name__ == "__main__":
    create_demo_output()

