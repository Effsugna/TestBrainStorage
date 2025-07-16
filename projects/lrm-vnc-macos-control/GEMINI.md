LRM VNC macOS Control — GEMINI.md

Project Goal

Enable real-time visual control and automation of a macOS desktop environment using local screen capture and simulated input, structured as a Flask-based server with callable endpoints. The long-term intent is to allow a Gemini agent (or other LLM) to observe screen content, decide on actions, and execute them on the user’s machine via vision + control endpoints. This system is intended to eventually support stable 30fps screen access with low-latency decision making, enabling the agent to complete complex interactive tasks — including playing games or navigating dynamic UIs — with speed and precision.

Agent Role

Gemini (or another assistant agent) will act as the remote controller, making decisions based on screen data and responding via HTTP API to take action (click, type, move, etc.). It should:

    Observe the current screen via /capture

    Decide what needs to be clicked or typed

    Send actions via /act

Current API Endpoints

GET /capture

    Captures the current screen using Quartz.CGDisplayCreateImage

    Converts image to JPEG

    Base64 encodes it for JSON transport

    Returns:
    {
    "image_base64": "<base64string>"
    }

POST /act

    Accepts JSON actions for mouse or keyboard control

    Currently supports:

        move → move mouse to x, y

        click → click at x, y

        type → type string (in development)

    Example:
    {
    "action": "click",
    "x": 400,
    "y": 300
    }

File Structure

lrm-vnc-macos-control/
├── server.py # Flask server, API entrypoints
├── screen.py # Quartz-based screen capture
├── control.py # macOS mouse/keyboard simulation
├── ocr.py # Optional: Tesseract or EasyOCR
├── vision.py # Object detection or future spatial planning
├── test_run.py # Manual local testing script
├── GEMINI.md # Project brief (this file)

Immediate Tasks

    Server captures and responds on /capture

    Mouse move and click via /act

    Add type string functionality

    Improve security (auth, HTTPS)

    Optimize performance for frequent calls

    Optional: add /video_feed or WebSocket

Long-Term Vision

This is not a VNC server. This project creates a structured control layer for intelligent agents to operate on top of macOS via a simplified remote interface. It trades protocol fidelity for agent compatibility, and focuses on:

    Integrating with Gemini or future model inference loops

    Allowing high-context vision-driven feedback

    Remaining human-readable and modular for experimentation

    Achieving a stable 30fps capture/response loop

    Supporting fast reaction time to visual state for high-speed or game-like interactions

Notes

    macOS accessibility permissions must be enabled for full mouse/keyboard control

    Flask is exposed locally; remote relay (via ngrok) must be secured in production

    GitHub push handled manually via local relay to prevent secrets exposure