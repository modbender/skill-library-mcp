#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 /path/to/audio-file"
  exit 1
fi

AUDIO_PATH="$1"
URL="${PARAKEET_URL:-http://localhost:9001/v1/audio/transcriptions}"

if [ ! -f "$AUDIO_PATH" ]; then
  echo "Audio file not found: $AUDIO_PATH"
  exit 1
fi

curl -fsS -X POST "$URL" \
  -F "file=@$AUDIO_PATH" \
  -F "model=parakeet-tdt-0.6b-v3"
echo
