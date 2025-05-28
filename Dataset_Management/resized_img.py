import cv2
import numpy as np
import os

def letterbox_image(image, new_size=(640, 640)):
    h, w, _ = image.shape
    scale = min(new_size[0] / w, new_size[1] / h)
    new_w = int(w * scale)
    new_h = int(h * scale)

    resized_image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    canvas = np.full((new_size[1], new_size[0], 3), 128, dtype=np.uint8)

    top = (new_size[1] - new_h) // 2
    left = (new_size[0] - new_w) // 2
    canvas[top:top+new_h, left:left+new_w, :] = resized_image

    return canvas, scale, left, top

# Resize tất cả ảnh
input_folder = "D:\\dataset\\images\\val"
output_folder = "D:\\dataset\\images\\val_resized"
os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    img_path = os.path.join(input_folder, filename)
    img = cv2.imread(img_path)

    if img is not None:
        img_resized, scale, left, top = letterbox_image(img, (640, 640))
        cv2.imwrite(os.path.join(output_folder, filename), img_resized)