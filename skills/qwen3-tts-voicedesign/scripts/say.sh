#!/usr/bin/env bash
# Quick TTS: generate speech from text
#
# Server defaults are authoritative (seed + instruct are baked in).
# Only override TTS_URL if pointing to a different server.
#
# Environment variables (all optional):
#   TTS_URL       Server base URL (default: http://localhost:8881)
#   TTS_FORMAT    Output format: mp3/wav (default: mp3)
#
# Usage:
#   say.sh "你好呀！"                    → plays audio (macOS) or saves to /tmp
#   say.sh "你好呀！" output.mp3         → saves to output.mp3
#   say.sh -                             → read text from stdin

set -euo pipefail

TTS_URL="${TTS_URL:-http://localhost:8881}"
TTS_FORMAT="${TTS_FORMAT:-mp3}"

# Parse args
TEXT="${1:-}"
OUTPUT="${2:-}"

if [[ "$TEXT" == "-" ]]; then
    TEXT=$(cat)
elif [[ -z "$TEXT" ]]; then
    echo "Usage: say.sh <text> [output_file]" >&2
    echo "  or:  echo 'text' | say.sh -" >&2
    exit 1
fi

# Build JSON body — only text and format, let server handle seed+instruct
BODY=$(python3 -c "import json,sys; print(json.dumps({'text': sys.argv[1], 'format': '$TTS_FORMAT'}))" "$TEXT")

# Generate
if [[ -z "$OUTPUT" ]]; then
    OUTPUT="/tmp/tts_$(date +%s).${TTS_FORMAT}"
    AUTO_PLAY=1
else
    AUTO_PLAY=0
fi

curl -s -o "$OUTPUT" \
    -X POST "${TTS_URL}/tts" \
    -H "Content-Type: application/json" \
    -d "$BODY"

size=$(stat -f%z "$OUTPUT" 2>/dev/null || stat -c%s "$OUTPUT" 2>/dev/null || echo "?")
echo "$OUTPUT (${size}B)"

# Auto-play on macOS
if [[ "$AUTO_PLAY" == "1" ]] && command -v afplay &>/dev/null; then
    afplay "$OUTPUT" &
fi
