from ultralytics import YOLO
import numpy as np

class PersonDetector:
    def __init__(self, model_path='yolov8n.pt', device='cpu', conf_thresh=0.25):
        self.model = YOLO(model_path)
        self.device = device
        self.conf_thresh = conf_thresh

    def detect(self, image):
        # Returns list of dicts: {x_min,y_min,x_max,y_max,confidence}
        results = self.model.predict(source=image, device=self.device, imgsz=max(image.shape[:2]), verbose=False)
        detections = []
        for r in results:
            # r.boxes.xyxyn - normalized boxes
            boxes = getattr(r, 'boxes', None)
            if boxes is None:
                continue
            xyxy = boxes.xyxy.cpu().numpy()
            confs = boxes.conf.cpu().numpy()
            cls = boxes.cls.cpu().numpy()
            for (x1, y1, x2, y2), conf, c in zip(xyxy, confs, cls):
                # COCO person class id = 0
                if int(c) == 0 and conf >= self.conf_thresh:
                    detections.append({
                        'x_min': int(x1),
                        'y_min': int(y1),
                        'x_max': int(x2),
                        'y_max': int(y2),
                        'confidence': float(conf)
                    })
        return detections
