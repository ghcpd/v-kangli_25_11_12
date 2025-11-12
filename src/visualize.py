import cv2

def draw_boxes(image, people=None, banners=None, color_people=(0,255,0), color_banners=(0,0,255)):
    img = image.copy()
    if people:
        for p in people:
            cv2.rectangle(img, (p['x_min'], p['y_min']), (p['x_max'], p['y_max']), color_people, 2)
            cv2.putText(img, f"P:{p['confidence']:.2f}", (p['x_min'], p['y_min']-8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_people, 1)
    if banners:
        for b in banners:
            cv2.rectangle(img, (b['x_min'], b['y_min']), (b['x_max'], b['y_max']), color_banners, 2)
            label = f"B:{b['confidence']:.2f} {b['text'][:30]}"
            cv2.putText(img, label, (b['x_min'], b['y_min']-8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_banners, 1)
    return img
