#!/usr/bin/env bash
# Read document content from Relay.
# Usage: scripts/read.sh <share_id> [doc_id] [key]
# Args:
#   share_id — share UUID (for ACL check)
#   doc_id   — (optional) document ID, defaults to share_id
#   key      — (optional) Yjs key, defaults to "contents"
# Env: RELAY_CP_URL, RELAY_TOKEN (or pass token as first arg)
# Output: document content as JSON (doc_id, content, format)
set -euo pipefail

: "${RELAY_CP_URL:?Set RELAY_CP_URL}"

# Token: prefer RELAY_TOKEN env var, fall back to $1 (backward-compatible)
if [ -n "${RELAY_TOKEN:-}" ]; then
  TOKEN="$RELAY_TOKEN"
else
  TOKEN="${1:?Usage: read.sh [token] <share_id> [doc_id] [key] (or set RELAY_TOKEN)}"
  shift
fi
SHARE_ID="${1:?Usage: read.sh <share_id> [doc_id] [key]}"
DOC_ID="${2:-$SHARE_ID}"
KEY="${3:-contents}"

curl -sf "${RELAY_CP_URL}/v1/documents/${DOC_ID}/content?share_id=${SHARE_ID}&key=${KEY}" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
