import logging
import asyncio
import io
from PIL import Image
from typing import Optional, Tuple, List, Any

from asyncvnc.client import VNCClient as AsyncVNCClient
from asyncvnc.exceptions import VNCError
from asyncvnc.keysyms import KEYSYMS

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('vnc_client')
logger.setLevel(logging.DEBUG)

class VNCClient:
    """Wrapper around AsyncVNCClient for persistent connection and simplified interface."""

    def __init__(self, host: str, port: int = 5900, password: Optional[str] = None, username: Optional[str] = None,
                 encryption: str = "prefer_on"):
        self.host = host
        self.port = port
        self.password = password
        self.username = username
        self.encryption = encryption # Not directly used by AsyncVNC, but kept for consistency
        self._client: Optional[AsyncVNCClient] = None
        self.width = 0
        self.height = 0
        self.socket = None # Placeholder for compatibility with action_handlers

    async def connect(self) -> Tuple[bool, Optional[str]]:
        """Connect to the remote MacOs machine using AsyncVNCClient."""
        try:
            logger.info(f"Attempting connection to remote MacOs machine at {self.host}:{self.port}")
            self._client = AsyncVNCClient(
                host=self.host,
                port=self.port,
                password=self.password,
                username=self.username,
                # AsyncVNC handles encryption negotiation automatically
            )
            await self._client.connect()
            self.width = self._client.width
            self.height = self._client.height
            self.socket = True # Indicate connected state for action_handlers
            logger.info(f"Successfully connected to remote MacOs machine: {self.width}x{self.height}")
            return True, None
        except VNCError as e:
            error_msg = f"VNC connection error: {e}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error during VNC connection: {e}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg

    async def capture_screen(self) -> Optional[bytes]:
        """Capture a screenshot from the remote MacOs machine using AsyncVNCClient."""
        if not self._client or not self._client.is_connected:
            logger.error("Not connected to remote MacOs machine for screen capture.")
            return None

        try:
            # Request a full screen update
            await self._client.framebuffer_update_request(0, 0, self.width, self.height, incremental=False)
            # AsyncVNC automatically updates its internal framebuffer

            # Get the raw pixel data from AsyncVNC's framebuffer
            raw_pixel_data = await self._client.get_framebuffer()

            if not raw_pixel_data:
                logger.error("Failed to get raw pixel data from framebuffer.")
                return None

            # AsyncVNC returns raw pixel data in RGB format
            img = Image.frombytes('RGB', (self.width, self.height), raw_pixel_data)

            # Scale the image to FWXGA resolution (1366x768)
            target_width, target_height = 1366, 768
            scaled_img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

            # Convert to PNG bytes
            output_buffer = io.BytesIO()
            scaled_img.save(output_buffer, format='PNG', optimize=True, quality=95)
            output_buffer.seek(0)
            return output_buffer.getvalue()

        except VNCError as e:
            logger.error(f"VNC screen capture error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during screen capture: {e}", exc_info=True)
            return None

    async def send_key_event(self, key: int, down: bool) -> bool:
        """Send a key event to the remote MacOs machine using AsyncVNCClient."""
        if not self._client or not self._client.is_connected:
            logger.error("Not connected to remote MacOs machine for key event.")
            return False
        try:
            await self._client.key_event(key, down)
            return True
        except VNCError as e:
            logger.error(f"VNC key event error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending key event: {e}", exc_info=True)
            return False

    async def send_pointer_event(self, x: int, y: int, button_mask: int) -> bool:
        """Send a pointer (mouse) event to the remote MacOs machine using AsyncVNCClient."""
        if not self._client or not self._client.is_connected:
            logger.error("Not connected to remote MacOs machine for pointer event.")
            return False
        try:
            await self._client.pointer_event(x, y, button_mask)
            return True
        except VNCError as e:
            logger.error(f"VNC pointer event error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending pointer event: {e}", exc_info=True)
            return False

    async def send_mouse_click(self, x: int, y: int, button: int = 1, double_click: bool = False, delay_ms: int = 100) -> bool:
        """Send a mouse click at the specified position using AsyncVNCClient."""
        if not self._client or not self._client.is_connected:
            logger.error("Not connected to remote MacOs machine for mouse click.")
            return False
        try:
            # AsyncVNC's pointer_event handles button masks directly
            button_mask = 1 << (button - 1)

            # Move mouse to position first (no buttons pressed)
            await self.send_pointer_event(x, y, 0)

            # Single click or first click of double-click
            await self.send_pointer_event(x, y, button_mask)
            await asyncio.sleep(delay_ms / 1000.0)
            await self.send_pointer_event(x, y, 0)

            # If double click, perform second click
            if double_click:
                await asyncio.sleep(delay_ms / 1000.0)
                await self.send_pointer_event(x, y, button_mask)
                await asyncio.sleep(delay_ms / 1000.0)
                await self.send_pointer_event(x, y, 0)
            return True
        except VNCError as e:
            logger.error(f"VNC mouse click error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending mouse click: {e}", exc_info=True)
            return False

    async def send_text(self, text: str) -> bool:
        """Send text as a series of key press/release events using AsyncVNCClient."""
        if not self._client or not self._client.is_connected:
            logger.error("Not connected to remote MacOs machine for sending text.")
            return False
        try:
            success = True
            for char in text:
                # AsyncVNC's KEYSYMS provides X11 keysyms
                # For simple ASCII, ord(char) often works directly as keysym
                # For special characters or shifted characters, more logic might be needed
                # For now, rely on direct char to keysym mapping where possible
                keysym = KEYSYMS.get(char.upper(), ord(char)) # Try uppercase for shifted keys

                # Handle shift for uppercase letters and symbols
                if char.isupper() or char in '~!@#$%^&*()_+{}|:"<>?' or (char.isdigit() and char in '!@#$%^&*()'):
                    await self.send_key_event(KEYSYMS['Shift_L'], True)
                    await asyncio.sleep(0.01)

                await self.send_key_event(keysym, True)
                await asyncio.sleep(0.01)
                await self.send_key_event(keysym, False)
                await asyncio.sleep(0.01)

                if char.isupper() or char in '~!@#$%^&*()_+{}|:"<>?' or (char.isdigit() and char in '!@#$%^&*()'):
                    await self.send_key_event(KEYSYMS['Shift_L'], False)
                    await asyncio.sleep(0.01)

            return success
        except VNCError as e:
            logger.error(f"VNC send text error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending text: {e}", exc_info=True)
            return False

    async def send_key_combination(self, keys: List[int]) -> bool:
        """Send a key combination (e.g., Ctrl+Alt+Delete) using AsyncVNCClient."""
        if not self._client or not self._client.is_connected:
            logger.error("Not connected to remote MacOs machine for key combination.")
            return False
        try:
            # Press all keys in sequence
            for key in keys:
                await self.send_key_event(key, True)
                await asyncio.sleep(0.01) # Small delay

            # Release all keys in reverse order
            for key in reversed(keys):
                await self.send_key_event(key, False)
                await asyncio.sleep(0.01) # Small delay
            return True
        except VNCError as e:
            logger.error(f"VNC key combination error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending key combination: {e}", exc_info=True)
            return False

    def close(self):
        """Close the connection to the remote MacOs machine."""
        if self._client and self._client.is_connected:
            self._client.close()
            logger.info("VNC client connection closed.")
        self.socket = None # Reset placeholder

async def capture_vnc_screen(host: str, port: int, password: str, username: Optional[str] = None,
                             encryption: str = "prefer_on") -> Tuple[bool, Optional[bytes], Optional[str], Optional[Tuple[int, int]]]:
    """Standalone function to capture a screenshot, for initial testing or one-off use."""
    vnc = VNCClient(host=host, port=port, password=password, username=username, encryption=encryption)
    try:
        success, error_message = await vnc.connect()
        if not success:
            return False, None, error_message, None
        screen_data = await vnc.capture_screen()
        if screen_data:
            return True, screen_data, None, (vnc.width, vnc.height)
        else:
            return False, None, "Failed to capture screen data.", None
    finally:
        vnc.close()

if __name__ == '__main__':
    from dotenv import load_dotenv
    import os
    load_dotenv()

    host = os.environ.get('MACOS_HOST')
    port = int(os.environ.get('MACOS_PORT', 5900))
    password = os.environ.get('MACOS_PASSWORD')
    username = os.environ.get('MACOS_USERNAME')

    if not all([host, password]):
        print("Please set MACOS_HOST and MACOS_PASSWORD environment variables.")
    else:
        async def run_test():
            success, screen_data, error_message, dims = await capture_vnc_screen(
                host=host, port=port, password=password, username=username
            )
            if success:
                with open("screenshot.png", "wb") as f:
                    f.write(screen_data)
                print(f"Screenshot saved to screenshot.png (Dimensions: {dims[0]}x{dims[1]})\n")
            else:
                print(f"Error: {error_message}\n")

        asyncio.run(run_test())