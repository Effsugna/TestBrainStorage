#!/bin/bash

# === Config ===
NGROK_URL="https://3b9e5fef67c1.ngrok-free.app"

# === Input Handling ===
FILE_PATH="$1"  # Path within the repo, like READMEs/MacBookTools.md
LOCAL_FILE="$2" # Local file to read content from (usually same as FILE_PATH)

if [ -z "$FILE_PATH" ] || [ -z "$LOCAL_FILE" ]; then
  echo "Usage: ./filepush.sh <repo-relative-path> <local-file-path>"
  echo "Example:"
  echo "  ./filepush.sh READMEs/MacBookTools.md READMEs/MacBookTools.md"
  exit 1
fi

if [ ! -f "$LOCAL_FILE" ]; then
  echo "File not found: $LOCAL_FILE"
  exit 1
fi

CONTENT=$(cat "$LOCAL_FILE")

# === Upload via cURL ===
curl -X POST ${NGROK_URL}/write \
  -H "Content-Type: application/json" \
  -d "$(jq -n \
    --arg path "$FILE_PATH" \
    --arg content "$CONTENT" \
    '{path: $path, content: $content}')"

