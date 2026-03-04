#!/usr/bin/env bash
set -euo pipefail

# Security Manifest:
# - Accesses: MEMEPICKUP_API_KEY
# - Endpoints: https://rork-memepickup-app-3.vercel.app/api/v1/*
# - File Operations: None

# Validate required env vars
if [[ -z "${MEMEPICKUP_API_KEY:-}" ]]; then
  echo '{"error":"MEMEPICKUP_API_KEY not set. Get your key from MemePickup app: Profile > Wingman API > Generate Key"}' >&2
  exit 1
fi

API_BASE="https://rork-memepickup-app-3.vercel.app/api/v1"
ACTION="${1:-}"

# Whitelist allowed actions — no arbitrary endpoint injection
case "$ACTION" in
  lines)      ENDPOINT="$API_BASE/lines/generate" ;;
  replies)    ENDPOINT="$API_BASE/replies/generate" ;;
  screenshot) ENDPOINT="$API_BASE/replies/from-screenshot" ;;
  analyze)    ENDPOINT="$API_BASE/profiles/analyze" ;;
  credits)    ENDPOINT="$API_BASE/credits" ;;
  get-prefs)  ENDPOINT="$API_BASE/preferences" ;;
  set-prefs)  ENDPOINT="$API_BASE/preferences" ;;
  *)
    echo '{"error":"Unknown action. Use: lines|replies|screenshot|analyze|credits|get-prefs|set-prefs"}' >&2
    exit 1
    ;;
esac

# GET requests (no body)
if [[ "$ACTION" == "credits" || "$ACTION" == "get-prefs" ]]; then
  exec curl -sf \
    -H "x-api-key: $MEMEPICKUP_API_KEY" \
    -H "Content-Type: application/json" \
    "$ENDPOINT"
fi

# PUT requests
if [[ "$ACTION" == "set-prefs" ]]; then
  # Read JSON payload from stdin (not from args — prevents shell injection)
  PAYLOAD=$(cat)
  exec curl -sf -X PUT \
    -H "x-api-key: $MEMEPICKUP_API_KEY" \
    -H "Content-Type: application/json" \
    --data-raw "$PAYLOAD" \
    "$ENDPOINT"
fi

# POST requests (lines, replies, screenshot, analyze)
PAYLOAD=$(cat)
exec curl -sf -X POST \
  -H "x-api-key: $MEMEPICKUP_API_KEY" \
  -H "Content-Type: application/json" \
  --data-raw "$PAYLOAD" \
  "$ENDPOINT"
