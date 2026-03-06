#!/bin/bash

# Free Groq Voice Transcription Script
# Usage: ./transcribe.sh <audio-file> [language]

AUDIO_FILE="$1"
LANGUAGE="${2:-zh}"
PROXY="${GROQ_PROXY:-http://127.0.0.1:7890}"

if [ -z "$GROQ_API_KEY" ]; then
    echo "Error: GROQ_API_KEY not set"
    echo "Get your FREE API key at https://console.groq.com/"
    exit 1
fi

if [ -z "$AUDIO_FILE" ]; then
    echo "Usage: $0 <audio-file> [language]"
    echo "Example: $0 voice.ogg zh"
    exit 1
fi

if [ ! -f "$AUDIO_FILE" ]; then
    echo "Error: File not found: $AUDIO_FILE"
    exit 1
fi

# Transcribe using Groq's FREE Whisper API
curl -s --proxy "$PROXY" \
    "https://api.groq.com/openai/v1/audio/transcriptions" \
    -H "Authorization: Bearer $GROQ_API_KEY" \
    -H "Content-Type: multipart/form-data" \
    -F "file=@$AUDIO_FILE" \
    -F "model=whisper-large-v3" \
    -F "language=$LANGUAGE" | jq -r '.text'
