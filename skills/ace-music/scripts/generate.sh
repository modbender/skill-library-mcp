#!/usr/bin/env bash
# ACE-Step Music Generation via API
# Usage: generate.sh <prompt> [options]
# Options: --lyrics "..." --duration 30 --language en --instrumental --output file.mp3
#          --bpm 120 --key "C major" --seed 42 --sample-mode --batch 2

set -euo pipefail

# Config
API_KEY="${ACE_MUSIC_API_KEY:-}"
BASE_URL="${ACE_MUSIC_BASE_URL:-https://api.acemusic.ai}"
OUTPUT="output_$(date +%s).mp3"

# Defaults
DURATION=""
LANGUAGE="en"
INSTRUMENTAL="null"
BPM=""
KEY_SCALE=""
SEED=""
SAMPLE_MODE="false"
BATCH_SIZE=1
LYRICS=""
PROMPT=""
FORMAT="mp3"

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --lyrics) LYRICS="$2"; shift 2 ;;
    --duration) DURATION="$2"; shift 2 ;;
    --language) LANGUAGE="$2"; shift 2 ;;
    --instrumental) INSTRUMENTAL="true"; shift ;;
    --output|-o) OUTPUT="$2"; shift 2 ;;
    --bpm) BPM="$2"; shift 2 ;;
    --key) KEY_SCALE="$2"; shift 2 ;;
    --seed) SEED="$2"; shift 2 ;;
    --sample-mode) SAMPLE_MODE="true"; shift ;;
    --batch) BATCH_SIZE="$2"; shift 2 ;;
    --format) FORMAT="$2"; shift 2 ;;
    *) PROMPT="$1"; shift ;;
  esac
done

if [[ -z "$API_KEY" ]]; then
  echo "ERROR: ACE_MUSIC_API_KEY not set." >&2
  echo "Get your free API key at: https://acemusic.ai/playground/api-key" >&2
  exit 1
fi

if [[ -z "$PROMPT" && "$SAMPLE_MODE" == "false" ]]; then
  echo "Usage: generate.sh <prompt> [--lyrics '...'] [--duration 30] [--language en] [--instrumental] [--output file.mp3]" >&2
  exit 1
fi

# Build audio_config
AUDIO_CONFIG="{\"vocal_language\":\"$LANGUAGE\",\"format\":\"$FORMAT\""
[[ -n "$DURATION" ]] && AUDIO_CONFIG="$AUDIO_CONFIG,\"duration\":$DURATION"
[[ -n "$BPM" ]] && AUDIO_CONFIG="$AUDIO_CONFIG,\"bpm\":$BPM"
[[ "$INSTRUMENTAL" != "null" ]] && AUDIO_CONFIG="$AUDIO_CONFIG,\"instrumental\":$INSTRUMENTAL"
[[ -n "$KEY_SCALE" ]] && AUDIO_CONFIG="$AUDIO_CONFIG,\"key_scale\":\"$KEY_SCALE\""
AUDIO_CONFIG="$AUDIO_CONFIG}"

# Build message content
if [[ -n "$LYRICS" && -n "$PROMPT" ]]; then
  # Tagged mode
  CONTENT="<prompt>${PROMPT}</prompt>\n<lyrics>${LYRICS}</lyrics>"
elif [[ -n "$LYRICS" ]]; then
  CONTENT="$LYRICS"
else
  CONTENT="$PROMPT"
fi

# Escape for JSON
CONTENT_ESCAPED=$(echo -n "$CONTENT" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))" | sed 's/^"//;s/"$//')

# Build request body
BODY="{\"messages\":[{\"role\":\"user\",\"content\":\"$CONTENT_ESCAPED\"}],\"audio_config\":$AUDIO_CONFIG,\"stream\":false"
[[ -n "$LYRICS" && -n "$PROMPT" ]] || true  # tagged mode handled via content
[[ "$SAMPLE_MODE" == "true" ]] && BODY="$BODY,\"sample_mode\":true"
[[ -n "$SEED" ]] && BODY="$BODY,\"seed\":$SEED"
[[ "$BATCH_SIZE" -gt 1 ]] && BODY="$BODY,\"batch_size\":$BATCH_SIZE"
BODY="$BODY}"

echo "🎵 Generating music..." >&2
echo "   Prompt: ${PROMPT:-[lyrics/sample mode]}" >&2
[[ -n "$DURATION" ]] && echo "   Duration: ${DURATION}s" >&2
echo "   Language: $LANGUAGE" >&2

# API call
RESPONSE=$(curl -s -X POST "${BASE_URL}/v1/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "$BODY")

# Check for errors
if echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if 'choices' in d else 1)" 2>/dev/null; then
  # Extract metadata
  METADATA=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['choices'][0]['message'].get('content',''))" 2>/dev/null || echo "")
  
  # Extract and save audio(s)
  COUNT=$(echo "$RESPONSE" | python3 -c "
import sys,json
d=json.load(sys.stdin)
audios=d['choices'][0]['message'].get('audio',[])
print(len(audios))
" 2>/dev/null || echo "0")

  if [[ "$COUNT" -eq 0 ]]; then
    echo "ERROR: No audio in response" >&2
    echo "$RESPONSE" >&2
    exit 1
  fi

  echo "$RESPONSE" | python3 -c "
import sys, json, base64
d = json.load(sys.stdin)
audios = d['choices'][0]['message'].get('audio', [])
output = '$OUTPUT'
for i, a in enumerate(audios):
    url = a['audio_url']['url']
    b64 = url.split(',', 1)[1]
    fname = output if len(audios) == 1 else output.rsplit('.', 1)[0] + f'_{i+1}.' + output.rsplit('.', 1)[1]
    with open(fname, 'wb') as f:
        f.write(base64.b64decode(b64))
    print(f'Saved: {fname}', file=sys.stderr)
    print(fname)
"

  if [[ -n "$METADATA" ]]; then
    echo "" >&2
    echo "📋 Metadata:" >&2
    echo "$METADATA" >&2
  fi
else
  echo "ERROR: API request failed" >&2
  echo "$RESPONSE" >&2
  exit 1
fi
