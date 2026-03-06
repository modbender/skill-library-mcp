#!/bin/bash
# Create video object with custom encoding configuration

PUBLIC_KEY="$1"
SECRET_KEY="$2"
TITLE="$3"

if [ -z "$PUBLIC_KEY" ] || [ -z "$SECRET_KEY" ] || [ -z "$TITLE" ]; then
  echo "Usage: $0 <public_key> <secret_key> <title>"
  exit 1
fi

# Example: 720p and 1080p with h264 codec
curl -s -X POST 'https://api-w3stream.attoaioz.cyou/api/videos/create' \
  -H 'stream-public-key: '"$PUBLIC_KEY" \
  -H 'stream-secret-key: '"$SECRET_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "'"$TITLE"'",
    "is_public": true,
    "qualities": [
      {
        "resolution": "1080p",
        "type": "hls",
        "container_type": "mpegts",
        "video_config": {
          "codec": "h264",
          "bitrate": 5000000,
          "index": 0
        },
        "audio_config": {
          "codec": "aac",
          "bitrate": 192000,
          "channels": "2",
          "sample_rate": 48000,
          "language": "en",
          "index": 0
        }
      },
      {
        "resolution": "720p",
        "type": "hls",
        "container_type": "mpegts",
        "video_config": {
          "codec": "h264",
          "bitrate": 3000000,
          "index": 0
        },
        "audio_config": {
          "codec": "aac",
          "bitrate": 128000,
          "channels": "2",
          "sample_rate": 44100,
          "language": "en",
          "index": 0
        }
      }
    ]
  }'
