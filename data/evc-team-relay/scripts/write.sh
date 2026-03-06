#!/usr/bin/env bash
# Write document content to Relay (doc shares only).
#
# IMPORTANT: This script detects folder shares and refuses to write.
# For folder shares, use upsert-file.sh instead — it properly registers
# files in folder metadata so Obsidian can see them.
#
# Usage: scripts/write.sh <share_id> <doc_id> <content> [key]
#    or: echo "content" | scripts/write.sh <share_id> <doc_id> - [key]
# Args:
#   share_id — share UUID (for ACL check)
#   doc_id   — document ID
#   content  — text content to write, or "-" to read from stdin
#   key      — (optional) Yjs key, defaults to "contents"
# Env: RELAY_CP_URL, RELAY_TOKEN (or pass token as first arg)
set -euo pipefail

: "${RELAY_CP_URL:?Set RELAY_CP_URL}"

# Token: prefer RELAY_TOKEN env var, fall back to $1 (backward-compatible)
if [ -n "${RELAY_TOKEN:-}" ]; then
  TOKEN="$RELAY_TOKEN"
else
  TOKEN="${1:?Usage: write.sh [token] <share_id> <doc_id> <content> [key] (or set RELAY_TOKEN)}"
  shift
fi
SHARE_ID="${1:?Usage: write.sh <share_id> <doc_id> <content> [key]}"
DOC_ID="${2:?Usage: write.sh <share_id> <doc_id> <content> [key]}"
CONTENT_ARG="${3:?Usage: write.sh <share_id> <doc_id> <content> [key]}"
KEY="${4:-contents}"

# Safety check: detect folder shares and refuse
# If share_id == doc_id AND the share has a files endpoint, it's likely a folder share
# being used incorrectly (user passing share_id as doc_id)
if [ "$SHARE_ID" = "$DOC_ID" ]; then
  # Check if this is a folder share by trying to list files
  FILES_CHECK=$(curl -sf "${RELAY_CP_URL}/v1/documents/${SHARE_ID}/files?share_id=${SHARE_ID}" \
    -H "Authorization: Bearer $TOKEN" 2>/dev/null || echo "")
  if [ -n "$FILES_CHECK" ]; then
    FILE_COUNT=$(echo "$FILES_CHECK" | jq '.files | length' 2>/dev/null || echo "0")
    if [ "$FILE_COUNT" -gt "0" ] || echo "$FILES_CHECK" | jq -e '.files' >/dev/null 2>&1; then
      echo "Error: this looks like a folder share (has file metadata)." >&2
      echo "write.sh does NOT work for folder shares — files won't appear in Obsidian." >&2
      echo "" >&2
      echo "Use upsert-file.sh instead:" >&2
      echo "  scripts/upsert-file.sh \"$TOKEN\" \"$SHARE_ID\" \"filename.md\" \"content\"" >&2
      exit 1
    fi
  fi
fi

if [ "$CONTENT_ARG" = "-" ]; then
  CONTENT=$(cat)
else
  CONTENT="$CONTENT_ARG"
fi

# Build JSON payload with jq to handle escaping
PAYLOAD=$(jq -n \
  --arg sid "$SHARE_ID" \
  --arg content "$CONTENT" \
  --arg key "$KEY" \
  '{share_id: $sid, content: $content, key: $key}')

curl -sf -X PUT "${RELAY_CP_URL}/v1/documents/${DOC_ID}/content" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" | jq '.'
