#!/usr/bin/env bash
set -euo pipefail

# Execute Home Assistant service calls with guardrails for risky domains.
#
# Usage:
#   ./scripts/ha_safe_action.sh light turn_on light.kitchen '{"brightness_pct":60}'
#   ./scripts/ha_safe_action.sh lock unlock lock.front_door --yes
#   ./scripts/ha_safe_action.sh alarm_control_panel alarm_disarm alarm_control_panel.home --dry-run

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CALL="$SCRIPT_DIR/ha_call.sh"

DOMAIN="${1:-}"
SERVICE="${2:-}"
ENTITY_ID="${3:-}"
DATA_ARG="${4:-}"
shift $(( $# >= 4 ? 4 : $# )) || true

AUTO_YES=false
DRY_RUN=false

usage() {
  cat <<'EOF'
Usage: ha_safe_action.sh <domain> <service> <entity_id> [json_payload] [options]

Options:
  --yes         Skip confirmation prompts
  --dry-run     Print payload only, do not execute
  -h, --help    Show this help

Example:
  ha_safe_action.sh light turn_on light.kitchen '{"brightness_pct":60}'
EOF
}

err() { echo "Error: $*" >&2; }

for arg in "$@"; do
  case "$arg" in
    --yes) AUTO_YES=true ;;
    --dry-run) DRY_RUN=true ;;
    -h|--help) usage; exit 0 ;;
    *) err "Unknown option: $arg"; usage; exit 2 ;;
  esac
done

if [[ -z "$DOMAIN" || -z "$SERVICE" || -z "$ENTITY_ID" ]]; then
  usage
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  err "jq is required. Install jq and try again."
  exit 3
fi

# Validate entity format domain.object_id
if [[ "$ENTITY_ID" != *.* ]]; then
  err "entity_id must look like domain.object_id"
  exit 4
fi

ENTITY_DOMAIN="${ENTITY_ID%%.*}"
if [[ "$ENTITY_DOMAIN" != "$DOMAIN" ]]; then
  err "Domain mismatch: domain='$DOMAIN' but entity_id starts with '$ENTITY_DOMAIN'"
  exit 5
fi

# Verify entity exists and gather current state
STATE_JSON="$(mktemp)"
RESP_JSON="$(mktemp)"
trap 'rm -f "$STATE_JSON" "$RESP_JSON"' EXIT

if ! "$CALL" GET "/api/states/$ENTITY_ID" > "$STATE_JSON"; then
  err "Failed to read current state for '$ENTITY_ID'."
  err "Check entity id, HA_URL/HA_TOKEN, and Home Assistant availability."
  exit 6
fi

if ! jq empty "$STATE_JSON" >/dev/null 2>&1; then
  err "Invalid JSON while reading current state for '$ENTITY_ID'."
  head -c 400 "$STATE_JSON" >&2 || true
  exit 7
fi

if jq -e '.message? != null' "$STATE_JSON" >/dev/null 2>&1; then
  err "Home Assistant returned an API error:"
  jq -r '.message' "$STATE_JSON" >&2 || true
  exit 8
fi

CURRENT_STATE="$(jq -r '.state // "unknown"' "$STATE_JSON")"
FRIENDLY_NAME="$(jq -r '.attributes.friendly_name // ""' "$STATE_JSON")"

PAYLOAD="{}"
if [[ -n "$DATA_ARG" ]]; then
  if ! printf '%s' "$DATA_ARG" | jq -e . >/dev/null 2>&1; then
    err "json_payload is not valid JSON: $DATA_ARG"
    exit 9
  fi
  PAYLOAD="$DATA_ARG"
fi

PAYLOAD="$(jq -c --arg eid "$ENTITY_ID" '. + {entity_id: $eid}' <<<"$PAYLOAD")"

RISKY_DOMAINS=(lock alarm_control_panel cover)
RISKY=false
for d in "${RISKY_DOMAINS[@]}"; do
  if [[ "$DOMAIN" == "$d" ]]; then
    RISKY=true
    break
  fi
done

echo "Action preview:"
echo "- Entity: $ENTITY_ID${FRIENDLY_NAME:+ ($FRIENDLY_NAME)}"
echo "- Current state: $CURRENT_STATE"
echo "- Service: $DOMAIN/$SERVICE"
echo "- Payload: $PAYLOAD"

if [[ "$DRY_RUN" == true ]]; then
  echo "Dry-run enabled. No request sent."
  exit 0
fi

if [[ "$RISKY" == true && "$AUTO_YES" != true ]]; then
  echo "This action is in a risky domain ($DOMAIN)."
  read -r -p "Type YES to continue: " answer
  if [[ "$answer" != "YES" ]]; then
    echo "Cancelled."
    exit 10
  fi
fi

if ! "$CALL" POST "/api/services/$DOMAIN/$SERVICE" "$PAYLOAD" > "$RESP_JSON"; then
  err "Service call failed at transport level."
  err "Endpoint: /api/services/$DOMAIN/$SERVICE"
  exit 11
fi

if ! jq empty "$RESP_JSON" >/dev/null 2>&1; then
  err "Service response is not valid JSON."
  head -c 400 "$RESP_JSON" >&2 || true
  exit 12
fi

# HA often returns an array of changed states; also handle {message: ...} errors.
if jq -e '.message? != null' "$RESP_JSON" >/dev/null 2>&1; then
  err "Home Assistant API error:"
  jq -r '.message' "$RESP_JSON" >&2 || true
  exit 13
fi

echo "Service call accepted."

# Post-check state (best effort)
if "$CALL" GET "/api/states/$ENTITY_ID" > "$STATE_JSON" 2>/dev/null && jq empty "$STATE_JSON" >/dev/null 2>&1; then
  NEW_STATE="$(jq -r '.state // "unknown"' "$STATE_JSON")"
  echo "State after call: $NEW_STATE"
else
  echo "Warning: could not verify post-action state."
fi

echo "Response summary:"
jq -c '.' "$RESP_JSON"
