#!/bin/bash
# Upload thumbnail for video

PUBLIC_KEY="$1"
SECRET_KEY="$2"
VIDEO_ID="$3"
THUMBNAIL_PATH="$4"

if [ -z "$PUBLIC_KEY" ] || [ -z "$SECRET_KEY" ] || [ -z "$VIDEO_ID" ] || [ -z "$THUMBNAIL_PATH" ]; then
  echo "Usage: $0 <public_key> <secret_key> <video_id> <thumbnail_path>"
  echo "Supported formats: .png, .jpg"
  exit 1
fi

if [ ! -f "$THUMBNAIL_PATH" ]; then
  echo "Error: Thumbnail file not found: $THUMBNAIL_PATH"
  exit 1
fi

curl -s -X POST "https://api-w3stream.attoaioz.cyou/api/videos/$VIDEO_ID/thumbnail" \
  -H 'accept: application/json' \
  -H 'stream-public-key: '"$PUBLIC_KEY" \
  -H 'stream-secret-key: '"$SECRET_KEY" \
  -F "file=@$THUMBNAIL_PATH"
