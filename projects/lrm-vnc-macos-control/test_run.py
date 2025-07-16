from screen import capture_screen
from vision import analyze_screen

if __name__ == "__main__":
    print("Capturing screen...")
    img = capture_screen()

    print("Analyzing screen...")
    objects = analyze_screen(img)

    print("Detected objects:")
    for obj in objects:
        print(obj)