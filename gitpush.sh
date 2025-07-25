#!/bin/bash

# === Config ===
NGROK_URL="https://e6968da8a58f.ngrok-free.app"

# === Input Handling ===
FILE_PATH="$1"
SOURCE="$2"

if [ -z "$FILE_PATH" ] || [ -z "$SOURCE" ]; then
  echo "Usage: ./gitpush.sh <repo-relative-path> <content|@filepath>"
  echo "Examples:"
  echo "  ./gitpush.sh testfiles/notes/hello.txt \"This is a direct message\""
  echo "  ./gitpush.sh memory/summary/data.json @localfile.json"
  exit 1
fi

# === Content Handling ===
if [[ "$SOURCE" == @* ]]; then
  FILE_TO_READ="${SOURCE:1}"
  if [ ! -f "$FILE_TO_READ" ]; then
    echo "File not found: $FILE_TO_READ"
    exit 1
  fi
  CONTENT=$(cat "$FILE_TO_READ")
else
  CONTENT="$SOURCE"
fi

# === Upload via cURL ===
curl -X POST ${NGROK_URL}/write \
  -H "Content-Type: application/json" \
  -d "$(jq -n \
    --arg path "$FILE_PATH" \
    --arg content "$CONTENT" \
    '{path: $path, content: $content}')"

