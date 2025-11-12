import easyocr
import numpy as np

class TextDetector:
    def __init__(self, lang_list=['en'], gpu=False, conf_thresh=0.3):
        self.reader = easyocr.Reader(lang_list, gpu=gpu)
        self.conf_thresh = conf_thresh

    def detect(self, image):
        # easyocr returns [(bbox, text, conf), ...] with bbox as list of four points
        results = self.reader.readtext(image)
        text_boxes = []
        for bbox, text, conf in results:
            if conf < self.conf_thresh:
                continue
            xs = [int(p[0]) for p in bbox]
            ys = [int(p[1]) for p in bbox]
            x_min, y_min = min(xs), min(ys)
            x_max, y_max = max(xs), max(ys)
            text_boxes.append({'x_min': x_min, 'y_min': y_min, 'x_max': x_max, 'y_max': y_max, 'confidence': float(conf), 'text': text})
        # Group text boxes to form banners
        groups = self._group_text_boxes(text_boxes)
        return groups

    def _group_text_boxes(self, text_boxes, x_tol=50, y_tol=20):
        """
        Simple greedy grouping: merge boxes that overlap or are close horizontally/vertically.
        """
        if not text_boxes:
            return []
        boxes = sorted(text_boxes, key=lambda x: (x['y_min'], x['x_min']))
        banners = []
        used = [False]*len(boxes)
        for i,b in enumerate(boxes):
            if used[i]:
                continue
            cur = b.copy()
            used[i] = True
            texts = [b['text']]
            for j in range(i+1, len(boxes)):
                if used[j]:
                    continue
                nb = boxes[j]
                # If boxes are close in y or overlap
                if (abs(nb['y_min'] - cur['y_min']) <= y_tol) or (not (nb['y_min'] > cur['y_max'] or nb['y_max'] < cur['y_min'])):
                    # expand
                    cur['x_min'] = min(cur['x_min'], nb['x_min'])
                    cur['y_min'] = min(cur['y_min'], nb['y_min'])
                    cur['x_max'] = max(cur['x_max'], nb['x_max'])
                    cur['y_max'] = max(cur['y_max'], nb['y_max'])
                    texts.append(nb['text'])
                    used[j] = True
            banner = {'x_min': cur['x_min'], 'y_min': cur['y_min'], 'x_max': cur['x_max'], 'y_max': cur['y_max'], 'confidence': float(np.mean([b['confidence'] for b in boxes if b['y_min']>=cur['y_min'] and b['y_max']<=cur['y_max']] or [cur['confidence']])), 'text': ' '.join(texts)}
            banners.append(banner)
        return banners
