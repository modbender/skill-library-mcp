#!/bin/bash
# MiniMax Video Generation Script

set -euo pipefail

if [ -z "${MINIMAX_API_KEY:-}" ]; then
    echo "Error: Required environment variable not set" >&2
    exit 1
fi

if [ $# -lt 1 ] || [ -z "$1" ]; then
    echo "Error: Missing required argument" >&2
    exit 1
fi

KEY="$MINIMAX_API_KEY"
PROMPT="$1"

if [ ${#PROMPT} -gt 500 ]; then
    echo "Error: Prompt exceeds maximum length" >&2
    exit 1
fi

PROMPT_JSON=$(jq -n --arg p "$PROMPT" '$p')

PAYLOAD=$(jq -n \
    --argjson prompt "$PROMPT_JSON" \
    '{
        model: "video-01",
        prompt: $prompt
    }')

RESULT=$(curl -s --proto =https --tlsv1.2 -m 120 -X POST "https://api.minimax.chat/v1/video_generation" \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

ERROR=$(echo "$RESULT" | jq -r '.error.message // empty' 2>/dev/null)
if [ -n "$ERROR" ]; then
    echo "API Error: $ERROR" >&2
    exit 1
fi

VIDEO_URL=$(echo "$RESULT" | jq -r '.data.video_url // empty' 2>/dev/null)
if [ -n "$VIDEO_URL" ] && [ "$VIDEO_URL" != "null" ]; then
    echo "$VIDEO_URL"
else
    echo "Error: Failed to generate video" >&2
    exit 1
fi
