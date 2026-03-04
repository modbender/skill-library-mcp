#!/usr/bin/env bash
# Read a file from a folder share by its path.
# Resolves file path → doc_id automatically via list-files, then reads content.
#
# Usage: scripts/read-file.sh <folder_share_id> <file_path> [key]
# Args:
#   folder_share_id — folder share UUID
#   file_path       — file path within the folder (e.g. "Marketing/plan.md")
#   key             — (optional) Yjs key, defaults to "contents"
# Env: RELAY_CP_URL, RELAY_TOKEN (or pass token as first arg)
# Output: JSON with doc_id, path, content
set -euo pipefail

: "${RELAY_CP_URL:?Set RELAY_CP_URL}"

# Token: prefer RELAY_TOKEN env var, fall back to $1 (backward-compatible)
if [ -n "${RELAY_TOKEN:-}" ]; then
  TOKEN="$RELAY_TOKEN"
else
  TOKEN="${1:?Usage: read-file.sh [token] <folder_share_id> <file_path> [key] (or set RELAY_TOKEN)}"
  shift
fi
FOLDER_SHARE_ID="${1:?Usage: read-file.sh <folder_share_id> <file_path> [key]}"
FILE_PATH="${2:?Usage: read-file.sh <folder_share_id> <file_path> [key]}"
KEY="${3:-contents}"

# Step 1: List files to resolve path → doc_id
FILES_JSON=$(curl -sf "${RELAY_CP_URL}/v1/documents/${FOLDER_SHARE_ID}/files?share_id=${FOLDER_SHARE_ID}" \
  -H "Authorization: Bearer $TOKEN")

DOC_ID=$(echo "$FILES_JSON" | jq -r --arg path "$FILE_PATH" '.files[$path].id // empty')

if [ -z "$DOC_ID" ]; then
  echo "Error: file not found in folder share: $FILE_PATH" >&2
  echo "Available files:" >&2
  echo "$FILES_JSON" | jq -r '.files | keys[]' >&2
  exit 1
fi

# Step 2: Read content using resolved doc_id
CONTENT_JSON=$(curl -sf "${RELAY_CP_URL}/v1/documents/${DOC_ID}/content?share_id=${FOLDER_SHARE_ID}&key=${KEY}" \
  -H "Authorization: Bearer $TOKEN")

# Return enriched response with path included
echo "$CONTENT_JSON" | jq --arg path "$FILE_PATH" '. + {path: $path}'
