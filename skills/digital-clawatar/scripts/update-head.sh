#!/bin/bash
# UNITH API - Update a Digital Human
# Modifies configuration of an existing digital human.
#
# Requires: UNITH_TOKEN (run: source scripts/auth.sh)
#
# Usage:
#   bash scripts/update-head.sh <headId> <payload.json>
#   bash scripts/update-head.sh <headId> --field ttsVoice=rachel
#   bash scripts/update-head.sh <headId> --field ttsVoice=rachel --field greetings="Hi!"
#
# The payload.json should contain only the fields to update (id is injected automatically).
# Alternatively, use --field key=value for simple single-field updates.
#
# Note: headVisualId (face) cannot be changed. Create a new head instead.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_utils.sh"

check_deps || exit 1
require_token || exit 1

HEAD_ID="${1:-}"

if [ -z "$HEAD_ID" ]; then
  log_error "Head ID required."
  echo ""
  echo "Usage: $0 <headId> <payload.json>"
  echo "       $0 <headId> --field key=value [--field key=value ...]"
  echo ""
  echo "Examples:"
  echo "  $0 abc123 updates.json"
  echo "  $0 abc123 --field ttsVoice=rachel"
  echo "  $0 abc123 --field greetings=\"Hello!\" --field ttsVoice=coco"
  echo ""
  echo "Note: headVisualId (face) cannot be changed after creation."
  exit 1
fi

shift  # consume headId

# --- Build payload from --field args or a JSON file ---
PAYLOAD=""

if [ "${1:-}" = "--field" ]; then
  # Build JSON from --field key=value pairs, starting with {"id":"<headId>"}
  PAYLOAD=$(jq -n --arg id "$HEAD_ID" '{id: $id}')

  while [ "${1:-}" = "--field" ]; do
    shift  # consume --field
    PAIR="${1:-}"
    if [ -z "$PAIR" ] || [[ ! "$PAIR" =~ = ]]; then
      log_error "Invalid --field argument: '$PAIR'. Expected key=value."
      exit 1
    fi
    KEY="${PAIR%%=*}"
    VALUE="${PAIR#*=}"
    # Use jq to safely add the field
    PAYLOAD=$(echo "$PAYLOAD" | jq --arg k "$KEY" --arg v "$VALUE" '. + {($k): $v}')
    if [ $? -ne 0 ]; then
      log_error "Failed to build JSON payload. Check your --field arguments."
      exit 1
    fi
    shift  # consume the pair
  done
else
  PAYLOAD_FILE="${1:-}"
  if [ -z "$PAYLOAD_FILE" ]; then
    log_error "Provide a payload JSON file or --field arguments."
    echo "Run: $0 --help for usage."
    exit 1
  fi

  if [ ! -f "$PAYLOAD_FILE" ]; then
    log_error "File not found: $PAYLOAD_FILE"
    exit 1
  fi

  if ! jq . "$PAYLOAD_FILE" &>/dev/null; then
    log_error "Invalid JSON in $PAYLOAD_FILE"
    exit 1
  fi

  # Inject the head ID into the payload
  PAYLOAD=$(jq --arg id "$HEAD_ID" '. + {id: $id}' "$PAYLOAD_FILE")
fi

# --- Validate no headVisualId change ---
FACE_CHANGE=$(echo "$PAYLOAD" | jq -r '.headVisualId // empty')
if [ -n "$FACE_CHANGE" ]; then
  log_error "Cannot change headVisualId (face) on an existing digital human."
  log_error "Remove 'headVisualId' from the payload, or create a new head instead."
  exit 1
fi

log_info "Updating digital human '$HEAD_ID'..."
log_info "Payload:"
echo "$PAYLOAD" | jq .

if ! unith_curl -X PUT "$API_BASE/head/update" \
  -H "Authorization: Bearer $UNITH_TOKEN" \
  -H 'Content-Type: application/json' \
  -H 'accept: application/json' \
  -d "$PAYLOAD"; then
  parse_api_error "$CURL_BODY"
  log_error "Failed to update digital human."
  case "$CURL_HTTP_CODE" in
    404)
      log_error "Head '$HEAD_ID' not found."
      log_error "Check your heads with: bash scripts/list-resources.sh heads"
      ;;
  esac
  exit 1
fi

validate_json "$CURL_BODY" "head/update response" || exit 1

log_ok "Digital human '$HEAD_ID' updated successfully."
echo ""
log_info "To verify changes: bash scripts/list-resources.sh head $HEAD_ID"
