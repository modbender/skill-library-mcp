#!/usr/bin/env bash
# =============================================================================
# kosmi-snapshot-debug.sh — Dump all interactive elements visible in the browser
#
# Use this to discover exact button names, textbox labels, and element
# roles/refs in the current Kosmi page state. Essential for calibrating
# the find_ref() patterns in other scripts.
#
# Usage:
#   ./kosmi-snapshot-debug.sh
#   ./kosmi-snapshot-debug.sh --raw   # Output raw JSON instead of formatted table
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Load .env for session name
ENV_FILE="${PLUGIN_ROOT}/.env"
if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

AGENT_BROWSER_SESSION_NAME="${AGENT_BROWSER_SESSION_NAME:-kosmi-dj-session}"
export AGENT_BROWSER_SESSION_NAME

RAW_MODE="${1:-}"

echo "[kosmi-dj-debug] Taking accessibility snapshot..."
echo ""

JSON="$(agent-browser snapshot -i -C --json 2>/dev/null)" || {
  echo "ERROR: Failed to take snapshot. Is agent-browser running? Is a page open?" >&2
  exit 1
}

SUCCESS="$(echo "$JSON" | jq -r '.success // false')"
if [[ "$SUCCESS" != "true" ]]; then
  echo "ERROR: Snapshot failed." >&2
  echo "$JSON" | jq '.' >&2
  exit 1
fi

if [[ "$RAW_MODE" == "--raw" ]]; then
  echo "$JSON" | jq '.data.refs // {}'
  exit 0
fi

# Pretty-print as a table
echo "REF ID          | ROLE           | NAME"
echo "----------------|----------------|---------------------------------------------"

echo "$JSON" | jq -r '
  .data.refs // {} | to_entries[]
  | [.key, (.value.role // "unknown"), (.value.name // "(unnamed)")]
  | @tsv
' | while IFS=$'\t' read -r ref role name; do
  printf "%-15s | %-14s | %s\n" "@$ref" "$role" "$name"
done

TOTAL="$(echo "$JSON" | jq '.data.refs // {} | length')"
echo ""
echo "Total interactive elements: $TOTAL"
echo ""
echo "Tip: Use these ref IDs and role/name values to calibrate find_ref()"
echo "     patterns in kosmi-connect.sh and kosmi-play.sh."
