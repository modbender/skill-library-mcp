#!/bin/bash
# UNITH API - Shared Utilities
# Source this file from other scripts: source "$(dirname "$0")/_utils.sh"

API_BASE="${API_BASE:-https://platform-api.unith.ai}"
MAX_RETRIES="${UNITH_MAX_RETRIES:-3}"
RETRY_DELAY="${UNITH_RETRY_DELAY:-2}"   # seconds, doubles each retry
CURL_TIMEOUT="${UNITH_CURL_TIMEOUT:-30}"          # max-time in seconds
CONNECT_TIMEOUT="${UNITH_CONNECT_TIMEOUT:-10}"   # connect-timeout in seconds

# --- Colors (disabled if not a terminal) ---
if [ -t 1 ]; then
  RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'; CYAN='\033[0;36m'; NC='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; CYAN=''; NC=''
fi

log_info()  { echo -e "${CYAN}[INFO]${NC} $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC} $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# --- Dependency check ---
check_deps() {
  local missing=()
  for cmd in curl jq; do
    if ! command -v "$cmd" &>/dev/null; then
      missing+=("$cmd")
    fi
  done
  if [ ${#missing[@]} -gt 0 ]; then
    log_error "Missing required commands: ${missing[*]}"
    log_error "Install them before running this skill."
    return 1
  fi
}

# --- Retry wrapper for curl ---
# Usage: unith_curl [curl args...]
# Returns: sets CURL_BODY and CURL_HTTP_CODE
unith_curl() {
  local attempt=1
  local delay="$RETRY_DELAY"
  CURL_BODY=""
  CURL_HTTP_CODE=""

  while [ "$attempt" -le "$MAX_RETRIES" ]; do
    local tmpfile
    tmpfile=$(mktemp)

    CURL_HTTP_CODE=$(curl -s -o "$tmpfile" -w '%{http_code}' \
      --connect-timeout "$CONNECT_TIMEOUT" \
      --max-time "$CURL_TIMEOUT" \
      "$@" 2>/dev/null) || CURL_HTTP_CODE="000"

    CURL_BODY=$(cat "$tmpfile")
    rm -f "$tmpfile"

    # Success: 2xx
    if [[ "$CURL_HTTP_CODE" =~ ^2[0-9]{2}$ ]]; then
      return 0
    fi

    # Non-retryable client errors: 400, 401, 403, 404, 422
    case "$CURL_HTTP_CODE" in
      400) log_error "Bad request (400). Check your payload."; return 1 ;;
      401) log_error "Unauthorized (401). Token expired or invalid credentials."
           log_error "Re-run: source scripts/auth.sh"; return 1 ;;
      403) log_error "Forbidden (403). Your account may lack access to this resource."; return 1 ;;
      404) log_error "Not found (404). Endpoint or resource does not exist."; return 1 ;;
      409) log_error "Conflict (409). A resource with this identifier may already exist."; return 1 ;;
      422) log_error "Validation error (422). Response:"
           echo "$CURL_BODY" | jq . 2>/dev/null || echo "$CURL_BODY"
           return 1 ;;
    esac

    # Retryable: 429 (rate limit), 500, 502, 503, 504, 000 (network failure)
    if [ "$attempt" -lt "$MAX_RETRIES" ]; then
      case "$CURL_HTTP_CODE" in
        429) log_warn "Rate limited (429). Waiting ${delay}s before retry ($attempt/$MAX_RETRIES)..." ;;
        000) log_warn "Network error (connection failed/timeout). Retrying in ${delay}s ($attempt/$MAX_RETRIES)..." ;;
        *)   log_warn "Server error ($CURL_HTTP_CODE). Retrying in ${delay}s ($attempt/$MAX_RETRIES)..." ;;
      esac
      sleep "$delay"
      delay=$((delay * 2))
    else
      case "$CURL_HTTP_CODE" in
        429) log_error "Rate limited (429) after $MAX_RETRIES attempts. Try again later." ;;
        000) log_error "Network failure after $MAX_RETRIES attempts. Check your internet connection and that $API_BASE is reachable." ;;
        *)   log_error "Server error ($CURL_HTTP_CODE) after $MAX_RETRIES attempts. UNITH API may be experiencing issues." ;;
      esac
      return 1
    fi

    attempt=$((attempt + 1))
  done
}

# --- Parse and display API error messages ---
# UNITH API sometimes returns { "message": "..." } or { "error": "..." }
parse_api_error() {
  local body="$1"
  local msg
  msg=$(echo "$body" | jq -r '.message // .error // .detail // empty' 2>/dev/null)
  if [ -n "$msg" ]; then
    log_error "API says: $msg"
  fi
}

# --- Require UNITH_TOKEN ---
require_token() {
  if [ -z "${UNITH_TOKEN:-}" ]; then
    log_error "UNITH_TOKEN is not set."
    log_error "Run first: source scripts/auth.sh"
    return 1
  fi
}

# --- Validate JSON response ---
# Usage: validate_json "$CURL_BODY" "description of what was expected"
validate_json() {
  local body="$1"
  local context="${2:-API response}"
  if ! echo "$body" | jq . &>/dev/null; then
    log_error "Expected valid JSON from $context but got:"
    echo "$body" | head -20
    return 1
  fi
}
