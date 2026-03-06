#!/bin/bash
# Check Claude OAuth token health and alert if refresh needed

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
TOKEN_FILE="$BASE_DIR/.tokens"
ALERT_STATE="/tmp/claude-oauth-refresh-alert"

# Extract current access token
if [ ! -f "$TOKEN_FILE" ]; then
  echo "❌ Token file not found: $TOKEN_FILE" >&2
  exit 1
fi

ACCESS_TOKEN=$(grep ACCESS_TOKEN "$TOKEN_FILE" | cut -d'=' -f2)

if [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ Could not extract access token" >&2
  exit 1
fi

# Test if token works (minimal API call)
RESPONSE=$(curl -s "https://api.anthropic.com/api/oauth/usage" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "anthropic-beta: oauth-2025-04-20")

# Check if token is valid
if echo "$RESPONSE" | grep -q '"five_hour"'; then
  # Token works! Clear alert state
  rm -f "$ALERT_STATE"
  echo "✅ OAuth token is valid"
  
  # Sync to ~/.claude/.credentials.json if needed
  if [ -f ~/.claude/.credentials.json ]; then
    REFRESH_TOKEN=$(grep REFRESH_TOKEN "$TOKEN_FILE" | cut -d'=' -f2)
    EXPIRES_AT=$(($(date +%s) * 1000 + 3600000))  # +1 hour
    
    python3 << PYTHON_EOF
import json, os
creds_file = os.path.expanduser('~/.claude/.credentials.json')
try:
    with open(creds_file, 'r') as f:
        creds = json.load(f)
    creds['claudeAiOauth']['accessToken'] = "$ACCESS_TOKEN"
    creds['claudeAiOauth']['refreshToken'] = "$REFRESH_TOKEN"
    creds['claudeAiOauth']['expiresAt'] = $EXPIRES_AT
    with open(creds_file, 'w') as f:
        json.dump(creds, f, indent=2)
    os.chmod(creds_file, 0o600)
except Exception as e:
    pass  # Silent fail - not critical
PYTHON_EOF
  fi
  
  exit 0
elif echo "$RESPONSE" | grep -q "token_expired\|authentication_error"; then
  # Token expired - need manual refresh
  
  # Alert only once (until token is refreshed)
  if [ ! -f "$ALERT_STATE" ]; then
    echo "🔴 OAuth token has EXPIRED!"
    echo ""
    echo "📋 Manual refresh required:"
    echo "   1. Run: claude auth login"
    echo "   2. Browser will open for OAuth flow"
    echo "   3. Sign in to claude.ai"
    echo "   4. Done! Tokens auto-update"
    echo ""
    echo "This happens ~once per week. Takes 30 seconds."
    
    # Mark alert as sent
    date > "$ALERT_STATE"
    exit 1
  else
    # Alert already sent, silent fail
    echo "⚠️  Token expired (alert already sent)"
    exit 1
  fi
else
  # Unexpected response
  echo "⚠️  Unexpected API response:"
  echo "$RESPONSE" | head -5
  exit 1
fi
