#!/usr/bin/env bash
# List accessible shares from Relay Control Plane.
# Usage: scripts/list-shares.sh [kind] [owned_only]
# Args:
#   kind        — (optional) "doc" or "folder"
#   owned_only  — (optional) "true" to show only owned shares
# Env: RELAY_CP_URL, RELAY_TOKEN (or pass token as first arg)
set -euo pipefail

: "${RELAY_CP_URL:?Set RELAY_CP_URL}"

# Token: prefer RELAY_TOKEN env var, fall back to $1 (backward-compatible)
if [ -n "${RELAY_TOKEN:-}" ]; then
  TOKEN="$RELAY_TOKEN"
else
  TOKEN="${1:?Usage: list-shares.sh [token] [kind] [owned_only] (or set RELAY_TOKEN)}"
  shift
fi
KIND="${1:-}"
OWNED="${2:-}"

URL="${RELAY_CP_URL}/v1/shares"
PARAMS=""
[ -n "$KIND" ] && PARAMS="${PARAMS}&kind=${KIND}"
[ -n "$OWNED" ] && PARAMS="${PARAMS}&owned_only=${OWNED}"
[ -n "$PARAMS" ] && URL="${URL}?${PARAMS:1}"

curl -sf "$URL" -H "Authorization: Bearer $TOKEN" | jq '.'
