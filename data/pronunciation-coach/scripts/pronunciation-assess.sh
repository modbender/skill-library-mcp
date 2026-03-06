#!/bin/bash
# Azure Speech Pronunciation Assessment
# Usage: pronunciation-assess.sh <audio_file> <reference_text> [azure_key] [azure_region]
#
# Accepts any audio format (auto-converts to WAV 16kHz mono via ffmpeg).
# Returns raw JSON from Azure Speech pronunciation assessment API.

AUDIO_FILE="$1"
REFERENCE_TEXT="$2"
AZURE_KEY="${3:-$AZURE_SPEECH_KEY}"
AZURE_REGION="${4:-$AZURE_SPEECH_REGION}"

# Basic usage check
if [ -z "$AUDIO_FILE" ] || [ -z "$REFERENCE_TEXT" ]; then
    echo "Usage: $0 <audio_file> <reference_text> [azure_key] [azure_region]"
    exit 1
fi

# Credential check
if [ -z "$AZURE_KEY" ] || [ -z "$AZURE_REGION" ]; then
    echo "Error: Azure Speech key/region required. Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION env vars, or pass as args 3 and 4."
    exit 1
fi

# Safety check for file existence and to prevent option injection
if [ ! -f "$AUDIO_FILE" ]; then
    echo "Error: Audio file not found: $AUDIO_FILE"
    exit 1
fi

case "$AUDIO_FILE" in
    -*)
        echo "Error: Malicious filename detected."
        exit 1
        ;;
esac

ENDPOINT="https://${AZURE_REGION}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"

# Create a temporary file for the conversion
TEMP_WAV=$(mktemp /tmp/pronXXXXXX.wav)
CLEANUP_WAV=1

# Convert to required format: WAV 16kHz 16-bit PCM mono
# Using -- to ensure the filename is treated as a path even if it looks like an option
if ! ffmpeg -y -i -- "$AUDIO_FILE" -ar 16000 -ac 1 -acodec pcm_s16le "$TEMP_WAV" > /dev/null 2>&1; then
    echo "Error: Audio conversion failed."
    rm -f "$TEMP_WAV"
    exit 1
fi

CONTENT_TYPE="audio/wav; codecs=audio/pcm; samplerate=16000"

# Safely escape quotes and backslashes for JSON in REFERENCE_TEXT
SAFE_TEXT=$(echo -n "$REFERENCE_TEXT" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | tr -d '\n')

# Build pronunciation assessment config (Base64-encoded JSON)
PRON_CONFIG=$(echo -n "{
  \"ReferenceText\": \"${SAFE_TEXT}\",
  \"GradingSystem\": \"HundredMark\",
  \"Granularity\": \"Phoneme\",
  \"Dimension\": \"Comprehensive\",
  \"EnableMiscue\": true,
  \"EnableProsodyAssessment\": true
}" | base64 | tr -d '\n')

# API call using --data-binary to point to the temporary file
RESULT=$(curl -s -X POST \
    "${ENDPOINT}?language=en-US&format=detailed" \
    -H "Ocp-Apim-Subscription-Key: ${AZURE_KEY}" \
    -H "Content-Type: ${CONTENT_TYPE}" \
    -H "Pronunciation-Assessment: ${PRON_CONFIG}" \
    -H "Accept: application/json" \
    --data-binary "@${TEMP_WAV}")

# Cleanup
if [ "$CLEANUP_WAV" = "1" ] && [ -f "$TEMP_WAV" ]; then
    rm -f "$TEMP_WAV"
fi

echo "$RESULT"
