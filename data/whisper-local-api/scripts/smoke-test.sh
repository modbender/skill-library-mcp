#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 /path/to/secure/audio-test-file.mp3"
  echo "Try using the included test-speech.mp3 from the root directory."
  exit 1
fi

AUDIO_PATH="$1"
URL="${WHISPER_API_URL:-http://localhost:9000/v1/audio/transcriptions}"

if [ ! -f "$AUDIO_PATH" ]; then
  echo "Audio file not found: $AUDIO_PATH"
  exit 1
fi

echo "Initiating private offline transcription... (no data sent to cloud)"
curl -fsS -X POST "$URL" \
  -H "Accept: application/json" \
  -F "file=@$AUDIO_PATH" \
  -F "model=large-v3-turbo"
echo
echo "Smoke test complete."
