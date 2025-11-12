# Detection Test Report Template

Use this template to capture detection pipeline test results.

- Test date: 
- Machine / OS:
- Python version:
- Docker image used (if any):
- Test dataset (number of images):

## Summary Statistics
- Total images processed: 
- Total people detected: 
- Total banners detected: 
- Average people per image: 
- Average banners per image: 
- Average person confidence: 
- Average banner confidence: 
- Max/min people in a single image: 
- Max/min banners in a single image: 

## Failures / Errors
- Corrupt images: (list)
- Exception traces: (attach)
- Missed detection cases / FP cases: (list)

## Notes / Next Steps
- 


Generated JSON files:
- outputs/summary.json
- outputs/<image>.json
- output_images/ annotated images

