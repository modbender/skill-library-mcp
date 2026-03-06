#!/usr/bin/env bash
set -euo pipefail

AUTH_FILE="$HOME/.openclaw/agents/main/agent/auth-profiles.json"
PROFILES=("anthropic:jawadjarvis" "anthropic:manual")

usage() {
  echo "Usage: keyswap.sh <new-token>"
  echo "  Token must start with 'sk-ant-'"
  exit 1
}

[[ $# -ne 1 ]] && usage

TOKEN="$1"

# Validate token format
if [[ ! "$TOKEN" =~ ^sk-ant- ]]; then
  echo "ERROR: Token must start with 'sk-ant-'. Got: ${TOKEN:0:10}..."
  exit 1
fi

# Check auth file exists
if [[ ! -f "$AUTH_FILE" ]]; then
  echo "ERROR: Auth profiles not found at $AUTH_FILE"
  exit 1
fi

# Check jq is available
if ! command -v jq &>/dev/null; then
  echo "ERROR: jq is required but not installed"
  exit 1
fi

echo "Updating tokens for: ${PROFILES[*]}"

# Build jq filter to update both profiles
FILTER='.'
for PROFILE in "${PROFILES[@]}"; do
  FILTER="$FILTER | .profiles[\"$PROFILE\"].token = \$token"
  FILTER="$FILTER | .usageStats[\"$PROFILE\"].errorCount = 0"
  FILTER="$FILTER | .usageStats[\"$PROFILE\"].lastFailureAt = null"
  FILTER="$FILTER | .usageStats[\"$PROFILE\"].cooldownUntil = null"
  FILTER="$FILTER | del(.usageStats[\"$PROFILE\"].failureCounts)"
done

TMPFILE=$(mktemp)
trap 'rm -f "$TMPFILE"' EXIT

if jq --arg token "$TOKEN" "$FILTER" "$AUTH_FILE" > "$TMPFILE"; then
  mv "$TMPFILE" "$AUTH_FILE"
  echo "Tokens updated successfully."
else
  echo "ERROR: jq failed to update auth profiles"
  exit 1
fi

# Restart gateway
echo "Restarting OpenClaw gateway..."
launchctl kickstart -k "gui/$(id -u)/ai.openclaw.gateway" 2>/dev/null || {
  echo "WARNING: launchctl restart failed. Gateway may not be running as a LaunchAgent."
}

echo "Waiting 5s for gateway to start..."
sleep 5

echo "Checking health..."
if openclaw health 2>/dev/null; then
  echo "Gateway is healthy. Key rotation complete."
else
  echo "WARNING: Health check failed or openclaw CLI not available. Check gateway manually."
fi
