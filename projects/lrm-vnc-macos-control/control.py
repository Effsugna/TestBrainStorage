import Quartz


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


def type_string(text):
    for char in text:
        event_down = Quartz.CGEventCreateKeyboardEvent(None, 0, True)
        event_up = Quartz.CGEventCreateKeyboardEvent(None, keycode, False)