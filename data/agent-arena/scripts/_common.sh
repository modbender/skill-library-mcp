#!/bin/bash
# Shared helpers for Agent Arena scripts — sourced, not executed directly

_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[1]:-$0}")" && pwd)"
CONFIG_FILE="$_SCRIPT_DIR/../config/arena-config.json"

# Require jq
command -v jq >/dev/null 2>&1 || { echo '{"error":"jq is required. Install: brew install jq (macOS) or apt install jq (Linux)"}'; exit 1; }

# Load config values (can be overridden by env vars)
_load_config() {
  ARENA_API_KEY="${ARENA_API_KEY:-$(jq -r '.apiKey // empty' "$CONFIG_FILE" 2>/dev/null)}"
  ARENA_BASE_URL="${ARENA_BASE_URL:-$(jq -r '.baseUrl // "https://api.agentarena.chat/api/v1"' "$CONFIG_FILE" 2>/dev/null)}"
  ARENA_TOKEN="${ARENA_TOKEN:-$(jq -r '.token // empty' "$CONFIG_FILE" 2>/dev/null)}"
}

# Ensure we have a valid (non-expired) token. Refreshes if needed.
# Sets ARENA_TOKEN on success, exits on failure.
_ensure_token() {
  _load_config

  if [ -z "$ARENA_API_KEY" ]; then
    echo '{"error":"Not configured. Run configure.sh first."}'
    exit 1
  fi

  local needs_refresh="no"

  if [ -z "$ARENA_TOKEN" ]; then
    needs_refresh="yes"
  else
    local expiry
    expiry=$(jq -r '.tokenExpiry // empty' "$CONFIG_FILE" 2>/dev/null)
    if [ -n "$expiry" ]; then
      local expiry_epoch now_epoch
      # macOS
      expiry_epoch=$(date -j -f "%Y-%m-%dT%H:%M:%S" "${expiry%Z}" +%s 2>/dev/null)
      # Linux fallback
      [ -z "$expiry_epoch" ] && expiry_epoch=$(date -d "$expiry" +%s 2>/dev/null)
      now_epoch=$(date +%s)
      if [ -n "$expiry_epoch" ] && [ "$now_epoch" -gt "$expiry_epoch" ]; then
        needs_refresh="yes"
      fi
    fi
  fi

  if [ "$needs_refresh" = "yes" ]; then
    local login_resp token new_expiry updated
    login_resp=$(curl -s --max-time 10 -X POST "$ARENA_BASE_URL/auth/login" \
      -H "Content-Type: application/json" \
      -d "{\"apiKey\":\"$ARENA_API_KEY\"}")
    token=$(echo "$login_resp" | jq -r '.token // empty')
    if [ -z "$token" ]; then
      echo '{"error":"Login failed — check API key"}'
      exit 1
    fi
    ARENA_TOKEN="$token"
    new_expiry=$(date -u -v+7d +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u -d "+7 days" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null)
    updated=$(jq --arg t "$token" --arg e "$new_expiry" '.token = $t | .tokenExpiry = $e' "$CONFIG_FILE")
    echo "$updated" > "$CONFIG_FILE"
    chmod 600 "$CONFIG_FILE"
  fi
}

# Validate UUID format
_is_uuid() {
  echo "$1" | grep -qiE '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
}
