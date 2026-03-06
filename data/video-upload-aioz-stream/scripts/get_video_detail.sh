#!/bin/bash
# Get video details from W3Stream API

PUBLIC_KEY="$1"
SECRET_KEY="$2"
VIDEO_ID="$3"

if [ -z "$PUBLIC_KEY" ] || [ -z "$SECRET_KEY" ] || [ -z "$VIDEO_ID" ]; then
  echo "Usage: $0 <public_key> <secret_key> <video_id>"
  exit 1
fi

curl -s "https://api-w3stream.attoaioz.cyou/api/videos/$VIDEO_ID" \
  -H 'accept: application/json' \
  -H 'stream-public-key: '"$PUBLIC_KEY" \
  -H 'stream-secret-key: '"$SECRET_KEY"
