#!/bin/bash
# Ultra-lightweight Claude Code usage checker
# Token-friendly: aggressive caching, minimal API calls, one-time alerts

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

# Config
CACHE_FILE="${CACHE_FILE:-/tmp/claude-usage.cache}"
STATE_FILE="${STATE_FILE:-/tmp/claude-usage-alert-state}"
CACHE_TTL="${CACHE_TTL:-600}"  # 10 minutes default
TOKEN_FILE="$BASE_DIR/.tokens"

# Check if tokens configured
if [ ! -f "$TOKEN_FILE" ]; then
  echo "ERROR: No tokens configured. Run setup.sh first." >&2
  exit 1
fi

# Load tokens
source "$TOKEN_FILE"

if [ -z "$ACCESS_TOKEN" ]; then
  echo "ERROR: ACCESS_TOKEN not found in $TOKEN_FILE" >&2
  exit 1
fi

# Check cache freshness
if [ -f "$CACHE_FILE" ]; then
  if [[ "$OSTYPE" == "darwin"* ]]; then
    AGE=$(($(date +%s) - $(stat -f%m "$CACHE_FILE")))
  else
    AGE=$(($(date +%s) - $(stat -c%Y "$CACHE_FILE")))
  fi
  
  if [ "$AGE" -lt "$CACHE_TTL" ]; then
    cat "$CACHE_FILE"
    exit 0
  fi
fi

# Check if claude CLI is available (handles auto-refresh automatically)
if command -v claude >/dev/null 2>&1; then
  # Claude CLI available - use it to get fresh token
  # It will auto-refresh if needed and update ~/.claude/.credentials.json
  
  # Trigger a simple query to ensure token is fresh
  echo "ping" | claude --quiet >/dev/null 2>&1 || true
  
  # Extract fresh token from credentials file
  if [ -f ~/.claude/.credentials.json ]; then
    FRESH_TOKEN=$(python3 -c "import json; d=json.load(open('$HOME/.claude/.credentials.json')); print(d.get('claudeAiOauth', {}).get('accessToken', ''))" 2>/dev/null)
    if [ -n "$FRESH_TOKEN" ]; then
      ACCESS_TOKEN="$FRESH_TOKEN"
      # Update .tokens file for consistency
      sed -i.bak "s|ACCESS_TOKEN=.*|ACCESS_TOKEN=\"$ACCESS_TOKEN\"|" "$TOKEN_FILE" 2>/dev/null || true
    fi
  fi
fi

# Fetch fresh data
RESP=$(curl -sf "https://api.anthropic.com/api/oauth/usage" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "anthropic-beta: oauth-2025-04-20" 2>&1)

# Check if failed
if [ -z "$RESP" ] || echo "$RESP" | grep -q "token_expired\|authentication_error"; then
  echo "ERROR: API request failed. Token may be expired." >&2
  echo "Hint: Run 'claude auth login' to refresh tokens." >&2
  exit 1
fi

# Parse critical fields only
SESSION=$(echo "$RESP" | grep -o '"five_hour":{"utilization":[0-9.]*' | grep -o '[0-9.]*$')
WEEKLY=$(echo "$RESP" | grep -o '"seven_day":{"utilization":[0-9.]*' | grep -o '[0-9.]*$')
WEEKLY_RESET=$(echo "$RESP" | grep -o '"seven_day":{"utilization":[0-9.]*,"resets_at":"[^"]*"' | grep -o 'resets_at":"[^"]*"' | cut -d'"' -f3)

# Calculate burn rate vs expected (daily budget = 14.3% = 100%/7 days)
BURN_RATE=""
if [ -n "$WEEKLY_RESET" ] && [ -n "$WEEKLY" ]; then
  if [[ "$OSTYPE" == "darwin"* ]]; then
    RESET_TS=$(date -j -f "%Y-%m-%dT%H:%M:%S" "${WEEKLY_RESET%.*}" +%s 2>/dev/null || echo 0)
  else
    RESET_TS=$(date -d "$WEEKLY_RESET" +%s 2>/dev/null || echo 0)
  fi
  
  if [ "$RESET_TS" -gt 0 ]; then
    NOW=$(date +%s)
    DAYS_LEFT=$(( ($RESET_TS - $NOW) / 86400 ))
    DAYS_ELAPSED=$(( 7 - $DAYS_LEFT ))
    EXPECTED=$(( $DAYS_ELAPSED * 14 ))  # ~14% per day (simplified)
    WEEKLY_INT=$(printf "%.0f" "${WEEKLY:-0}")
    DIFF=$(( $WEEKLY_INT - $EXPECTED ))
    
    if [ "$DIFF" -lt -10 ]; then
      BURN_RATE="UNDER"  # Can use more
    elif [ "$DIFF" -gt 10 ]; then
      BURN_RATE="OVER"   # Over-using
    else
      BURN_RATE="OK"     # On pace
    fi
  fi
fi

# Check previous state for alert deduplication
PREV_SESSION=0
if [ -f "$STATE_FILE" ]; then
  PREV_SESSION=$(grep "^LAST_SESSION=" "$STATE_FILE" 2>/dev/null | cut -d= -f2)
  PREV_SESSION=${PREV_SESSION:-0}
fi

# Save to cache
echo "SESSION=${SESSION:-0}" > "$CACHE_FILE"
echo "WEEKLY=${WEEKLY:-0}" >> "$CACHE_FILE"
echo "BURN_RATE=${BURN_RATE}" >> "$CACHE_FILE"
echo "CACHED_AT=$(date +%s)" >> "$CACHE_FILE"

# Check if should alert (only on threshold crossing)
SESSION_INT=$(printf "%.0f" "${SESSION:-0}")
PREV_INT=$(printf "%.0f" "$PREV_SESSION")

if [ "$SESSION_INT" -gt 50 ] && [ "$PREV_INT" -le 50 ]; then
  echo "ALERT_SESSION=1" >> "$CACHE_FILE"
fi

# Update state
echo "LAST_SESSION=${SESSION:-0}" > "$STATE_FILE"

# Output
cat "$CACHE_FILE"
