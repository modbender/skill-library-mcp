#!/usr/bin/env bash
set -euo pipefail

# Search Home Assistant entities by partial id/friendly_name.
#
# Usage:
#   ./scripts/ha_entity_find.sh kitchen
#   ./scripts/ha_entity_find.sh temp --domains sensor,climate
#   ./scripts/ha_entity_find.sh door --limit 30 --json

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CALL="$SCRIPT_DIR/ha_call.sh"

QUERY=""
DOMAINS=""
LIMIT=50
OUTPUT="table"

usage() {
  cat <<'EOF'
Usage: ha_entity_find.sh <query> [options]

Options:
  --domains <csv>   Filter by domain list (example: light,switch,sensor)
  --limit <n>       Max results (default: 50)
  --json            Print JSON output
  -h, --help        Show this help
EOF
}

err() { echo "Error: $*" >&2; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --domains)
      DOMAINS="${2:-}"
      shift 2
      ;;
    --limit)
      LIMIT="${2:-}"
      shift 2
      ;;
    --json)
      OUTPUT="json"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      if [[ -z "$QUERY" ]]; then
        QUERY="$1"
      else
        QUERY+=" $1"
      fi
      shift
      ;;
  esac
done

if [[ -z "$QUERY" ]]; then
  usage
  exit 1
fi

if ! [[ "$LIMIT" =~ ^[0-9]+$ ]] || [[ "$LIMIT" -lt 1 ]]; then
  err "--limit must be a positive integer"
  exit 2
fi

if ! command -v jq >/dev/null 2>&1; then
  err "jq is required. Install jq and try again."
  exit 3
fi

TMP_JSON="$(mktemp)"
trap 'rm -f "$TMP_JSON"' EXIT

if ! "$CALL" GET /api/states > "$TMP_JSON"; then
  err "Failed to fetch /api/states from Home Assistant."
  err "Check HA_URL/HA_TOKEN and if Home Assistant is reachable."
  exit 4
fi

if ! jq empty "$TMP_JSON" >/dev/null 2>&1; then
  err "Home Assistant response is not valid JSON (possible auth/proxy error)."
  head -c 400 "$TMP_JSON" >&2 || true
  exit 5
fi

DOMAIN_JSON='[]'
if [[ -n "$DOMAINS" ]]; then
  DOMAIN_JSON="$(printf '%s' "$DOMAINS" | jq -R 'split(",") | map(gsub("^\\s+|\\s+$"; "")) | map(select(length>0))')"
fi

if [[ "$OUTPUT" == "json" ]]; then
  jq --arg q "$QUERY" --argjson domains "$DOMAIN_JSON" --argjson limit "$LIMIT" '
    ( $q | ascii_downcase ) as $qnorm
    | [ .[]
        | select(.entity_id != null)
        | . as $e
        | ($e.entity_id | split(".")[0]) as $domain
        | ($e.attributes.friendly_name // "") as $fname
        | (($e.entity_id + " " + $fname) | ascii_downcase) as $hay
        | select($hay | contains($qnorm))
        | select(($domains | length == 0) or ($domains | index($domain)))
        | {
            entity_id: $e.entity_id,
            domain: $domain,
            state: ($e.state // "unknown"),
            friendly_name: $fname
          }
      ]
    | sort_by(.entity_id)
    | .[:$limit]
  ' "$TMP_JSON"
else
  jq -r --arg q "$QUERY" --argjson domains "$DOMAIN_JSON" --argjson limit "$LIMIT" '
    ( $q | ascii_downcase ) as $qnorm
    | [ .[]
        | select(.entity_id != null)
        | . as $e
        | ($e.entity_id | split(".")[0]) as $domain
        | ($e.attributes.friendly_name // "") as $fname
        | (($e.entity_id + " " + $fname) | ascii_downcase) as $hay
        | select($hay | contains($qnorm))
        | select(($domains | length == 0) or ($domains | index($domain)))
        | {
            entity_id: $e.entity_id,
            domain: $domain,
            state: ($e.state // "unknown"),
            friendly_name: $fname
          }
      ]
    | sort_by(.entity_id)
    | .[:$limit]
    | if length == 0 then
        "No entities found."
      else
        ("Found " + (length|tostring) + " entities:"),
        "",
        (.[] | "- `" + .entity_id + "` [" + .domain + "] state=`" + .state + "`" + (if .friendly_name != "" then " — " + .friendly_name else "" end))
      end
  ' "$TMP_JSON"
fi
