#!/bin/bash
# Usage: speak.sh "Text to speak" [voice] [output_file]
# Default voice: en-US-AriaNeural (female, American English)
# Output: /tmp/edge_tts_output.mp3

TEXT="$1"
VOICE="${2:-en-US-AriaNeural}"
OUTPUT="${3:-/tmp/edge_tts_output.mp3}"

if [ -z "$TEXT" ]; then
  echo "Usage: speak.sh \"Text to speak\" [voice] [output_file]"
  exit 1
fi

/root/.local/bin/edge-tts \
  --voice "$VOICE" \
  --text "$TEXT" \
  --write-media "$OUTPUT"

echo "$OUTPUT"
