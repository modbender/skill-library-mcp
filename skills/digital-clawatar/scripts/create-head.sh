#!/bin/bash
# UNITH API - Create a Digital Human
# Creates a new digital human (head) from a JSON payload file.
#
# Requires: UNITH_TOKEN (run: source scripts/auth.sh)
#
# Usage:
#   bash scripts/create-head.sh <payload.json>
#   bash scripts/create-head.sh <payload.json> --dry-run    # validate only, don't send
#
# The payload.json must contain the head creation body. See references/api-payloads.md.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_utils.sh"

check_deps || exit 1
require_token || exit 1

PAYLOAD_FILE="${1:-}"
DRY_RUN=false
if [ "${2:-}" = "--dry-run" ]; then DRY_RUN=true; fi

# --- Validate input ---
if [ -z "$PAYLOAD_FILE" ]; then
  log_error "Payload file required."
  echo ""
  echo "Usage: $0 <payload.json> [--dry-run]"
  echo ""
  echo "Example payload (ttt mode):"
  echo '  {'
  echo '    "headVisualId": "<id_from_list_faces>",'
  echo '    "alias": "My Avatar",'
  echo '    "languageSpeechRecognition": "en-US",'
  echo '    "language": "en-US",'
  echo '    "ttsProvider": "audiostack",'
  echo '    "operationMode": "ttt",'
  echo '    "ocProvider": "playground",'
  echo '    "ttsVoice": "coco",'
  echo '    "greetings": "Hello!"'
  echo '  }'
  echo ""
  echo "See references/api-payloads.md for all modes."
  exit 1
fi

if [ ! -f "$PAYLOAD_FILE" ]; then
  log_error "File not found: $PAYLOAD_FILE"
  exit 1
fi

# --- Validate JSON syntax ---
if ! jq . "$PAYLOAD_FILE" &>/dev/null; then
  log_error "Invalid JSON in $PAYLOAD_FILE"
  log_error "Fix the syntax and try again. Use 'jq . $PAYLOAD_FILE' to see the error."
  exit 1
fi

# --- Validate required fields ---
REQUIRED_FIELDS=("headVisualId" "alias" "operationMode" "ttsVoice" "ttsProvider")
MISSING=()

for field in "${REQUIRED_FIELDS[@]}"; do
  value=$(jq -r ".$field // empty" "$PAYLOAD_FILE")
  if [ -z "$value" ]; then
    MISSING+=("$field")
  fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
  log_error "Payload is missing required fields: ${MISSING[*]}"
  log_error ""
  log_error "Required fields:"
  log_error "  headVisualId        - Face ID (get from: bash scripts/list-resources.sh faces)"
  log_error "  alias               - Display name for the digital human"
  log_error "  operationMode       - One of: ttt, oc, doc_qa, voiceflow, plugin"
  log_error "  ttsVoice            - Voice name (get from: bash scripts/list-resources.sh voices)"
  log_error "  ttsProvider         - One of: elevenlabs, azure, audiostack"
  exit 1
fi

# --- Mode-specific validation ---
MODE=$(jq -r '.operationMode' "$PAYLOAD_FILE")
case "$MODE" in
  ttt|oc|doc_qa|voiceflow|plugin) ;;
  *)
    log_error "Invalid operationMode: '$MODE'"
    log_error "Must be one of: ttt, oc, doc_qa, voiceflow, plugin"
    exit 1
    ;;
esac

if [ "$MODE" = "voiceflow" ]; then
  vf_key=$(jq -r '.voiceflowApiKey // empty' "$PAYLOAD_FILE")
  if [ -z "$vf_key" ]; then
    log_error "operationMode=voiceflow requires 'voiceflowApiKey' in the payload."
    exit 1
  fi
fi

if [ "$MODE" = "plugin" ]; then
  plugin_url=$(jq -r '.pluginOperationalModeConfig.url // empty' "$PAYLOAD_FILE")
  if [ -z "$plugin_url" ]; then
    log_error "operationMode=plugin requires 'pluginOperationalModeConfig.url' in the payload."
    exit 1
  fi
fi

if [ "$MODE" = "oc" ] || [ "$MODE" = "doc_qa" ]; then
  sys_prompt=$(jq -r '.promptConfig.system_prompt // empty' "$PAYLOAD_FILE")
  if [ -z "$sys_prompt" ]; then
    log_warn "No system_prompt in promptConfig. The digital human will use default behavior."
    log_warn "Consider adding: \"promptConfig\": {\"system_prompt\": \"Your instructions here\"}"
  fi
fi

# --- Dry run ---
if [ "$DRY_RUN" = true ]; then
  log_ok "Dry run — payload is valid."
  log_info "Mode: $MODE"
  log_info "Alias: $(jq -r '.alias' "$PAYLOAD_FILE")"
  log_info "Voice: $(jq -r '.ttsVoice' "$PAYLOAD_FILE") ($(jq -r '.ttsProvider' "$PAYLOAD_FILE"))"
  if [ "$MODE" = "doc_qa" ]; then
    log_warn "After creation, you must upload a knowledge document with:"
    log_warn "  bash scripts/upload-document.sh <headId> /path/to/document.pdf"
  fi
  exit 0
fi

# --- Create ---
log_info "Creating digital human (mode: $MODE)..."

PAYLOAD=$(cat "$PAYLOAD_FILE")

if ! unith_curl -X POST "$API_BASE/head/create" \
  -H "Authorization: Bearer $UNITH_TOKEN" \
  -H 'Content-Type: application/json' \
  -H 'accept: application/json' \
  -d "$PAYLOAD"; then
  parse_api_error "$CURL_BODY"
  log_error "Failed to create digital human."
  log_error ""
  case "$CURL_HTTP_CODE" in
    400)
      log_error "Likely causes:"
      log_error "  - Invalid headVisualId (check with: bash scripts/list-resources.sh faces)"
      log_error "  - Invalid ttsVoice (check with: bash scripts/list-resources.sh voices)"
      log_error "  - Malformed payload"
      ;;
    409)
      log_error "A digital human with this name may already exist."
      log_error "Try a different 'name' value."
      ;;
  esac
  exit 1
fi

validate_json "$CURL_BODY" "head/create response" || exit 1

HEAD_ID=$(echo "$CURL_BODY" | jq -r '.id // empty')
PUBLIC_URL=$(echo "$CURL_BODY" | jq -r '.publicUrl // empty')

if [ -z "$HEAD_ID" ]; then
  log_warn "Response did not include a head ID. Full response:"
  echo "$CURL_BODY" | jq .
  exit 1
fi

log_ok "Digital human created successfully!"
echo ""
log_info "Head ID:    $HEAD_ID"
if [ -n "$PUBLIC_URL" ]; then
  log_info "Public URL: $PUBLIC_URL"
fi

# --- Post-creation guidance ---
if [ "$MODE" = "doc_qa" ]; then
  echo ""
  log_warn "NEXT STEP: Upload a knowledge document to make this digital human functional."
  log_warn "Run:"
  echo "  bash scripts/upload-document.sh $HEAD_ID /path/to/your/document.pdf"
fi

if [ "$MODE" = "ttt" ]; then
  echo ""
  log_info "This is a text-to-video head. Use the UNITH platform to generate videos."
fi

echo ""
log_info "To update later: bash scripts/update-head.sh $HEAD_ID <payload.json>"
log_info "To view details: bash scripts/list-resources.sh head $HEAD_ID"
