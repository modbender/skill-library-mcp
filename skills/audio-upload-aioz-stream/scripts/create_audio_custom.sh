#!/bin/bash
# Create audio with custom configuration
# Usage: ./create_audio_custom.sh PUBLIC_KEY SECRET_KEY CONFIG_JSON_FILE

PUBLIC_KEY="$1"
SECRET_KEY="$2"
CONFIG_FILE="$3"

if [ -z "$PUBLIC_KEY" ] || [ -z "$SECRET_KEY" ] || [ -z "$CONFIG_FILE" ]; then
    echo "Usage: $0 PUBLIC_KEY SECRET_KEY CONFIG_JSON_FILE"
    exit 1
fi

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config file $CONFIG_FILE not found"
    exit 1
fi

curl -s -X POST 'https://api-w3stream.attoaioz.cyou/api/videos/create' \
  -H "stream-public-key: $PUBLIC_KEY" \
  -H "stream-secret-key: $SECRET_KEY" \
  -H 'Content-Type: application/json' \
  -d @"$CONFIG_FILE"
