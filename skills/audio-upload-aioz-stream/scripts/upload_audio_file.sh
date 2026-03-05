#!/bin/bash
# Upload audio file to W3Stream (create + upload in one step)
# Usage: ./upload_audio_file.sh PUBLIC_KEY SECRET_KEY FILE_PATH TITLE

PUBLIC_KEY="$1"
SECRET_KEY="$2"
FILE_PATH="$3"
TITLE="$4"

if [ -z "$PUBLIC_KEY" ] || [ -z "$SECRET_KEY" ] || [ -z "$FILE_PATH" ] || [ -z "$TITLE" ]; then
    echo "Usage: $0 PUBLIC_KEY SECRET_KEY FILE_PATH TITLE"
    exit 1
fi

if [ ! -f "$FILE_PATH" ]; then
    echo "Error: File not found: $FILE_PATH"
    exit 1
fi

# Step 1: Create audio object
echo "Creating audio object..."
CREATE_RESPONSE=$(curl -s -X POST 'https://api-w3stream.attoaioz.cyou/api/videos/create' \
  -H "stream-public-key: $PUBLIC_KEY" \
  -H "stream-secret-key: $SECRET_KEY" \
  -H 'Content-Type: application/json' \
  -d "{
    \"title\": \"$TITLE\",
    \"type\": \"audio\"
  }")

# Extract audio ID
AUDIO_ID=$(echo "$CREATE_RESPONSE" | jq -r '.data.id')

if [ "$AUDIO_ID" == "null" ] || [ -z "$AUDIO_ID" ]; then
    echo "Error creating audio object:"
    echo "$CREATE_RESPONSE"
    exit 1
fi

echo "Audio object created with ID: $AUDIO_ID"

# Step 2: Calculate file size and MD5 hash
echo "Calculating file size and hash..."
FILE_SIZE=$(stat -f%z "$FILE_PATH" 2>/dev/null || stat -c%s "$FILE_PATH")
END_POS=$((FILE_SIZE - 1))
HASH=$(md5sum "$FILE_PATH" | awk '{print $1}')

echo "File size: $FILE_SIZE bytes"
echo "MD5 hash: $HASH"

# Step 3: Upload the file using multipart form-data with Content-Range header
echo "Uploading file..."
UPLOAD_RESPONSE=$(curl -s -X POST "https://api-w3stream.attoaioz.cyou/api/videos/$AUDIO_ID/part" \
  -H "stream-public-key: $PUBLIC_KEY" \
  -H "stream-secret-key: $SECRET_KEY" \
  -H "Content-Range: bytes 0-$END_POS/$FILE_SIZE" \
  -F "file=@$FILE_PATH" \
  -F "index=0" \
  -F "hash=$HASH")

echo "Upload response:"
echo "$UPLOAD_RESPONSE" | jq '.'

# Step 4: Complete the upload to trigger transcoding
echo ""
echo "Completing upload..."
COMPLETE_RESPONSE=$(curl -s -X GET "https://api-w3stream.attoaioz.cyou/api/videos/$AUDIO_ID/complete" \
  -H 'accept: application/json' \
  -H "stream-public-key: $PUBLIC_KEY" \
  -H "stream-secret-key: $SECRET_KEY")

echo "Complete response:"
echo "$COMPLETE_RESPONSE" | jq '.'

# Step 5: Get final audio details
echo ""
echo "Fetching audio details..."
sleep 2
DETAIL_RESPONSE=$(curl -s "https://api-w3stream.attoaioz.cyou/api/videos/$AUDIO_ID" \
  -H "stream-public-key: $PUBLIC_KEY" \
  -H "stream-secret-key: $SECRET_KEY")

echo ""
echo "=== Final Audio Details ==="
echo "$DETAIL_RESPONSE" | jq '.'

# Extract and display URLs
HLS_URL=$(echo "$DETAIL_RESPONSE" | jq -r '.data.assets.hls_url // .data.assets.hls // empty')
HLS_PLAYER_URL=$(echo "$DETAIL_RESPONSE" | jq -r '.data.assets.hls_player_url // empty')
STATUS=$(echo "$DETAIL_RESPONSE" | jq -r '.data.status // empty')

echo ""
echo "=== Upload Status ==="
echo "Status: $STATUS"

if [ -n "$HLS_PLAYER_URL" ]; then
    echo ""
    echo "=== 🎵 Audio Player URL (Click to Play) ==="
    echo "$HLS_PLAYER_URL"
fi

if [ -n "$HLS_URL" ]; then
    echo ""
    echo "=== HLS Manifest URL (for developers) ==="
    echo "$HLS_URL"
fi

if [ "$STATUS" == "transcoding" ]; then
    echo ""
    echo "Note: Audio is still transcoding. Check back later for the streaming URL."
elif [ -z "$HLS_PLAYER_URL" ] && [ -z "$HLS_URL" ]; then
    echo ""
    echo "Note: No streaming URLs available yet. The audio may still be processing."
fi

