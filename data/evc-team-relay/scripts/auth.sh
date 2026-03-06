#!/usr/bin/env bash
# Authenticate with Relay Control Plane and print the access token.
# Usage: scripts/auth.sh
# Env: RELAY_CP_URL, RELAY_EMAIL, RELAY_PASSWORD
# Output: access_token (plain text, no newline) — suitable for $()
set -euo pipefail

: "${RELAY_CP_URL:?Set RELAY_CP_URL (e.g. https://cp.tr.entire.vc)}"
: "${RELAY_EMAIL:?Set RELAY_EMAIL}"
: "${RELAY_PASSWORD:?Set RELAY_PASSWORD}"

resp=$(curl -sf -X POST "${RELAY_CP_URL}/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"${RELAY_EMAIL}\", \"password\": \"${RELAY_PASSWORD}\"}")

token=$(echo "$resp" | jq -r '.access_token')
if [ -z "$token" ] || [ "$token" = "null" ]; then
  echo "Authentication failed" >&2
  echo "$resp" >&2
  exit 1
fi

echo -n "$token"
