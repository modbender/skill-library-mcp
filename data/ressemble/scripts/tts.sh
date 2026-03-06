#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "" ]]; then
  echo "Usage: tts.sh \"text\" [VOICE_UUID]"
  exit 1
fi

TEXT="$1"
VOICE_UUID="${2:-01aa67f7}"
OUTPUT_FILE="/tmp/resemble_$(date +%s).mp3"

if [[ -z "${RESEMBLE_API_KEY:-}" ]]; then
  echo "Missing RESEMBLE_API_KEY"
  exit 1
fi

echo "🔊 Generating speech..."

RESPONSE=$(curl -s -X POST "https://f.cluster.resemble.ai/synthesize" \
  -H "Authorization: Bearer $RESEMBLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"voice_uuid\": \"$VOICE_UUID\",
    \"data\": \"$TEXT\",
    \"output_format\": \"mp3\"
  }")

SUCCESS=$(echo "$RESPONSE" | jq -r '.success')

if [[ "$SUCCESS" != "true" ]]; then
  echo "TTS failed:"
  echo "$RESPONSE"
  exit 1
fi

echo "$RESPONSE" | jq -r '.audio_content' | base64 -d > "$OUTPUT_FILE"

echo "MEDIA:$OUTPUT_FILE"
