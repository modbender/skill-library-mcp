#!/bin/bash
# Pollinations Audio Transcription
# Usage: ./transcribe.sh "audio_file_or_url" [--prompt "transcribe this"] [--model gemini]

set -e

AUDIO_INPUT="$1"
shift || true

# Defaults
PROMPT="${PROMPT:-Transcribe this audio accurately. Return only the transcription text, nothing else.}"
MODEL="${MODEL:-gemini}"

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --prompt)
      PROMPT="$2"
      shift 2
      ;;
    --model)
      MODEL="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

if [[ -z "$AUDIO_INPUT" ]]; then
  echo "Usage: transcribe.sh <audio_file_or_url> [--prompt \"...\"] [--model gemini]"
  echo "Models: gemini, gemini-large, gemini-legacy, openai-audio"
  echo "Formats: MP3, WAV, FLAC, OGG, M4A"
  exit 1
fi

# Temp files for large data
BODY_FILE=$(mktemp /tmp/transcribe_body_XXXXXX.json)
B64_FILE=$(mktemp /tmp/transcribe_b64_XXXXXX)
trap "rm -f '$BODY_FILE' '$B64_FILE'" EXIT

# Determine audio format
detect_format() {
  case "$1" in
    *.wav) echo "wav" ;;
    *.flac) echo "flac" ;;
    *.ogg) echo "ogg" ;;
    *.m4a) echo "m4a" ;;
    *) echo "mp3" ;;
  esac
}

if [[ -f "$AUDIO_INPUT" ]]; then
  FORMAT=$(detect_format "$AUDIO_INPUT")
  base64 -w0 "$AUDIO_INPUT" > "$B64_FILE"
else
  # URL: download first
  echo "Downloading audio..."
  TEMP_AUDIO=$(mktemp /tmp/audio_dl_XXXXXX)
  trap "rm -f '$BODY_FILE' '$B64_FILE' '$TEMP_AUDIO'" EXIT
  curl -s -o "$TEMP_AUDIO" "$AUDIO_INPUT"
  FORMAT=$(detect_format "$AUDIO_INPUT")
  base64 -w0 "$TEMP_AUDIO" > "$B64_FILE"
fi

# Build JSON using jq with file input to avoid shell arg limits
jq -n -c --rawfile b64data "$B64_FILE" \
  --arg model "$MODEL" \
  --arg prompt "$PROMPT" \
  --arg format "$FORMAT" \
  '{
    model: $model,
    messages: [{
      role: "user",
      content: [
        {type: "text", text: $prompt},
        {type: "input_audio", input_audio: {data: ($b64data | rtrimstr("\n")), format: $format}}
      ]
    }]
  }' > "$BODY_FILE"

# Make request
echo "Transcribing audio with $MODEL..."

RESPONSE=$(curl -s --max-time 300 -H "Content-Type: application/json" \
  ${POLLINATIONS_API_KEY:+-H "Authorization: Bearer $POLLINATIONS_API_KEY"} \
  -X POST "https://gen.pollinations.ai/v1/chat/completions" \
  -d @"$BODY_FILE")

# Extract result
RESULT=$(echo "$RESPONSE" | jq -r '.choices[0].message.content // empty')

if [[ -n "$RESULT" ]]; then
  echo "$RESULT"
else
  echo "Error: Failed to transcribe audio"
  echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE"
  exit 1
fi
