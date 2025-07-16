import logging
from typing import Any, Dict, List, Optional, Tuple
from dotenv import load_dotenv
import asyncio
import os
import sys

# Import MCP server libraries
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# Import LiveKit
from livekit import api
from .livekit_handler import LiveKitHandler

# Import VNC client and action handlers
from vnc_client import VNCClient
import action_handlers

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('mcp_remote_macos_use')
logger.setLevel(logging.DEBUG)

# Load environment variables
load_dotenv()
MACOS_HOST = os.environ.get('MACOS_HOST', '')
MACOS_PORT = int(os.environ.get('MACOS_PORT', '5900'))
MACOS_USERNAME = os.environ.get('MACOS_USERNAME', '')
MACOS_PASSWORD = os.environ.get('MACOS_PASSWORD', '')
VNC_ENCRYPTION = os.environ.get('VNC_ENCRYPTION', 'prefer_on')
LIVEKIT_URL = os.environ.get('LIVEKIT_URL', '')
LIVEKIT_API_KEY = os.environ.get('LIVEKIT_API_KEY', '')
LIVEKIT_API_SECRET = os.environ.get('LIVEKIT_API_SECRET', '')


async def main():
    """Run the Remote MacOS MCP server."""
    logger.info("Remote MacOS computer use server starting")

    # Validate required environment variables
    if not MACOS_HOST or not MACOS_PASSWORD:
        logger.error("MACOS_HOST and MACOS_PASSWORD environment variables are required.")
        raise ValueError("MACOS_HOST and MACOS_PASSWORD are required.")

    # Initialize and connect the VNC client
    vnc_client = VNCClient(
        host=MACOS_HOST,
        port=MACOS_PORT,
        password=MACOS_PASSWORD,
        username=MACOS_USERNAME,
        encryption=VNC_ENCRYPTION
    )
    success, error_message = vnc_client.connect()
    if not success:
        logger.error(f"Failed to connect VNC client: {error_message}")
        raise ConnectionError(f"VNC connection failed: {error_message}")

    # Make the connected client available to the action handlers
    action_handlers.vnc_client = vnc_client

    livekit_handler = None
    if all([LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET]):
        livekit_handler = LiveKitHandler()
        token = api.AccessToken() \
            .with_identity("remote-macos-bot") \
            .with_name("Remote MacOS Bot") \
            .with_grants(api.VideoGrants(
                room_join=True,
                room="remote-macos-room",
            )).to_jwt()
        if not await livekit_handler.start("remote-macos-room", token):
            logger.warning("Failed to establish LiveKit connection.")
            livekit_handler = None

    server = Server("remote-macos-client")

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List available tools"""
        # Tool definitions remain the same
        return [
            types.Tool(
                name="remote_macos_get_screen",
                description="Connect to a remote MacOs machine and get a screenshot of the remote desktop. Uses environment variables for connection details.",
                inputSchema={
                    "type": "object",
                    "properties": {}
                },
            ),
            types.Tool(
                name="remote_macos_mouse_scroll",
                description="Perform a mouse scroll at specified coordinates on a remote MacOs machine, with automatic coordinate scaling. Uses environment variables for connection details.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer", "description": "X coordinate for mouse position (in source dimensions)"},
                        "y": {"type": "integer", "description": "Y coordinate for mouse position (in source dimensions)"},
                        "source_width": {"type": "integer", "description": "Width of the reference screen for coordinate scaling", "default": 1366},
                        "source_height": {"type": "integer", "description": "Height of the reference screen for coordinate scaling", "default": 768},
                        "direction": {
                            "type": "string",
                            "description": "Scroll direction",
                            "enum": ["up", "down"],
                            "default": "down"
                        }
                    },
                    "required": ["x", "y"]
                },
            ),
            types.Tool(
                name="remote_macos_send_keys",
                description="Send keyboard input to a remote MacOs machine. Uses environment variables for connection details.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text to send as keystrokes"},
                        "special_key": {"type": "string", "description": "Special key to send (e.g., 'enter', 'backspace', 'tab', 'escape', etc.)"},
                        "key_combination": {"type": "string", "description": "Key combination to send (e.g., 'ctrl+c', 'cmd+q', 'ctrl+alt+delete', etc.)"}
                    },
                    "required": []
                },
            ),
            types.Tool(
                name="remote_macos_mouse_move",
                description="Move the mouse cursor to specified coordinates on a remote MacOs machine, with automatic coordinate scaling. Uses environment variables for connection details.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer", "description": "X coordinate for mouse position (in source dimensions)"},
                        "y": {"type": "integer", "description": "Y coordinate for mouse position (in source dimensions)"},
                        "source_width": {"type": "integer", "description": "Width of the reference screen for coordinate scaling", "default": 1366},
                        "source_height": {"type": "integer", "description": "Height of the reference screen for coordinate scaling", "default": 768}
                    },
                    "required": ["x", "y"]
                },
            ),
            types.Tool(
                name="remote_macos_mouse_click",
                description="Perform a mouse click at specified coordinates on a remote MacOs machine, with automatic coordinate scaling. Uses environment variables for connection details.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer", "description": "X coordinate for mouse position (in source dimensions)"},
                        "y": {"type": "integer", "description": "Y coordinate for mouse position (in source dimensions)"},
                        "source_width": {"type": "integer", "description": "Width of the reference screen for coordinate scaling", "default": 1366},
                        "source_height": {"type": "integer", "description": "Height of the reference screen for coordinate scaling", "default": 768},
                        "button": {"type": "integer", "description": "Mouse button (1=left, 2=middle, 3=right)", "default": 1}
                    },
                    "required": ["x", "y"]
                },
            ),
            types.Tool(
                name="remote_macos_mouse_double_click",
                description="Perform a mouse double-click at specified coordinates on a remote MacOs machine, with automatic coordinate scaling. Uses environment variables for connection details.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer", "description": "X coordinate for mouse position (in source dimensions)"},
                        "y": {"type": "integer", "description": "Y coordinate for mouse position (in source dimensions)"},
                        "source_width": {"type": "integer", "description": "Width of the reference screen for coordinate scaling", "default": 1366},
                        "source_height": {"type": "integer", "description": "Height of the reference screen for coordinate scaling", "default": 768},
                        "button": {"type": "integer", "description": "Mouse button (1=left, 2=middle, 3=right)", "default": 1}
                    },
                    "required": ["x", "y"]
                },
            ),
            types.Tool(
                name="remote_macos_open_application",
                description="Opens/activates an application and returns its PID for further interactions.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "identifier": {
                            "type": "string",
                            "description": "REQUIRED. App name, path, or bundle ID."
                        }
                    },
                    "required": ["identifier"]
                },
            ),
            types.Tool(
                name="remote_macos_mouse_drag_n_drop",
                description="Perform a mouse drag operation from start point and drop to end point on a remote MacOs machine, with automatic coordinate scaling.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "start_x": {"type": "integer", "description": "Starting X coordinate (in source dimensions)"},
                        "start_y": {"type": "integer", "description": "Starting Y coordinate (in source dimensions)"},
                        "end_x": {"type": "integer", "description": "Ending X coordinate (in source dimensions)"},
                        "end_y": {"type": "integer", "description": "Ending Y coordinate (in source dimensions)"},
                        "source_width": {"type": "integer", "description": "Width of the reference screen for coordinate scaling", "default": 1366},
                        "source_height": {"type": "integer", "description": "Height of the reference screen for coordinate scaling", "default": 768},
                        "button": {"type": "integer", "description": "Mouse button (1=left, 2=middle, 3=right)", "default": 1},
                        "steps": {"type": "integer", "description": "Number of intermediate points for smooth dragging", "default": 10},
                        "delay_ms": {"type": "integer", "description": "Delay between steps in milliseconds", "default": 10}
                    },
                    "required": ["start_x", "start_y", "end_x", "end_y"]
                },
            ),
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle tool execution requests"""
        try:
            if not arguments:
                arguments = {}

            handler_map = {
                "remote_macos_get_screen": action_handlers.handle_remote_macos_get_screen,
                "remote_macos_mouse_scroll": action_handlers.handle_remote_macos_mouse_scroll,
                "remote_macos_send_keys": action_handlers.handle_remote_macos_send_keys,
                "remote_macos_mouse_move": action_handlers.handle_remote_macos_mouse_move,
                "remote_macos_mouse_click": action_handlers.handle_remote_macos_mouse_click,
                "remote_macos_mouse_double_click": action_handlers.handle_remote_macos_mouse_double_click,
                "remote_macos_open_application": action_handlers.handle_remote_macos_open_application,
                "remote_macos_mouse_drag_n_drop": action_handlers.handle_remote_macos_mouse_drag_n_drop,
            }

            if name in handler_map:
                # Note: asyncio.run is used for async handlers, direct call for sync
                if asyncio.iscoroutinefunction(handler_map[name]):
                    return await handler_map[name](arguments)
                else:
                    return handler_map[name](arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            logger.error(f"Error in handle_call_tool: {str(e)}", exc_info=True)
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info("Server running with stdio transport")
        try:
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="vnc-client",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
        finally:
            logger.info("Shutting down server and closing connections.")
            if vnc_client:
                vnc_client.close()
            if livekit_handler:
                await livekit_handler.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (ValueError, ConnectionError) as e:
        logger.error(f"Initialization failed: {str(e)}")
        print(f"ERROR: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        print(f"ERROR: Unexpected error occurred: {str(e)}")
        sys.exit(1)
