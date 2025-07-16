#!/bin/bash

while true; do
  # 1. Take a screenshot and OCR the text
  TEXT=$(screencapture -x - | tesseract stdin stdout)

  # 2. Send to Gemini and get a cliclick command
  COMMAND=$(echo "$TEXT" | gemini ask --multiline --no-stream "You are a computer agent. Based on this screen content, output a single cliclick command to control mouse or keyboard. Output only the command.")

  # 3. Show and run the command
  echo "Gemini says: $COMMAND"
  eval "$COMMAND"

  # 4. Wait a bit before next loop
  sleep 10
done

