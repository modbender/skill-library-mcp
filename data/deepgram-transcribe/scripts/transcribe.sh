#!/usr/bin/env bash
# Transcribe audio using Deepgram Nova-3 API
# Usage: transcribe.sh /path/to/audio.mp3 [--model nova-3] [--out /path/to/output.txt] [--language en] [--json]
set -euo pipefail

AUDIO_FILE=""
MODEL="nova-3"
OUT_FILE=""
LANGUAGE="en"
JSON_OUTPUT=false
API_KEY="${DEEPGRAM_API_KEY:-}"

while [[ $# -gt 0 ]]; do
  case $1 in
    --model) MODEL="$2"; shift 2 ;;
    --out) OUT_FILE="$2"; shift 2 ;;
    --language) LANGUAGE="$2"; shift 2 ;;
    --json) JSON_OUTPUT=true; shift ;;
    --api-key) API_KEY="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: transcribe.sh <audio-file> [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --model MODEL      Deepgram model (default: nova-3)"
      echo "  --out FILE         Output file (default: <input>.txt)"
      echo "  --language LANG    Language code (default: en)"
      echo "  --json             Output full JSON response"
      echo "  --api-key KEY      Deepgram API key (overrides DEEPGRAM_API_KEY)"
      echo ""
      echo "Models: nova-3 (best), nova-2, enhanced, base, whisper-large"
      exit 0
      ;;
    *) AUDIO_FILE="$1"; shift ;;
  esac
done

if [[ -z "$AUDIO_FILE" ]]; then
  echo "Error: No audio file specified" >&2
  echo "Usage: transcribe.sh <audio-file> [--model nova-3] [--out output.txt]" >&2
  exit 1
fi

if [[ ! -f "$AUDIO_FILE" ]]; then
  echo "Error: File not found: $AUDIO_FILE" >&2
  exit 1
fi

if [[ -z "$API_KEY" ]]; then
  # Try reading from secrets
  if [[ -f ~/.openclaw/secrets/deepgram-api-key.txt ]]; then
    API_KEY=$(cat ~/.openclaw/secrets/deepgram-api-key.txt)
  else
    echo "Error: No API key. Set DEEPGRAM_API_KEY or pass --api-key" >&2
    exit 1
  fi
fi

if [[ -z "$OUT_FILE" ]]; then
  OUT_FILE="${AUDIO_FILE%.*}.txt"
fi

# Detect content type
EXT="${AUDIO_FILE##*.}"
case "$EXT" in
  mp3) CONTENT_TYPE="audio/mpeg" ;;
  wav) CONTENT_TYPE="audio/wav" ;;
  m4a) CONTENT_TYPE="audio/mp4" ;;
  ogg) CONTENT_TYPE="audio/ogg" ;;
  flac) CONTENT_TYPE="audio/flac" ;;
  webm) CONTENT_TYPE="audio/webm" ;;
  aiff|aif) CONTENT_TYPE="audio/aiff" ;;
  *) CONTENT_TYPE="audio/mpeg" ;;
esac

echo "Transcribing: $AUDIO_FILE"
echo "Model: $MODEL | Language: $LANGUAGE"

PARAMS="model=${MODEL}&language=${LANGUAGE}&smart_format=true&paragraphs=true&punctuate=true&diarize=true"

RESPONSE=$(curl -s -X POST "https://api.deepgram.com/v1/listen?${PARAMS}" \
  -H "Authorization: Token ${API_KEY}" \
  -H "Content-Type: ${CONTENT_TYPE}" \
  --data-binary @"$AUDIO_FILE")

# Check for errors
ERROR=$(echo "$RESPONSE" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('err_msg',''))" 2>/dev/null || echo "")
if [[ -n "$ERROR" ]]; then
  echo "Error: $ERROR" >&2
  exit 1
fi

if [[ "$JSON_OUTPUT" == "true" ]]; then
  echo "$RESPONSE" > "$OUT_FILE"
  echo "Full JSON saved to: $OUT_FILE"
else
  # Extract transcript
  TRANSCRIPT=$(echo "$RESPONSE" | python3 -c "
import json, sys
d = json.load(sys.stdin)
channels = d.get('results', {}).get('channels', [])
if channels:
    paragraphs = channels[0].get('alternatives', [{}])[0].get('paragraphs', {}).get('paragraphs', [])
    if paragraphs:
        for p in paragraphs:
            for s in p.get('sentences', []):
                speaker = s.get('speaker', 0)
                text = s.get('text', '')
                print(f'[Speaker {speaker}] {text}')
    else:
        print(channels[0]['alternatives'][0]['transcript'])
")
  echo "$TRANSCRIPT" > "$OUT_FILE"
  echo ""
  echo "$TRANSCRIPT"
  echo ""
  echo "Saved to: $OUT_FILE"
fi

# Print metadata
python3 -c "
import json, sys
d = json.loads('''$RESPONSE''')
meta = d.get('metadata', {})
dur = meta.get('duration', 0)
conf = d.get('results',{}).get('channels',[{}])[0].get('alternatives',[{}])[0].get('confidence', 0)
print(f'Duration: {dur:.1f}s | Confidence: {conf:.4f} | Model: ${MODEL}')
" 2>/dev/null || true
