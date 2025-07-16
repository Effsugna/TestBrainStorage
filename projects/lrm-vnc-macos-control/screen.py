import Quartz
from PIL import Image
from io import BytesIO
import base64


def capture_screen():
    display_id = Quartz.CGMainDisplayID()
    image = Quartz.CGDisplayCreateImage(display_id)
    if image is None:
        raise RuntimeError("Screen capture failed")

    width = Quartz.CGImageGetWidth(image)
    height = Quartz.CGImageGetHeight(image)
    bytes_per_row = Quartz.CGImageGetBytesPerRow(image)
    data_provider = Quartz.CGImageGetDataProvider(image)
    data = Quartz.CGDataProviderCopyData(data_provider)

    img = Image.frombytes("RGB", (width, height), bytes(data), "raw", "RGBX", bytes_per_row, 1)
    return img


def encode_image(img):
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return encoded