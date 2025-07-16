from screen import capture_screen
from ocr import read_text


def process_vision():
    img = capture_screen()
    text = read_text(img)
    return {"text": text, "image": img}


if __name__ == "__main__":
    result = process_vision()
    print("Extracted Text:\n", result["text"])