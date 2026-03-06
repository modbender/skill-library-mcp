#!/usr/bin/env bash
# Delete a file from a folder share.
# Usage: scripts/delete-file.sh <folder_share_id> <file_path>
# Args:
#   folder_share_id — folder share UUID
#   file_path       — file name within the folder (e.g. "notes.md")
# Env: RELAY_CP_URL, RELAY_TOKEN (or pass token as first arg)
# Output: JSON with path and status
set -euo pipefail

: "${RELAY_CP_URL:?Set RELAY_CP_URL}"

# Token: prefer RELAY_TOKEN env var, fall back to $1 (backward-compatible)
if [ -n "${RELAY_TOKEN:-}" ]; then
  TOKEN="$RELAY_TOKEN"
else
  TOKEN="${1:?Usage: delete-file.sh [token] <folder_share_id> <file_path> (or set RELAY_TOKEN)}"
  shift
fi
FOLDER_SHARE_ID="${1:?Usage: delete-file.sh <folder_share_id> <file_path>}"
FILE_PATH="${2:?Usage: delete-file.sh <folder_share_id> <file_path>}"

# URL-encode the file path for safety (using jq to avoid python3 dependency)
ENCODED_PATH=$(printf '%s' "$FILE_PATH" | jq -sRr @uri)

curl -sf -X DELETE "${RELAY_CP_URL}/v1/documents/${FOLDER_SHARE_ID}/files/${ENCODED_PATH}?share_id=${FOLDER_SHARE_ID}" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
