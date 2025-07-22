#!/bin/bash

# === Config ===
NGROK_URL="https://558edbc7dea5.ngrok-free.app"

# === Default log folder ===
DEFAULT_DIR="testfiles/logs"
ALT_DIR="memory/V conversation log summaries"

# === Input handling ===
MESSAGE="$1"
TARGET="$2"

if [ -z "$MESSAGE" ]; then
  echo "Usage: ./logpush.sh \"Your log message here\" [folder-key]"
  echo "Folder key options: logs (default), summary"
  exit 1
fi

# === Path handling ===
if [ "$TARGET" == "summary" ]; then
  LOG_DIR="$ALT_DIR"
else
  LOG_DIR="$DEFAULT_DIR"
fi

# === Timestamping ===
NOW=$(date +"%Y-%m-%d-%H%M")
HUMAN_TIME=$(date +"%Y-%m-%d – %H:%M")
FILENAME="log-${NOW}.md"
FULL_PATH="${LOG_DIR}/${FILENAME}"

# === Format message ===
LOG_CONTENT=$(cat <<EOF
# Log – ${HUMAN_TIME}

$MESSAGE
EOF
)

# === cURL Push ===
curl -X POST ${NGROK_URL}/write \
  -H "Content-Type: application/json" \
  -d "$(jq -n \
    --arg path "$FULL_PATH" \
    --arg content "$LOG_CONTENT" \
    '{path: $path, content: $content}')"
