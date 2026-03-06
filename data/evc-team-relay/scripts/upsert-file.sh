#!/usr/bin/env bash
# Create or update a file in a folder share (smart upsert).
# Automatically detects whether the file already exists:
#   - New file    → POST /files (creates document + registers in folder metadata)
#   - Existing    → PUT /content (updates document content)
#
# Usage: scripts/upsert-file.sh <folder_share_id> <file_path> <content>
#    or: echo "content" | scripts/upsert-file.sh <folder_share_id> <file_path> -
# Args:
#   folder_share_id — folder share UUID
#   file_path       — file name within the folder (e.g. "notes.md")
#   content         — text content to write, or "-" to read from stdin
# Env: RELAY_CP_URL, RELAY_TOKEN (or pass token as first arg)
# Output: JSON with doc_id, path, length, and operation ("created" or "updated")
set -euo pipefail

: "${RELAY_CP_URL:?Set RELAY_CP_URL}"

# Token: prefer RELAY_TOKEN env var, fall back to $1 (backward-compatible)
if [ -n "${RELAY_TOKEN:-}" ]; then
  TOKEN="$RELAY_TOKEN"
else
  TOKEN="${1:?Usage: upsert-file.sh [token] <folder_share_id> <file_path> <content> (or set RELAY_TOKEN)}"
  shift
fi
FOLDER_SHARE_ID="${1:?Usage: upsert-file.sh <folder_share_id> <file_path> <content>}"
FILE_PATH="${2:?Usage: upsert-file.sh <folder_share_id> <file_path> <content>}"
CONTENT_ARG="${3:?Usage: upsert-file.sh <folder_share_id> <file_path> <content>}"

if [ "$CONTENT_ARG" = "-" ]; then
  CONTENT=$(cat)
else
  CONTENT="$CONTENT_ARG"
fi

# Check if file already exists in the folder's metadata
FILES_JSON=$(curl -sf "${RELAY_CP_URL}/v1/documents/${FOLDER_SHARE_ID}/files?share_id=${FOLDER_SHARE_ID}" \
  -H "Authorization: Bearer $TOKEN")

EXISTING_DOC_ID=$(echo "$FILES_JSON" | jq -r --arg path "$FILE_PATH" '.files[$path].id // empty')

if [ -n "$EXISTING_DOC_ID" ]; then
  # File exists — update content via PUT
  PAYLOAD=$(jq -n \
    --arg sid "$FOLDER_SHARE_ID" \
    --arg content "$CONTENT" \
    '{share_id: $sid, content: $content, key: "contents"}')

  RESULT=$(curl -sf -X PUT "${RELAY_CP_URL}/v1/documents/${EXISTING_DOC_ID}/content" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")

  echo "$RESULT" | jq --arg path "$FILE_PATH" '. + {path: $path, operation: "updated"}'
else
  # File doesn't exist — create via POST (registers in filemeta_v0)
  PAYLOAD=$(jq -n \
    --arg sid "$FOLDER_SHARE_ID" \
    --arg path "$FILE_PATH" \
    --arg content "$CONTENT" \
    '{share_id: $sid, path: $path, content: $content}')

  RESULT=$(curl -sf -X POST "${RELAY_CP_URL}/v1/documents/${FOLDER_SHARE_ID}/files" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")

  echo "$RESULT" | jq '. + {operation: "created"}'
fi
