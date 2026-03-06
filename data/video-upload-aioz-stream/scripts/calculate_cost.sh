#!/bin/bash
# Calculate transcode price for video

PUBLIC_KEY="$1"
SECRET_KEY="$2"
DURATION="$3"
QUALITIES="$4"

if [ -z "$PUBLIC_KEY" ] || [ -z "$SECRET_KEY" ] || [ -z "$DURATION" ] || [ -z "$QUALITIES" ]; then
  echo "Usage: $0 <public_key> <secret_key> <duration_seconds> <qualities>"
  echo "Example: $0 pk_xxx sk_xxx 60 '360p,720p,1080p'"
  exit 1
fi

# URL encode the qualities parameter
ENCODED_QUALITIES=$(echo "$QUALITIES" | sed 's/,/%2C/g')

curl -s "https://api-w3stream.attoaioz.cyou/api/videos/cost?duration=$DURATION&qualities=$ENCODED_QUALITIES" \
  -H 'accept: application/json' \
  -H 'stream-public-key: '"$PUBLIC_KEY" \
  -H 'stream-secret-key: '"$SECRET_KEY"
