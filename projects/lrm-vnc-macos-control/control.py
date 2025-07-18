import Quartz
import time


def move_mouse(x, y):
    event = Quartz.CGEventCreateMouseEvent(
        None, Quartz.kCGEventMouseMoved, (x, y), Quartz.kCGMouseButtonLeft
    )
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)


def click_mouse(x, y):
    for event_type in [Quartz.kCGEventLeftMouseDown, Quartz.kCGEventLeftMouseUp]:
        event = Quartz.CGEventCreateMouseEvent(
            None, event_type, (x, y), Quartz.kCGMouseButtonLeft
        )
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)


def key_press(keycode):
    event_down = Quartz.CGEventCreateKeyboardEvent(None, keycode, True)
    event_up = Quartz.CGEventCreateKeyboardEvent(None, keycode, False)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_down)
    time.sleep(0.01) # Add a small delay
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_up)