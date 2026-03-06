#!/bin/bash
# UNITH API - List Available Resources
# Lists faces, voices, languages, and existing digital humans.
#
# Requires: UNITH_TOKEN (run: source scripts/auth.sh)
#
# Usage:
#   bash scripts/list-resources.sh              # list faces, voices, and heads
#   bash scripts/list-resources.sh faces         # list available faces only
#   bash scripts/list-resources.sh voices        # list available voices only
#   bash scripts/list-resources.sh heads         # list existing digital humans
#   bash scripts/list-resources.sh languages     # list supported languages
#   bash scripts/list-resources.sh head <headId> # get details for one head

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_utils.sh"

check_deps || exit 1
require_token || exit 1

AUTH_HEADER="Authorization: Bearer $UNITH_TOKEN"

# --- Resource fetchers ---

list_faces() {
  log_info "Fetching available faces (head visuals)..."

  if ! unith_curl -X GET "$API_BASE/headvisual/list" \
    -H "$AUTH_HEADER" \
    -H 'accept: application/json'; then
    parse_api_error "$CURL_BODY"
    log_error "Failed to fetch faces."
    log_error "If you see 401, your token may have expired. Re-run: source scripts/auth.sh"
    return 1
  fi

  validate_json "$CURL_BODY" "headvisual/list" || return 1

  local count
  count=$(echo "$CURL_BODY" | jq 'if type == "array" then length else 0 end')

  if [ "$count" -eq 0 ]; then
    log_warn "No faces found. Your organization may not have any head visuals assigned."
    log_warn "Contact UNITH support or check your dashboard at https://unith.ai"
    return 0
  fi

  log_ok "Found $count face(s):"
  echo "$CURL_BODY" | jq -r '
    if type == "array" then
      .[] | "  ID: \(.id // "n/a")  |  Name: \(.name // "unnamed")  |  Public: \(.public // "n/a")"
    else
      "Unexpected response format"
    end
  '
}

list_voices() {
  log_info "Fetching available voices..."

  if ! unith_curl -X GET "$API_BASE/voice/list" \
    -H "$AUTH_HEADER" \
    -H 'accept: application/json'; then
    parse_api_error "$CURL_BODY"
    log_error "Failed to fetch voices."
    return 1
  fi

  validate_json "$CURL_BODY" "voice/list" || return 1

  local count
  count=$(echo "$CURL_BODY" | jq 'if type == "array" then length else 0 end')

  if [ "$count" -eq 0 ]; then
    log_warn "No voices found. This is unexpected — check your account permissions."
    return 0
  fi

  log_ok "Found $count voice(s):"
  echo "$CURL_BODY" | jq -r '
    if type == "array" then
      .[] | "  Voice: \(.name // .id // "unnamed")  |  Provider: \(.provider // "n/a")  |  Language: \(.language // "n/a")"
    else
      "Unexpected response format"
    end
  '
}

list_heads() {
  log_info "Fetching existing digital humans..."

  if ! unith_curl -X GET "$API_BASE/head/list" \
    -H "$AUTH_HEADER" \
    -H 'accept: application/json'; then
    parse_api_error "$CURL_BODY"
    log_error "Failed to fetch digital humans."
    return 1
  fi

  validate_json "$CURL_BODY" "head/list" || return 1

  local count
  count=$(echo "$CURL_BODY" | jq 'if type == "array" then length else 0 end')

  if [ "$count" -eq 0 ]; then
    log_info "No digital humans created yet. Use POST /head/create to make one."
    return 0
  fi

  log_ok "Found $count digital human(s):"
  echo "$CURL_BODY" | jq -r '
    if type == "array" then
      .[] | "  ID: \(.id // "n/a")  |  Alias: \(.alias // "unnamed")  |  Mode: \(.operationMode // "n/a")  |  URL: \(.publicUrl // "n/a")"
    else
      "Unexpected response format"
    end
  '
}

get_head_details() {
  local head_id="$1"

  if [ -z "$head_id" ]; then
    log_error "Head ID required. Usage: $0 head <headId>"
    return 1
  fi

  log_info "Fetching details for head '$head_id'..."

  if ! unith_curl -X GET "$API_BASE/head/$head_id" \
    -H "$AUTH_HEADER" \
    -H 'accept: application/json'; then
    parse_api_error "$CURL_BODY"
    case "$CURL_HTTP_CODE" in
      404) log_error "Digital human '$head_id' not found. Check the ID with: $0 heads" ;;
      *)   log_error "Failed to fetch head details." ;;
    esac
    return 1
  fi

  validate_json "$CURL_BODY" "head/$head_id" || return 1

  log_ok "Digital human details:"
  echo "$CURL_BODY" | jq '{
    id,
    alias,
    name,
    operationMode,
    ttsVoice,
    ttsProvider,
    language,
    languageSpeechRecognition,
    greetings,
    publicId,
    publicUrl
  }'
}

list_languages() {
  log_info "Fetching supported languages..."

  if ! unith_curl -X GET "$API_BASE/languages/all" \
    -H "$AUTH_HEADER" \
    -H 'accept: application/json'; then
    parse_api_error "$CURL_BODY"
    log_error "Failed to fetch languages."
    return 1
  fi

  validate_json "$CURL_BODY" "languages/all" || return 1
  log_ok "Supported languages:"
  echo "$CURL_BODY" | jq .
}

# --- Main dispatch ---

RESOURCE="${1:-all}"

case "$RESOURCE" in
  faces)      list_faces ;;
  voices)     list_voices ;;
  heads)      list_heads ;;
  head)       get_head_details "${2:-}" ;;
  languages)  list_languages ;;
  all)
    list_faces
    echo ""
    list_voices
    echo ""
    list_heads
    ;;
  -h|--help|help)
    echo "Usage: $0 [faces|voices|heads|head <id>|languages|all]"
    echo ""
    echo "  faces       List available face visuals"
    echo "  voices      List available voices"
    echo "  heads       List existing digital humans"
    echo "  head <id>   Get details for a specific digital human"
    echo "  languages   List supported UI languages"
    echo "  all         List faces, voices, and heads (default)"
    echo ""
    echo "Environment:"
    echo "  UNITH_TOKEN          Required. Run: source scripts/auth.sh"
    echo "  UNITH_MAX_RETRIES    Max retries on failure (default: 3)"
    echo "  UNITH_RETRY_DELAY    Initial retry delay in seconds (default: 2)"
    echo "  UNITH_CURL_TIMEOUT   Curl timeout in seconds (default: 30)"
    ;;
  *)
    log_error "Unknown resource: '$RESOURCE'"
    echo "Run: $0 --help"
    exit 1
    ;;
esac
