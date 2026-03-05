#!/bin/bash
# Upload video file to W3Stream
# Handles MD5 hashing, Content-Range headers, and multipart upload

PUBLIC_KEY="$1"
SECRET_KEY="$2"
VIDEO_ID="$3"
FILE_PATH="$4"

if [ -z "$PUBLIC_KEY" ] || [ -z "$SECRET_KEY" ] || [ -z "$VIDEO_ID" ] || [ -z "$FILE_PATH" ]; then
  echo "Usage: $0 <public_key> <secret_key> <video_id> <file_path>"
  exit 1
fi

if [ ! -f "$FILE_PATH" ]; then
  echo "Error: File not found: $FILE_PATH"
  exit 1
fi

echo "Uploading video file: $FILE_PATH"

# Get file size (cross-platform compatible)
FILE_SIZE=$(stat -f%z "$FILE_PATH" 2>/dev/null || stat -c%s "$FILE_PATH")
END_POS=$((FILE_SIZE - 1))

echo "File size: $FILE_SIZE bytes"

# Compute MD5 hash
echo "Computing MD5 hash..."
HASH=$(md5sum "$FILE_PATH" | awk '{print $1}')
echo "MD5 hash: $HASH"

# Determine chunk size for large files
CHUNK_SIZE=$((100 * 1024 * 1024))  # 100MB chunks

if [ "$FILE_SIZE" -le "$CHUNK_SIZE" ]; then
  # Single-part upload
  echo "Uploading in single part..."
  
  curl -s -X POST "https://api-w3stream.attoaioz.cyou/api/videos/$VIDEO_ID/part" \
    -H 'stream-public-key: '"$PUBLIC_KEY" \
    -H 'stream-secret-key: '"$SECRET_KEY" \
    -H "Content-Range: bytes 0-$END_POS/$FILE_SIZE" \
    -F "file=@$FILE_PATH" \
    -F "index=0" \
    -F "hash=$HASH"
  
  echo ""
  echo "Upload completed!"
else
  # Multi-part upload
  echo "File is large. Using multi-part upload..."
  
  PART_INDEX=0
  START_POS=0
  
  while [ "$START_POS" -lt "$FILE_SIZE" ]; do
    # Calculate end position for this chunk
    END_POS=$((START_POS + CHUNK_SIZE - 1))
    if [ "$END_POS" -ge "$FILE_SIZE" ]; then
      END_POS=$((FILE_SIZE - 1))
    fi
    
    CHUNK_SIZE_ACTUAL=$((END_POS - START_POS + 1))
    
    echo "Uploading part $PART_INDEX: bytes $START_POS-$END_POS/$FILE_SIZE ($CHUNK_SIZE_ACTUAL bytes)"
    
    # Extract chunk and compute its MD5
    dd if="$FILE_PATH" bs=1 skip="$START_POS" count="$CHUNK_SIZE_ACTUAL" 2>/dev/null | \
      tee >(md5sum | awk '{print $1}' > /tmp/chunk_hash_$$) | \
      curl -s -X POST "https://api-w3stream.attoaioz.cyou/api/videos/$VIDEO_ID/part" \
        -H 'stream-public-key: '"$PUBLIC_KEY" \
        -H 'stream-secret-key: '"$SECRET_KEY" \
        -H "Content-Range: bytes $START_POS-$END_POS/$FILE_SIZE" \
        -F "file=@-;filename=$(basename "$FILE_PATH")" \
        -F "index=$PART_INDEX" \
        -F "hash=$(cat /tmp/chunk_hash_$$)"
    
    echo ""
    
    # Cleanup temp file
    rm -f /tmp/chunk_hash_$$
    
    # Move to next chunk
    START_POS=$((END_POS + 1))
    PART_INDEX=$((PART_INDEX + 1))
  done
  
  echo "Multi-part upload completed!"
fi

# Complete the upload
echo "Finalizing upload..."
curl -s -X GET "https://api-w3stream.attoaioz.cyou/api/videos/$VIDEO_ID/complete" \
  -H 'accept: application/json' \
  -H 'stream-public-key: '"$PUBLIC_KEY" \
  -H 'stream-secret-key: '"$SECRET_KEY"

echo ""
echo "Upload finalized successfully!"
