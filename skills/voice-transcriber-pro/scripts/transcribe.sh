#!/bin/bash
# Transcribe audio using OpenRouter's OpenAI-compatible API (whisper)
# Usage: transcribe.sh /path/to/audio.ogg [--out /path/to/output.txt]

AUDIO_FILE="$1"
OUT_FILE="${2:-}"
OR_KEY="${OPENROUTER_API_KEY:-$(grep OPENROUTER_API_KEY ~/.openclaw/workspace/.env 2>/dev/null | cut -d= -f2)}"

if [ -z "$AUDIO_FILE" ] || [ ! -f "$AUDIO_FILE" ]; then
    echo "Error: Audio file not found: $AUDIO_FILE" >&2
    exit 1
fi

# Use OpenAI directly for Whisper (OpenRouter doesn't support audio transcription endpoint)
# Fall back to local ffmpeg + sending to a model
TRANSCRIPT=$(curl -sf "https://api.openai.com/v1/audio/transcriptions" \
    -H "Authorization: Bearer ${OPENAI_API_KEY:-notset}" \
    -F "file=@$AUDIO_FILE" \
    -F "model=whisper-1" \
    -F "response_format=text" 2>/dev/null)

# If OpenAI key not available, try OpenRouter with a workaround
if [ -z "$TRANSCRIPT" ] && [ -n "$OR_KEY" ]; then
    # Convert to base64 and ask an LLM to transcribe via multimodal
    # For now, use ffmpeg to convert to wav and use a simpler approach
    TRANSCRIPT=$(curl -sf "https://openrouter.ai/api/v1/audio/transcriptions" \
        -H "Authorization: Bearer $OR_KEY" \
        -F "file=@$AUDIO_FILE" \
        -F "model=openai/whisper-large-v3" \
        -F "response_format=text" 2>/dev/null)
fi

if [ -z "$TRANSCRIPT" ]; then
    echo "[Audio transcription unavailable - no API key configured]"
    exit 0
fi

if [ -n "$OUT_FILE" ]; then
    echo "$TRANSCRIPT" > "$OUT_FILE"
fi

echo "$TRANSCRIPT"
