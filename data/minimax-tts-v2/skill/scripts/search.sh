#!/bin/bash
# MiniMax TTS Generation Script

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
TEXT="$1"

if [ ${#TEXT} -gt 1000 ]; then
    echo "Error: Text exceeds maximum length" >&2
    exit 1
fi

TEXT_JSON=$(jq -n --arg t "$TEXT" '$t')

PAYLOAD=$(jq -n \
    --argjson text "$TEXT_JSON" \
    '{
        model: "speech-02",
        text: $text,
        voice_setting: {"voice_id": "male-qingqiu"},
        speed: 1.0,
        vol: 1.0
    }')

RESULT=$(curl -s --proto =https --tlsv1.2 -m 60 -X POST "https://api.minimax.chat/v1/t2a_v2" \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

ERROR=$(echo "$RESULT" | jq -r '.error.message // empty' 2>/dev/null)
if [ -n "$ERROR" ]; then
    echo "API Error: $ERROR" >&2
    exit 1
fi

AUDIO_URL=$(echo "$RESULT" | jq -r '.data.audio // empty' 2>/dev/null)
if [ -n "$AUDIO_URL" ] && [ "$AUDIO_URL" != "null" ]; then
    echo "$AUDIO_URL"
else
    echo "Error: Failed to generate audio" >&2
    exit 1
fi
