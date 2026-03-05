#!/bin/bash
# Check a single TestFlight URL for availability

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOOKUP="$SCRIPT_DIR/lookup.sh"

URL="${1:-}"

if [[ -z "$URL" ]]; then
  echo "Usage: check-single.sh <testflight-url>" >&2
  exit 1
fi

# Extract code from URL
CODE=$(echo "$URL" | grep -oE '[A-Za-z0-9]{8}$' || true)

if [[ -z "$CODE" ]]; then
  echo "Error: Invalid TestFlight URL: $URL" >&2
  exit 1
fi

# Look up app name
APP_NAME=$("$LOOKUP" "$CODE" 2>/dev/null || echo "Beta $CODE")

echo "Checking $URL..."

# Fetch the page
HTML=$(curl -sSL -H "User-Agent: Mozilla/5.0" "$URL" 2>&1 || true)

# Check for availability indicators
if echo "$HTML" | grep -qi "This beta is full"; then
  STATUS="full"
  echo "Status: full | App: $APP_NAME"
  exit 0
elif echo "$HTML" | grep -qi "This beta isn't accepting"; then
  STATUS="full"
  echo "Status: full | App: $APP_NAME"
  exit 0
elif echo "$HTML" | grep -qi "Start Testing"; then
  STATUS="available"
  echo "Status: AVAILABLE ✓ | App: $APP_NAME"
  echo ""
  echo "🎉 Open slots available! Join now: $URL"
  exit 0
elif echo "$HTML" | grep -qi "Join the .* beta"; then
  STATUS="available"
  echo "Status: AVAILABLE ✓ | App: $APP_NAME"
  echo ""
  echo "🎉 Open slots available! Join now: $URL"
  exit 0
else
  # Unknown state - might be rate limited or page changed
  echo "Status: unknown | App: $APP_NAME"
  echo "Warning: Could not determine status (rate limit or page change?)"
  exit 2
fi
