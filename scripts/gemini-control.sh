#!/bin/bash

# This script requires the OPENAI_API_KEY environment variable to be set.
# export OPENAI_API_KEY='your_key_here'

while true; do
  TEXT=$(screencapture -x - | tesseract stdin stdout)
  RESPONSE=$(curl -s -X POST https://api.openai.com/v1/chat/completions \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
      "model": "gpt-4",
      "messages": [{"role": "user", "content": "'"$TEXT"'"}]
    }' | jq -r '.choices[0].message.content')

  echo "$RESPONSE" | say
  echo "$RESPONSE" | pbcopy
  echo "$RESPONSE"
done

