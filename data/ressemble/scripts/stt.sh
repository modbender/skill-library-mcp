#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "" ]]; then
  echo "Usage: stt.sh <audio-file>"
  exit 1
fi

INPUT_AUDIO="$1"

if [[ ! -f "$INPUT_AUDIO" ]]; then
  echo "File not found: $INPUT_AUDIO"
  exit 1
fi

if [[ -z "${RESEMBLE_API_KEY:-}" ]]; then
  echo "Missing RESEMBLE_API_KEY"
  exit 1
fi

echo "🎤 Sending audio for transcription..."

RESPONSE=$(curl -s -X POST "https://app.resemble.ai/api/v2/speech-to-text" \
  -H "Authorization: Bearer $RESEMBLE_API_KEY" \
  -F "file=@${INPUT_AUDIO}")

JOB_ID=$(echo "$RESPONSE" | jq -r '.id')

if [[ "$JOB_ID" == "null" ]]; then
  echo "Failed to create STT job"
  echo "$RESPONSE"
  exit 1
fi

STATUS="processing"

while [[ "$STATUS" == "processing" ]]; do
  sleep 2
  STATUS=$(curl -s "https://app.resemble.ai/api/v2/speech-to-text/${JOB_ID}" \
    -H "Authorization: Bearer $RESEMBLE_API_KEY" | jq -r '.status')
done

if [[ "$STATUS" != "completed" ]]; then
  echo "Transcription failed"
  exit 1
fi

TRANSCRIPT=$(curl -s "https://app.resemble.ai/api/v2/speech-to-text/${JOB_ID}" \
  -H "Authorization: Bearer $RESEMBLE_API_KEY" | jq -r '.transcript')

echo "$TRANSCRIPT"
