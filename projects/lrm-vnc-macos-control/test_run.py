from screen import capture_screen
from control import move_mouse, click_mouse
import time

if __name__ == "__main__":
    print("Capturing screen...")
    img = capture_screen()
    img.save("test_screen.jpg")
    print("Saved screenshot as test_screen.jpg")

    print("Moving mouse to (100, 100)...")
    move_mouse(100, 100)
    time.sleep(1)
    
    print("Clicking mouse...")
    click_mouse()
    print("Done.")