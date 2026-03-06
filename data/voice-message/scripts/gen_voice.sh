#!/bin/bash
# Generate ogg/opus voice file from text using edge-tts + ffmpeg
# Usage: gen_voice.sh <text> <output.ogg> [voice]
# Default voice: zh-CN-XiaoxiaoNeural

set -e

TEXT="$1"
OUTPUT="$2"
VOICE="${3:-zh-CN-XiaoxiaoNeural}"

if [ -z "$TEXT" ] || [ -z "$OUTPUT" ]; then
  echo "Usage: gen_voice.sh <text> <output.ogg> [voice]"
  exit 1
fi

TMP_MP3=$(mktemp /tmp/voice_XXXXXX.mp3)
trap "rm -f $TMP_MP3" EXIT

edge-tts --voice "$VOICE" --text "$TEXT" --write-media "$TMP_MP3" 2>&1
ffmpeg -y -i "$TMP_MP3" -c:a libopus -b:a 64k "$OUTPUT" 2>&1 | tail -1

echo "Generated: $OUTPUT"
