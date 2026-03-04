#!/usr/bin/env bash
# List files in a folder share from Relay.
# Usage: scripts/list-files.sh <share_id>
# Args:
#   share_id — folder share UUID (used as both doc_id and share_id for ACL check)
# Env: RELAY_CP_URL, RELAY_TOKEN (or pass token as first arg)
# Output: JSON with doc_id and files map (path -> metadata)
set -euo pipefail

: "${RELAY_CP_URL:?Set RELAY_CP_URL}"

# Token: prefer RELAY_TOKEN env var, fall back to $1 (backward-compatible)
if [ -n "${RELAY_TOKEN:-}" ]; then
  TOKEN="$RELAY_TOKEN"
else
  TOKEN="${1:?Usage: list-files.sh [token] <share_id> (or set RELAY_TOKEN)}"
  shift
fi
SHARE_ID="${1:?Usage: list-files.sh <share_id>}"

curl -sf "${RELAY_CP_URL}/v1/documents/${SHARE_ID}/files?share_id=${SHARE_ID}" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
