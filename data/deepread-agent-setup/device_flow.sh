#!/bin/bash
# DeepRead Device Flow Authentication
#
# OAuth 2.0 Device Authorization Flow (RFC 8628) for AI agents.
# Requests a device code, waits for user approval, and exports
# the resulting API key as DEEPREAD_API_KEY.
#
# Only contacts: api.deepread.tech
#
# Usage:
#   source device_flow.sh
#
# Dependencies: curl, jq

set -euo pipefail

API_BASE="https://api.deepread.tech"

# Step 1: Request device code
# POST /v1/agent/device/code — body: {"agent_name": "..."} (optional)
echo "Requesting device code..."
DEVICE_RESPONSE=$(curl -s -X POST "${API_BASE}/v1/agent/device/code" \
  -H "Content-Type: application/json" \
  -d '{"agent_name": "clawdhub-agent"}')

DEVICE_CODE=$(echo "$DEVICE_RESPONSE" | jq -r '.device_code')
USER_CODE=$(echo "$DEVICE_RESPONSE" | jq -r '.user_code')
VERIFY_URI=$(echo "$DEVICE_RESPONSE" | jq -r '.verification_uri')
VERIFY_URI_COMPLETE=$(echo "$DEVICE_RESPONSE" | jq -r '.verification_uri_complete')
INTERVAL=$(echo "$DEVICE_RESPONSE" | jq -r '.interval // 5')

if [ -z "$DEVICE_CODE" ] || [ "$DEVICE_CODE" = "null" ]; then
  echo "Error: Failed to get device code." >&2
  echo "Response: $DEVICE_RESPONSE" >&2
  exit 1
fi

echo ""
echo "Open: ${VERIFY_URI}"
echo "Enter code: ${USER_CODE}"
echo "Or open directly: ${VERIFY_URI_COMPLETE}"
echo ""
echo "Waiting for approval..."

# Step 2: Poll for token
# POST /v1/agent/device/token — body: {"device_code": "..."}
# Returns: api_key (once, on approval) or error string
while true; do
  TOKEN_RESPONSE=$(curl -s -X POST "${API_BASE}/v1/agent/device/token" \
    -H "Content-Type: application/json" \
    -d "{\"device_code\": \"${DEVICE_CODE}\"}")

  ERROR=$(echo "$TOKEN_RESPONSE" | jq -r '.error // empty')

  if [ -z "$ERROR" ]; then
    API_KEY=$(echo "$TOKEN_RESPONSE" | jq -r '.api_key')
    break
  elif [ "$ERROR" = "authorization_pending" ]; then
    sleep "$INTERVAL"
  elif [ "$ERROR" = "slow_down" ]; then
    INTERVAL=$((INTERVAL + 5))
    sleep "$INTERVAL"
  else
    echo "Error: ${ERROR}" >&2
    exit 1
  fi
done

# Step 3: Store as environment variable (current session only — does not write to disk)
export DEEPREAD_API_KEY="$API_KEY"
unset API_KEY  # Clear the temporary variable
echo ""
echo "Approved! DEEPREAD_API_KEY is set for this session."
echo ""
echo "To persist across sessions (your choice):"
echo "  Option 1 (recommended): Store in a secrets manager (OS keychain, 1Password CLI, pass)"
echo "  Option 2: Manually add 'export DEEPREAD_API_KEY=\"...\"' to ~/.zshrc"
echo ""
echo "The key value is in \$DEEPREAD_API_KEY — use 'echo \$DEEPREAD_API_KEY' to see it."
