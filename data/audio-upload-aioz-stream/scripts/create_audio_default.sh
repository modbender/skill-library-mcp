#!/bin/bash
# Create audio with default configuration
# Usage: ./create_audio_default.sh "PUBLIC_KEY" "SECRET_KEY" "Audio Title"

PUBLIC_KEY="$1"
SECRET_KEY="$2"
TITLE="$3"

if [ -z "$PUBLIC_KEY" ] || [ -z "$SECRET_KEY" ] || [ -z "$TITLE" ]; then
    echo "Usage: $0 PUBLIC_KEY SECRET_KEY TITLE"
    exit 1
fi

curl -s -X POST 'https://api-w3stream.attoaioz.cyou/api/videos/create' \
  -H "stream-public-key: $PUBLIC_KEY" \
  -H "stream-secret-key: $SECRET_KEY" \
  -H 'Content-Type: application/json' \
  -d "{
    \"title\": \"$TITLE\",
    \"type\": \"audio\"
  }"
