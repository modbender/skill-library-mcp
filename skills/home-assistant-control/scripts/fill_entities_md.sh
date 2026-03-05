#!/usr/bin/env bash
set -euo pipefail

# Generate references/entities.md from Home Assistant GET /api/states
# Usage:
#   export HA_URL_LOCAL=http://homeassistant.local:8123
#   # or export HA_URL_PUBLIC=https://your-home.example.com
#   export HA_TOKEN=...
#   ./scripts/fill_entities_md.sh
#   ./scripts/fill_entities_md.sh /custom/path/entities.md
#   ./scripts/fill_entities_md.sh --domains light,switch,climate,sensor
#   ./scripts/fill_entities_md.sh /custom/path/entities.md --domains light,switch

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CALL="$SCRIPT_DIR/ha_call.sh"
OUT_FILE="$SCRIPT_DIR/../references/entities.md"
DOMAINS=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --domains)
      DOMAINS="${2:-}"
      shift 2
      ;;
    *)
      OUT_FILE="$1"
      shift
      ;;
  esac
done

if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq is required. Install jq and try again." >&2
  exit 1
fi

TMP_JSON="$(mktemp)"
trap 'rm -f "$TMP_JSON"' EXIT

"$CALL" GET /api/states > "$TMP_JSON"

JQ_FILTER='map(select(.entity_id != null))'
if [[ -n "$DOMAINS" ]]; then
  JQ_FILTER+=" | map(select((.entity_id | split(\".\")[0]) as \$d | (\"$DOMAINS\" | split(\",\") | index(\$d))))"
fi
JQ_FILTER+=" | sort_by(.entity_id) | group_by(.entity_id | split(\".\")[0]) | .[] | \"## \" + (.[0].entity_id | split(\".\")[0] | ascii_upcase), \"\", (.[] | \"- `\" + .entity_id + \"`\" + (if (.attributes.friendly_name // \"\") != \"\" then \" — \" + .attributes.friendly_name else \"\" end)), \"\""

{
  echo "# Home Assistant Entity Map"
  echo
  echo "Auto-generated from \`GET /api/states\` on $(date '+%Y-%m-%d %H:%M:%S %Z')."
  if [[ -n "$DOMAINS" ]]; then
    echo "Filtered domains: \`$DOMAINS\`"
  fi
  echo
  jq -r "$JQ_FILTER" "$TMP_JSON"
} > "$OUT_FILE"

echo "Wrote entity map to: $OUT_FILE"