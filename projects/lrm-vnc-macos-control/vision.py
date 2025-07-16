import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import base64


def decode_base64_image(data):
    try:
        image_data = base64.b64decode(data)
        img_array = np.frombuffer(image_data, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        raise ValueError(f"Failed to decode base64 image: {e}")


def find_template(base_img, template_img_path, threshold=0.9):
    template = cv2.imread(template_img_path, cv2.IMREAD_COLOR)
    if template is None:
        raise ValueError(f"Template not found at path: {template_img_path}")

    result = cv2.matchTemplate(base_img, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        return max_loc, template.shape[1], template.shape_