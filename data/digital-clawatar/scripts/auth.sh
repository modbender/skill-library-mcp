#!/bin/bash
# UNITH API Authentication Helper
# Obtains a bearer token and stores it for subsequent API calls.
#
# Requires environment variables:
#   UNITH_EMAIL       - Your UNITH account email
#   UNITH_SECRET_KEY  - Your UNITH secret key
#
# Optional environment variables:
#   UNITH_MAX_RETRIES   - Max retry attempts (default: 3)
#   UNITH_RETRY_DELAY   - Initial retry delay in seconds (default: 2)
#   UNITH_CURL_TIMEOUT  - Curl timeout in seconds (default: 30)
#
# Usage: source scripts/auth.sh
# After running, UNITH_TOKEN is exported and available.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_utils.sh"

check_deps || { return 1 2>/dev/null || exit 1; }

# --- Validate credentials ---
if [ -z "${UNITH_EMAIL:-}" ]; then
  log_error "UNITH_EMAIL is not set."
  log_error "  export UNITH_EMAIL='your@email.com'"
  log_error ""
  log_error "Get your account at https://unith.ai"
  return 1 2>/dev/null || exit 1
fi

if [ -z "${UNITH_SECRET_KEY:-}" ]; then
  log_error "UNITH_SECRET_KEY is not set."
  log_error "  export UNITH_SECRET_KEY='your_secret_key'"
  log_error ""
  log_error "Generate it at: UNITH dashboard → Manage Account → Secret Key → Generate"
  log_error "The key is shown only once. If lost, delete and regenerate."
  return 1 2>/dev/null || exit 1
fi

# Basic format sanity check
if [[ ! "$UNITH_EMAIL" =~ ^[^@]+@[^@]+\.[^@]+$ ]]; then
  log_warn "UNITH_EMAIL ('$UNITH_EMAIL') does not look like a valid email address."
fi

# --- Token caching ---
# Cache file stores: email \t token \t timestamp (epoch seconds)
# Token is valid for 7 days; we reuse if less than 6 days old to give margin.
TOKEN_CACHE="${UNITH_TOKEN_CACHE-/tmp/.unith_token_cache}"
CACHE_MAX_AGE=$((6 * 24 * 60 * 60))  # 6 days in seconds

if [ -n "$TOKEN_CACHE" ] && [ -f "$TOKEN_CACHE" ]; then
  CACHED_EMAIL=$(cut -f1 "$TOKEN_CACHE" 2>/dev/null || echo "")
  CACHED_TOKEN=$(cut -f2 "$TOKEN_CACHE" 2>/dev/null || echo "")
  CACHED_TIME=$(cut -f3 "$TOKEN_CACHE" 2>/dev/null || echo "0")
  NOW=$(date +%s)
  AGE=$((NOW - CACHED_TIME))

  if [ "$CACHED_EMAIL" = "$UNITH_EMAIL" ] && [ -n "$CACHED_TOKEN" ] && [ "$AGE" -lt "$CACHE_MAX_AGE" ]; then
    export UNITH_TOKEN="$CACHED_TOKEN"
    REMAINING_DAYS=$(( (CACHE_MAX_AGE - AGE) / 86400 + 1 ))
    log_ok "Reusing cached token (valid ~${REMAINING_DAYS} more days). To force refresh: rm $TOKEN_CACHE"
    return 0 2>/dev/null || exit 0
  fi
fi

log_info "Authenticating with UNITH API as $UNITH_EMAIL..."

unith_curl -X POST "$API_BASE/auth/token" \
  -H 'Content-Type: application/json' \
  -H 'accept: application/json' \
  -d "$(jq -n --arg e "$UNITH_EMAIL" --arg k "$UNITH_SECRET_KEY" '{email:$e, secretkey:$k}')"

if [ $? -ne 0 ]; then
  parse_api_error "$CURL_BODY"
  log_error "Authentication failed."
  log_error ""
  log_error "Common causes:"
  log_error "  1. Wrong email or secret key"
  log_error "  2. Secret key was regenerated (old one is invalidated)"
  log_error "  3. Account not yet activated"
  log_error ""
  log_error "Verify at: UNITH dashboard → Manage Account"
  return 1 2>/dev/null || exit 1
fi

validate_json "$CURL_BODY" "auth/token" || { return 1 2>/dev/null || exit 1; }

TOKEN=$(echo "$CURL_BODY" | jq -r '.token // empty')

if [ -z "$TOKEN" ]; then
  log_error "Auth response did not contain a token."
  log_error "Full response:"
  echo "$CURL_BODY" | jq . 2>/dev/null || echo "$CURL_BODY"
  return 1 2>/dev/null || exit 1
fi

export UNITH_TOKEN="$TOKEN"

# Write to cache
if [ -n "$TOKEN_CACHE" ]; then
  printf '%s\t%s\t%s\n' "$UNITH_EMAIL" "$TOKEN" "$(date +%s)" > "$TOKEN_CACHE"
  chmod 600 "$TOKEN_CACHE"
fi

log_ok "Authenticated successfully. Token stored in UNITH_TOKEN (valid 7 days)."
