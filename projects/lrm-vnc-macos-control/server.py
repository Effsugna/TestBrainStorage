import time
import base64
from io import BytesIO
from flask import Flask, jsonify, request
from PIL import Image
import Quartz
from control import click_mouse, move_mouse, key_press

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

@app.route("/act", methods=["POST"])
def act_endpoint():
    try:
        data = request.get_json()
        action = data.get("action")

        if action == "click":
            x = data.get("x")
            y = data.get("y")
            if x is not None and y is not None:
                click_mouse(x, y)
                return jsonify({"status": "ok"})
            else:
                return jsonify({"error": "Missing x or y for click action"}), 400
        elif action == "move":
            x = data.get("x")
            y = data.get("y")
            if x is not None and y is not None:
                move_mouse(x, y)
                return jsonify({"status": "ok"})
            else:
                return jsonify({"error": "Missing x or y for move action"}), 400
        elif action == "key":
            keycode = data.get("keycode")
            if keycode is not None:
                key_press(keycode)
                return jsonify({"status": "ok"})
            else:
                return jsonify({"error": "Missing keycode for key action"}), 400
        else:
            return jsonify({"error": "Unknown action type"}), 400
            return jsonify({"error": "Unknown action type"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5051)
