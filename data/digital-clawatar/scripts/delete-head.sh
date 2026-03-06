#!/bin/bash
# UNITH API - Delete a Digital Human
# Permanently removes a digital human and its associated resources.
#
# Requires: UNITH_TOKEN (run: source scripts/auth.sh)
#
# Usage:
#   bash scripts/delete-head.sh <headId>
#   bash scripts/delete-head.sh <headId> --confirm    # skip confirmation prompt

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_utils.sh"

check_deps || exit 1
require_token || exit 1

HEAD_ID="${1:-}"
CONFIRM="${2:-}"

if [ -z "$HEAD_ID" ]; then
  log_error "Head ID required."
  echo ""
  echo "Usage: $0 <headId> [--confirm]"
  echo ""
  echo "  headId      - The digital human ID (from list-resources.sh heads)"
  echo "  --confirm   - Skip confirmation prompt"
  echo ""
  echo "WARNING: This permanently deletes the digital human and cannot be undone."
  exit 1
fi

# --- Fetch head details for confirmation ---
log_info "Fetching details for head '$HEAD_ID'..."

if ! unith_curl -X GET "$API_BASE/head/$HEAD_ID" \
  -H "Authorization: Bearer $UNITH_TOKEN" \
  -H 'accept: application/json'; then
  parse_api_error "$CURL_BODY"
  case "$CURL_HTTP_CODE" in
    404) log_error "Digital human '$HEAD_ID' not found." ;;
    *)   log_error "Failed to fetch head details." ;;
  esac
  exit 1
fi

HEAD_ALIAS=$(echo "$CURL_BODY" | jq -r '.alias // "unnamed"' 2>/dev/null)
HEAD_MODE=$(echo "$CURL_BODY" | jq -r '.operationMode // "unknown"' 2>/dev/null)

# --- Confirmation ---
if [ "$CONFIRM" != "--confirm" ]; then
  echo ""
  log_warn "You are about to DELETE this digital human:"
  log_warn "  ID:    $HEAD_ID"
  log_warn "  Alias: $HEAD_ALIAS"
  log_warn "  Mode:  $HEAD_MODE"
  echo ""
  log_warn "This action is PERMANENT and cannot be undone."
  echo ""
  read -r -p "Type 'delete' to confirm: " RESPONSE
  if [ "$RESPONSE" != "delete" ]; then
    log_info "Cancelled."
    exit 0
  fi
fi

# --- Delete ---
log_info "Deleting digital human '$HEAD_ID' ($HEAD_ALIAS)..."

if ! unith_curl -X DELETE "$API_BASE/head/$HEAD_ID" \
  -H "Authorization: Bearer $UNITH_TOKEN" \
  -H 'accept: application/json'; then
  parse_api_error "$CURL_BODY"
  log_error "Failed to delete digital human."
  case "$CURL_HTTP_CODE" in
    404)
      log_error "Head '$HEAD_ID' not found. It may have already been deleted."
      ;;
  esac
  exit 1
fi

log_ok "Digital human '$HEAD_ID' ($HEAD_ALIAS) deleted successfully."
