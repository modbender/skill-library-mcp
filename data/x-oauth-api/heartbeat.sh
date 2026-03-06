#!/bin/bash

# x-oauth-api Heartbeat Integration
# Monitors and posts status updates to X

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$HOME/.openclaw/heartbeat/x-api.log"
STATE_FILE="$HOME/.openclaw/heartbeat/x-api.state.json"

# Ensure directories exist
mkdir -p "$(dirname "$LOG_FILE")" "$(dirname "$STATE_FILE")"

# Initialize state if missing
if [ ! -f "$STATE_FILE" ]; then
  echo '{"lastCheck": null, "lastPost": null, "status": "ready"}' > "$STATE_FILE"
fi

# Function: Check rate limits
check_rate_limits() {
  echo "[$(date)] Checking X API rate limits..."
  node "$SCRIPT_DIR/bin/x.js" rate-limits >> "$LOG_FILE" 2>&1
  
  if [ $? -eq 0 ]; then
    echo "✅ Rate limits OK"
    return 0
  else
    echo "❌ Rate limit check failed"
    return 1
  fi
}

# Function: Verify credentials
verify_credentials() {
  if [ -z "$X_API_KEY" ] || [ -z "$X_API_SECRET" ] || [ -z "$X_ACCESS_TOKEN" ] || [ -z "$X_ACCESS_TOKEN_SECRET" ]; then
    echo "❌ Missing X API credentials"
    return 1
  fi
  echo "✅ Credentials configured"
  return 0
}

# Main heartbeat check
main() {
  echo "[$(date)] x-oauth-api heartbeat check"
  
  # Verify setup
  if ! verify_credentials; then
    echo "Status: credential_error" >> "$LOG_FILE"
    exit 1
  fi
  
  # Check rate limits
  if ! check_rate_limits; then
    echo "Status: rate_limit_check_failed" >> "$LOG_FILE"
    exit 1
  fi
  
  # Update state
  jq '.lastCheck = now | .status = "healthy"' "$STATE_FILE" > "${STATE_FILE}.tmp" && mv "${STATE_FILE}.tmp" "$STATE_FILE"
  
  echo "✅ Heartbeat OK"
  exit 0
}

main
