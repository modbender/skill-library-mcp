#!/usr/bin/env bash
set -euo pipefail
[ -z "${CLAWNALYST_API_KEY:-}" ] && { echo '{"error":"CLAWNALYST_API_KEY not set"}' >&2; exit 1; }
BODY="${1:?Usage: update_profile.sh '<json_body>'}"
curl -s -X PUT "https://api.clawnalyst.com/v1/agents/me/profile" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${CLAWNALYST_API_KEY}" \
  -d "${BODY}"