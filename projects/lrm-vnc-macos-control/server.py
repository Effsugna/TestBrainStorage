import time
import base64
from io import BytesIO
from flask import Flask, jsonify
from PIL import Image
import Quartz

app = Flask(__name__)

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

@app.route("/capture", methods=["GET"])
def capture_endpoint():
    try:
        img = capture_screen()
        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return jsonify({"image_base64": encoded})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)

