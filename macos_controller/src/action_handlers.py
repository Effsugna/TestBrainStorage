import logging
from typing import Any, Dict, List, Optional, Tuple
import base64
import os
import sys
import asyncio # Import asyncio for async operations

import mcp.types as types
# Import vnc_client from the current directory
from .vnc_client import VNCClient

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('action_handlers')
logger.setLevel(logging.DEBUG)

# This global VNC client will be managed by the server
vnc_client: Optional[VNCClient] = None

async def handle_remote_macos_get_screen(arguments: dict[str, Any]) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Connect to a remote MacOs machine and get a screenshot of the remote desktop."""
    if not vnc_client or not vnc_client.socket:
        return [types.TextContent(type="text", text="VNC client not connected.")]

    # Capture screen using the existing connection
    screen_data = await vnc_client.capture_screen()

    if not screen_data:
        return [types.TextContent(type="text", text="Failed to capture screenshot.")]

    # Encode image in base64
    base64_data = base64.b64encode(screen_data).decode('utf-8')

    # Return image content with dimensions
    width, height = vnc_client.width, vnc_client.height
    return [
        types.ImageContent(
            type="image",
            data=base64_data,
            mimeType="image/png",
            alt_text=f"Screenshot from remote MacOs machine at {vnc_client.host}:{vnc_client.port}"
        ),
        types.TextContent(
            type="text",
            text=f"Image dimensions: {width}x{height}"
        )
    ]

async def handle_remote_macos_mouse_scroll(arguments: dict[str, Any]) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Perform a mouse scroll action on a remote MacOs machine."""
    if not vnc_client or not vnc_client.socket:
        return [types.TextContent(type="text", text="VNC client not connected.")]

    # Get required parameters from arguments
    x = arguments.get("x")
    y = arguments.get("y")
    source_width = int(arguments.get("source_width", 1366))
    source_height = int(arguments.get("source_height", 768))
    direction = arguments.get("direction", "down")

    if x is None or y is None:
        raise ValueError("x and y coordinates are required")

    # Ensure source dimensions are positive
    if source_width <= 0 or source_height <= 0:
        raise ValueError("Source dimensions must be positive values")

    # Get target screen dimensions
    target_width = vnc_client.width
    target_height = vnc_client.height

    # Scale coordinates
    scaled_x = int((x / source_width) * target_width)
    scaled_y = int((y / source_height) * target_height)

    # Ensure coordinates are within the screen bounds
    scaled_x = max(0, min(scaled_x, target_width - 1))
    scaled_y = max(0, min(scaled_y, target_height - 1))

    # First move the mouse to the target location without clicking
    move_result = await vnc_client.send_pointer_event(scaled_x, scaled_y, 0)

    # Map of special keys for page up/down
    special_keys = {
        "up": 0xff55,    # Page Up key
        "down": 0xff56,  # Page Down key
    }

    # Send the appropriate page key based on direction
    key = special_keys["up" if direction.lower() == "up" else "down"]
    key_result = await vnc_client.send_key_event(key, True) and await vnc_client.send_key_event(key, False)

    # Prepare the response with useful details
    scale_factors = {
        "x": target_width / source_width,
        "y": target_height / source_height
    }

    return [types.TextContent(
        type="text",
        text=f"""Mouse move to ({scaled_x}, {scaled_y}) {'succeeded' if move_result else 'failed'}
Page {direction} key press {'succeeded' if key_result else 'failed'}
Source dimensions: {source_width}x{source_height}
Target dimensions: {target_width}x{target_height}
Scale factors: {scale_factors['x']:.4f}x, {scale_factors['y']:.4f}y"""
    )]

async def handle_remote_macos_mouse_click(arguments: dict[str, Any]) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Perform a mouse click action on a remote MacOs machine."""
    if not vnc_client or not vnc_client.socket:
        return [types.TextContent(type="text", text="VNC client not connected.")]

    # Get required parameters from arguments
    x = arguments.get("x")
    y = arguments.get("y")
    source_width = int(arguments.get("source_width", 1366))
    source_height = int(arguments.get("source_height", 768))
    button = int(arguments.get("button", 1))

    if x is None or y is None:
        raise ValueError("x and y coordinates are required")

    # Ensure source dimensions are positive
    if source_width <= 0 or source_height <= 0:
        raise ValueError("Source dimensions must be positive values")

    # Get target screen dimensions
    target_width = vnc_client.width
    target_height = vnc_client.height

    # Scale coordinates
    scaled_x = int((x / source_width) * target_width)
    scaled_y = int((y / source_height) * target_height)

    # Ensure coordinates are within the screen bounds
    scaled_x = max(0, min(scaled_x, target_width - 1))
    scaled_y = max(0, min(scaled_y, target_height - 1))

    # Single click
    result = await vnc_client.send_mouse_click(scaled_x, scaled_y, button, False)

    # Prepare the response with useful details
    scale_factors = {
        "x": target_width / source_width,
        "y": target_height / source_height
    }

    return [types.TextContent(
        type="text",
        text=f"""Mouse click (button {button}) from source ({x}, {y}) to target ({scaled_x}, {scaled_y}) {'succeeded' if result else 'failed'}
Source dimensions: {source_width}x{source_height}
Target dimensions: {target_width}x{target_height}
Scale factors: {scale_factors['x']:.4f}x, {scale_factors['y']:.4f}y"""
    )]

async def handle_remote_macos_send_keys(arguments: dict[str, Any]) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Send keyboard input to a remote MacOs machine."""
    if not vnc_client or not vnc_client.socket:
        return [types.TextContent(type="text", text="VNC client not connected.")]

    # Get required parameters from arguments
    text = arguments.get("text")
    special_key = arguments.get("special_key")
    key_combination = arguments.get("key_combination")

    if not text and not special_key and not key_combination:
        raise ValueError("Either text, special_key, or key_combination must be provided")

    result_message = []

    # Map of special key names to X11 keysyms
    special_keys = {
        "enter": 0xff0d,
        "return": 0xff0d,
        "backspace": 0xff08,
        "tab": 0xff09,
        "escape": 0xff1b,
        "esc": 0xff1b,
        "delete": 0xffff,
        "del": 0xffff,
        "home": 0xff50,
        "end": 0xff57,
        "page_up": 0xff55,
        "page_down": 0xff56,
        "left": 0xff51,
        "up": 0xff52,
        "right": 0xff53,
        "down": 0xff54,
        "f1": 0xffbe,
        "f2": 0xffbf,
        "f3": 0xffc0,
        "f4": 0xffc1,
        "f5": 0xffc2,
        "f6": 0xffc3,
        "f7": 0xffc4,
        "f8": 0xffc5,
        "f9": 0xffc6,
        "f10": 0xffc7,
        "f11": 0xffc8,
        "f12": 0xffc9,
        "space": 0x20,
    }

    # Map of modifier key names to X11 keysyms
    modifier_keys = {
        "ctrl": 0xffe3,    # Control_L
        "control": 0xffe3,  # Control_L
        "shift": 0xffe1,   # Shift_L
        "alt": 0xffe9,     # Alt_L
        "option": 0xffe9,  # Alt_L (Mac convention)
        "cmd": 0xffeb,     # Command_L (Mac convention)
        "command": 0xffeb,  # Command_L (Mac convention)
        "win": 0xffeb,     # Command_L
        "super": 0xffeb,   # Command_L
        "fn": 0xffed,      # Function key
        "meta": 0xffeb,    # Command_L (Mac convention)
    }

    # Map for letter keys (a-z)
    letter_keys = {chr(i): i for i in range(ord('a'), ord('z') + 1)}

    # Map for number keys (0-9)
    number_keys = {str(i): ord(str(i)) for i in range(10)}

    # Process special key
    if special_key:
        if special_key.lower() in special_keys:
            key = special_keys[special_key.lower()]
            if await vnc_client.send_key_event(key, True) and await vnc_client.send_key_event(key, False):
                result_message.append(f"Sent special key: {special_key}")
            else:
                result_message.append(f"Failed to send special key: {special_key}")
        else:
            result_message.append(f"Unknown special key: {special_key}")
            result_message.append(f"Supported special keys: {', '.join(special_keys.keys())}")

    # Process text
    if text:
        if await vnc_client.send_text(text):
            result_message.append(f"Sent text: '{text}'")
        else:
            result_message.append(f"Failed to send text: '{text}'")

    # Process key combination
    if key_combination:
        keys = []
        for part in key_combination.lower().split('+'):
            part = part.strip()
            if part in modifier_keys:
                keys.append(modifier_keys[part])
            elif part in special_keys:
                keys.append(special_keys[part])
            elif part in letter_keys:
                keys.append(letter_keys[part])
            elif part in number_keys:
                keys.append(number_keys[part])
            elif len(part) == 1:
                # For any other single character keys
                keys.append(ord(part))
            else:
                result_message.append(f"Unknown key in combination: {part}")
                break

        if len(keys) == len(key_combination.split('+')):
            if await vnc_client.send_key_combination(keys):
                result_message.append(f"Sent key combination: {key_combination}")
            else:
                result_message.append(f"Failed to send key combination: {key_combination}")

    return [types.TextContent(type="text", text="\n".join(result_message))]

async def handle_remote_macos_mouse_double_click(arguments: dict[str, Any]) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Perform a mouse double-click action on a remote MacOs machine."""
    if not vnc_client or not vnc_client.socket:
        return [types.TextContent(type="text", text="VNC client not connected.")]

    # Get required parameters from arguments
    x = arguments.get("x")
    y = arguments.get("y")
    source_width = int(arguments.get("source_width", 1366))
    source_height = int(arguments.get("source_height", 768))
    button = int(arguments.get("button", 1))

    if x is None or y is None:
        raise ValueError("x and y coordinates are required")

    # Ensure source dimensions are positive
    if source_width <= 0 or source_height <= 0:
        raise ValueError("Source dimensions must be positive values")

    # Get target screen dimensions
    target_width = vnc_client.width
    target_height = vnc_client.height

    # Scale coordinates
    scaled_x = int((x / source_width) * target_width)
    scaled_y = int((y / source_height) * target_height)

    # Ensure coordinates are within the screen bounds
    scaled_x = max(0, min(scaled_x, target_width - 1))
    scaled_y = max(0, min(scaled_y, target_height - 1))

    # Double click
    result = await vnc_client.send_mouse_click(scaled_x, scaled_y, button, True)

    # Prepare the response with useful details
    scale_factors = {
        "x": target_width / source_width,
        "y": target_height / source_height
    }

    return [types.TextContent(
        type="text",
        text=f"""Mouse double-click (button {button}) from source ({x}, {y}) to target ({scaled_x}, {scaled_y}) {'succeeded' if result else 'failed'}
Source dimensions: {source_width}x{source_height}
Target dimensions: {target_width}x{target_height}
Scale factors: {scale_factors['x']:.4f}x, {scale_factors['y']:.4f}y"""
    )]

async def handle_remote_macos_mouse_move(arguments: dict[str, Any]) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Move the mouse cursor on a remote MacOs machine."""
    if not vnc_client or not vnc_client.socket:
        return [types.TextContent(type="text", text="VNC client not connected.")]

    # Get required parameters from arguments
    x = arguments.get("x")
    y = arguments.get("y")
    source_width = int(arguments.get("source_width", 1366))
    source_height = int(arguments.get("source_height", 768))

    if x is None or y is None:
        raise ValueError("x and y coordinates are required")

    # Ensure source dimensions are positive
    if source_width <= 0 or source_height <= 0:
        raise ValueError("Source dimensions must be positive values")

    # Get target screen dimensions
    target_width = vnc_client.width
    target_height = vnc_client.height

    # Scale coordinates
    scaled_x = int((x / source_width) * target_width)
    scaled_y = int((y / source_height) * target_height)

    # Ensure coordinates are within the screen bounds
    scaled_x = max(0, min(scaled_x, target_width - 1))
    scaled_y = max(0, min(scaled_y, target_height - 1))

    # Move mouse pointer (button_mask=0 means no buttons are pressed)
    result = await vnc_client.send_pointer_event(scaled_x, scaled_y, 0)

    # Prepare the response with useful details
    scale_factors = {
        "x": target_width / source_width,
        "y": target_height / source_height
    }

    return [types.TextContent(
        type="text",
        text=f"""Mouse move from source ({x}, {y}) to target ({scaled_x}, {scaled_y}) {'succeeded' if result else 'failed'}
Source dimensions: {source_width}x{source_height}
Target dimensions: {target_width}x{target_height}
Scale factors: {scale_factors['x']:.4f}x, {scale_factors['y']:.4f}y"""
    )]

async def handle_remote_macos_open_application(arguments: dict[str, Any]) -> List[types.TextContent]:
    """
    Opens or activates an application on the remote MacOS machine using VNC.

    Args:
        arguments: Dictionary containing:
            - identifier: App name, path, or bundle ID

    Returns:
        List containing a TextContent with the result
    """
    if not vnc_client or not vnc_client.socket:
        return [types.TextContent(type="text", text="VNC client not connected.")]

    identifier = arguments.get("identifier")
    if not identifier:
        raise ValueError("identifier is required")

    start_time = asyncio.get_event_loop().time() # Use asyncio's time for async context

    # Send Command+Space to open Spotlight
    cmd_key = 0xffeb  # Command key
    space_key = 0x20  # Space key

    # Press Command+Space
    await vnc_client.send_key_event(cmd_key, True)
    await vnc_client.send_key_event(space_key, True)

    # Release Command+Space
    await vnc_client.send_key_event(space_key, False)
    await vnc_client.send_key_event(cmd_key, False)

    # Small delay to let Spotlight open
    await asyncio.sleep(0.5)

    # Type the application name
    await vnc_client.send_text(identifier)

    # Small delay to let Spotlight find the app
    await asyncio.sleep(0.5)

    # Press Enter to launch
    enter_key = 0xff0d
    await vnc_client.send_key_event(enter_key, True)
    await vnc_client.send_key_event(enter_key, False)

    end_time = asyncio.get_event_loop().time()
    processing_time = round(end_time - start_time, 3)

    return [types.TextContent(
        type="text",
        text=f"Launched application: {identifier}\nProcessing time: {processing_time}s"
    )]

async def handle_remote_macos_mouse_drag_n_drop(arguments: dict[str, Any]) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Perform a mouse drag operation on a remote MacOs machine."""
    if not vnc_client or not vnc_client.socket:
        return [types.TextContent(type="text", text="VNC client not connected.")]

    # Get required parameters from arguments
    start_x = arguments.get("start_x")
    start_y = arguments.get("start_y")
    end_x = arguments.get("end_x")
    end_y = arguments.get("end_y")
    source_width = int(arguments.get("source_width", 1366))
    source_height = int(arguments.get("source_height", 768))
    button = int(arguments.get("button", 1))
    steps = int(arguments.get("steps", 10))
    delay_ms = int(arguments.get("delay_ms", 10))

    # Validate required parameters
    if any(x is None for x in [start_x, start_y, end_x, end_y]):
        raise ValueError("start_x, start_y, end_x, and end_y coordinates are required")

    # Ensure source dimensions are positive
    if source_width <= 0 or source_height <= 0:
        raise ValueError("Source dimensions must be positive values")

    # Get target screen dimensions
    target_width = vnc_client.width
    target_height = vnc_client.height

    # Scale coordinates
    scaled_start_x = int((start_x / source_width) * target_width)
    scaled_start_y = int((start_y / source_height) * target_height)
    scaled_end_x = int((end_x / source_width) * target_width)
    scaled_end_y = int((end_y / source_height) * target_height)

    # Ensure coordinates are within the screen bounds
    scaled_start_x = max(0, min(scaled_start_x, target_width - 1))
    scaled_start_y = max(0, min(scaled_start_y, target_height - 1))
    scaled_end_x = max(0, min(scaled_end_x, target_width - 1))
    scaled_end_y = max(0, min(scaled_end_y, target_height - 1))

    # Calculate step sizes
    dx = (scaled_end_x - scaled_start_x) / steps
    dy = (scaled_end_y - scaled_start_y) / steps

    # Move to start position
    if not await vnc_client.send_pointer_event(scaled_start_x, scaled_start_y, 0):
        return [types.TextContent(type="text", text="Failed to move to start position")]

    # Press button
    button_mask = 1 << (button - 1)
    if not await vnc_client.send_pointer_event(scaled_start_x, scaled_start_y, button_mask):
        return [types.TextContent(type="text", text="Failed to press mouse button")]

    # Perform drag
    for step in range(1, steps + 1):
        current_x = int(scaled_start_x + dx * step)
        current_y = int(scaled_start_y + dy * step)
        if not await vnc_client.send_pointer_event(current_x, current_y, button_mask):
            return [types.TextContent(type="text", text=f"Failed during drag at step {step}")]
        await asyncio.sleep(delay_ms / 1000.0)  # Convert ms to seconds

    # Release button at final position
    if not await vnc_client.send_pointer_event(scaled_end_x, scaled_end_y, 0):
        return [types.TextContent(type="text", text="Failed to release mouse button")]

    # Prepare the response with useful details
    scale_factors = {
        "x": target_width / source_width,
        "y": target_height / source_height
    }

    return [types.TextContent(
        type="text",
        text=f"""Mouse drag (button {button}) completed:
From source ({start_x}, {start_y}) to ({end_x}, {end_y})
From target ({scaled_start_x}, {scaled_start_y}) to ({scaled_end_x}, {scaled_end_y})
Source dimensions: {source_width}x{source_height}
Target dimensions: {target_width}x{target_height}
Scale factors: {scale_factors['x']:.4f}x, {scale_factors['y']:.4f}y
Steps: {steps}
Delay: {delay_ms}ms"""
    )]