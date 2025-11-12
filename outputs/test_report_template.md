# Test Report

- Total images tested:
- Total people detected:
- Total banners detected:
- Average people per image:
- Average banners per image:
- Average confidence (people):
- Average confidence (banners):

## Issues & Observations


## Environment

- Python version:
- Packages:

## Repro Steps

## 示例输出（示范）

下面是 `outputs/detections.json` 的示例内容，展示了人员检测、横幅检测与统计信息的 JSON 格式：

```json
{
  "images": [
    {
      "image_id": "street_001.jpg",
      "detections": {
        "people": [
          {"x_min": 34, "y_min": 50, "x_max": 120, "y_max": 310, "confidence": 0.95},
          {"x_min": 200, "y_min": 80, "x_max": 280, "y_max": 320, "confidence": 0.87}
        ],
        "banners": [
          {"x_min": 50, "y_min": 400, "x_max": 400, "y_max": 480, "confidence": 0.92, "text": "Welcome to the park"}
        ]
      }
    },
    {
      "image_id": "protest_010.jpg",
      "detections": {
        "people": [],
        "banners": [
          {"x_min": 12, "y_min": 30, "x_max": 300, "y_max": 120, "confidence": 0.88, "text": "No more war"}
        ]
      }
    }
  ],
  "stats": {
    "total_images": 2,
    "total_people": 2,
    "total_banners": 2,
    "avg_people_per_image": 1.0,
    "avg_banners_per_image": 1.0,
    "avg_conf_people": 0.91,
    "avg_conf_banners": 0.90,
    "max_people_in_image": 2,
    "min_people_in_image": 0,
    "max_banners_in_image": 1,
    "min_banners_in_image": 0
  },
  "errors": [
    {"image_id": "corrupt.jpg", "error": {"error": "image read failed"}}
  ]
}
```

---

## 如何生成真实输出结果

1. 安装依赖：
   - Windows(cmd.exe)：
     - pip install -r requirements.txt
2. 运行检测：
   - python -m src.detect_all --input images --output outputs/detections.json --out-images output_images
   - 或使用一键脚本：`run_demo.bat`
3. 结果：
   - JSON 文件：`outputs/detections.json`
   - 可视化图片：`output_images/<image_name>`（展示标注框和识别文本）
   - 损坏/不可读图片将被记录到 `errors` 字段

---

## 查看/分析建议

- 使用 `jq` 或 Python 脚本来读取并汇总 JSON 中的 `stats` 字段。
- 如果需要逐张验证横幅文本，在 `output_images` 中查看对应图片的文字叠加。 
- 对文本识别质量敏感时，修改 `src/text_detector.py` 中的 `conf_thresh` 或文本分组策略；对人员检测敏感时，修改 `--person-conf`。


