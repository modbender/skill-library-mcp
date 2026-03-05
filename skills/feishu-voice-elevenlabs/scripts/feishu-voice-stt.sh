#!/usr/bin/env bash
# feishu-voice-stt.sh — Transcribe an audio file using ElevenLabs Speech-to-Text
# Usage: feishu-voice-stt.sh <audio_file>
#
# Required env:
#   ELEVENLABS_API_KEY — ElevenLabs API key

set -euo pipefail

AUDIO_FILE="${1:?Usage: feishu-voice-stt.sh <audio_file>}"

: "${ELEVENLABS_API_KEY:?Set ELEVENLABS_API_KEY}"

[ ! -f "$AUDIO_FILE" ] && echo "ERROR: File not found: $AUDIO_FILE" >&2 && exit 1

RESULT=$(curl -sf "https://api.elevenlabs.io/v1/speech-to-text" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -F "model_id=scribe_v1" \
  -F "file=@$AUDIO_FILE")

echo "$RESULT" | python3 -c "
import sys,json
d=json.load(sys.stdin)
text=d.get('text','')
if text:
    print(text)
else:
    print('ERROR: No text recognized')
    sys.exit(1)
"
