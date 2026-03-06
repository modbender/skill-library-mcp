#!/bin/bash
# Validation library for social-post

# Farcaster byte limit (10% safety buffer applied)
FARCASTER_BYTE_LIMIT=288  # 320 - 10% = 288

# Load tier detection library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/tier-detection.sh"

# Check Twitter character count (dynamic limit based on account tier)
validate_twitter() {
  local text="$1"
  local account="${TWITTER_ACCOUNT:-mr_crtee}"
  local force_refresh="${2:-false}"
  
  local char_count=${#text}
  local twitter_limit=$(get_twitter_char_limit_buffered "$account" "$force_refresh")
  
  if [ "$char_count" -gt "$twitter_limit" ]; then
    echo "❌ Twitter: $char_count/$twitter_limit characters (over by $(($char_count - $twitter_limit)))" >&2
    return 1
  else
    echo "✅ Twitter: $char_count/$twitter_limit characters" >&2
    return 0
  fi
}

# Check Farcaster byte count (UTF-8)
validate_farcaster() {
  local text="$1"
  local byte_count=$(echo -n "$text" | wc -c)
  
  if [ "$byte_count" -gt "$FARCASTER_BYTE_LIMIT" ]; then
    echo "❌ Farcaster: $byte_count/$FARCASTER_BYTE_LIMIT bytes (over by $(($byte_count - $FARCASTER_BYTE_LIMIT)))" >&2
    return 1
  else
    echo "✅ Farcaster: $byte_count/$FARCASTER_BYTE_LIMIT bytes" >&2
    return 0
  fi
}

# Truncate text to fit platform
truncate_for_twitter() {
  local text="$1"
  local account="${TWITTER_ACCOUNT:-mr_crtee}"
  local twitter_limit=$(get_twitter_char_limit_buffered "$account")
  
  if [ "${#text}" -gt "$twitter_limit" ]; then
    echo "${text:0:$((twitter_limit-3))}..."
  else
    echo "$text"
  fi
}

truncate_for_farcaster() {
  local text="$1"
  local byte_count=$(echo -n "$text" | wc -c)
  
  if [ "$byte_count" -gt "$FARCASTER_BYTE_LIMIT" ]; then
    # Simple truncation (not perfect for multi-byte chars, but safe)
    local cutoff=$((FARCASTER_BYTE_LIMIT - 3))
    echo "${text:0:$cutoff}..."
  else
    echo "$text"
  fi
}

# Validate both platforms
validate_both() {
  local text="$1"
  local twitter_ok=0
  local farcaster_ok=0
  
  validate_twitter "$text" && twitter_ok=1
  validate_farcaster "$text" && farcaster_ok=1
  
  if [ "$twitter_ok" -eq 1 ] && [ "$farcaster_ok" -eq 1 ]; then
    return 0
  else
    return 1
  fi
}
