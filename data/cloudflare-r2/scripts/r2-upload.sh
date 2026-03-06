#!/bin/bash
# Cloudflare R2 Upload Script
# Usage: r2-upload.sh <local-path> [remote-path]

set -e

CONFIG_FILE="$HOME/.config/cloudflare/r2.json"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "Error: Config file not found at $CONFIG_FILE"
  exit 1
fi

# Load config
export CLOUDFLARE_ACCOUNT_ID=$(jq -r .accountId "$CONFIG_FILE")
export CLOUDFLARE_API_TOKEN=$(jq -r .apiToken "$CONFIG_FILE")
BUCKET=$(jq -r .bucket "$CONFIG_FILE")
PUBLIC_DOMAIN=$(jq -r .publicDomain "$CONFIG_FILE")

LOCAL_PATH="$1"
REMOTE_PATH="$2"

if [ -z "$LOCAL_PATH" ]; then
  echo "Usage: r2-upload.sh <local-path> [remote-path]"
  echo ""
  echo "Examples:"
  echo "  r2-upload.sh image.png                    # Upload to root"
  echo "  r2-upload.sh image.png article/cover.png  # Upload with custom path"
  echo "  r2-upload.sh ./images/ article/gallery/   # Batch upload directory"
  exit 1
fi

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
  echo "Error: wrangler not found. Install with: npm install -g wrangler"
  exit 1
fi

upload_file() {
  local local_file="$1"
  local remote_file="$2"
  
  echo "Uploading: $local_file -> $remote_file"
  wrangler r2 object put "$BUCKET/$remote_file" --file "$local_file" --remote 2>&1 | grep -E "Upload|Error|Creating"
  echo "URL: https://$PUBLIC_DOMAIN/$remote_file"
}

if [ -d "$LOCAL_PATH" ]; then
  # Directory upload
  if [ -z "$REMOTE_PATH" ]; then
    echo "Error: Remote prefix required for directory upload"
    exit 1
  fi
  
  echo "Uploading directory: $LOCAL_PATH -> $REMOTE_PATH"
  echo "---"
  
  find "$LOCAL_PATH" -type f | while read file; do
    filename=$(basename "$file")
    remote_file="${REMOTE_PATH%/}/$filename"
    upload_file "$file" "$remote_file"
  done
  
  echo "---"
  echo "Done! Files available at: https://$PUBLIC_DOMAIN/$REMOTE_PATH"
else
  # Single file upload
  if [ -z "$REMOTE_PATH" ]; then
    REMOTE_PATH=$(basename "$LOCAL_PATH")
  fi
  
  upload_file "$LOCAL_PATH" "$REMOTE_PATH"
fi
