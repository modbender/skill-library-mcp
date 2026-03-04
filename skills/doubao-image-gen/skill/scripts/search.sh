#!/bin/bash
# Doubao Image Generation Script

set -euo pipefail

if [ -z "${DOUBAO_API_KEY:-}" ]; then
    echo "Error: Required environment variable not set" >&2
    exit 1
fi

if [ $# -lt 1 ] || [ -z "$1" ]; then
    echo "Error: Missing required argument" >&2
    exit 1
fi

KEY="$DOUBAO_API_KEY"
PROMPT="$1"

if [ ${#PROMPT} -gt 500 ]; then
    echo "Error: Prompt exceeds maximum length" >&2
    exit 1
fi

PROMPT_JSON=$(jq -n --arg p "$PROMPT" '$p')

PAYLOAD=$(jq -n \
    --argjson prompt "$PROMPT_JSON" \
    '{
        model: "doubao-image-v1",
        prompt: $prompt
    }')

RESULT=$(curl -s --proto =https --tlsv1.2 -m 60 -X POST "https://ark.cn-beijing.volces.com/api/v3/images/generations" \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

ERROR=$(echo "$RESULT" | jq -r '.error.message // empty' 2>/dev/null)
if [ -n "$ERROR" ]; then
    echo "API Error: $ERROR" >&2
    exit 1
fi

IMAGE_URL=$(echo "$RESULT" | jq -r '.data[0].url // empty' 2>/dev/null)
if [ -n "$IMAGE_URL" ] && [ "$IMAGE_URL" != "null" ]; then
    echo "$IMAGE_URL"
else
    echo "Error: Failed to generate image" >&2
    exit 1
fi
