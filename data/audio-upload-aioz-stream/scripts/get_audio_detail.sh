#!/bin/bash
# Get audio details and streaming URL
# Usage: ./get_audio_detail.sh PUBLIC_KEY SECRET_KEY AUDIO_ID

PUBLIC_KEY="$1"
SECRET_KEY="$2"
AUDIO_ID="$3"

if [ -z "$PUBLIC_KEY" ] || [ -z "$SECRET_KEY" ] || [ -z "$AUDIO_ID" ]; then
    echo "Usage: $0 PUBLIC_KEY SECRET_KEY AUDIO_ID"
    exit 1
fi

curl -s "https://api-w3stream.attoaioz.cyou/api/videos/$AUDIO_ID" \
  -H "stream-public-key: $PUBLIC_KEY" \
  -H "stream-secret-key: $SECRET_KEY"
