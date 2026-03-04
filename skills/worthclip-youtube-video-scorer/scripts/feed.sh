#!/usr/bin/env bash
set -euo pipefail

API_KEY="${WORTHCLIP_API_KEY:?Set WORTHCLIP_API_KEY}"
BASE="https://greedy-mallard-11.convex.site/api/v1"

# URL-encode a value (percent-encode unsafe characters)
urlencode() {
  jq -rn --arg v "$1" '$v | @uri'
}

# Parse optional flags with input validation
PARAMS=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --min-score)
      if [[ ! "$2" =~ ^[0-9]+$ ]]; then
        echo "Invalid --min-score: must be a number" >&2; exit 1
      fi
      PARAMS="${PARAMS}&minScore=$(urlencode "$2")"; shift 2 ;;
    --verdict)
      PARAMS="${PARAMS}&verdict=$(urlencode "$2")"; shift 2 ;;
    --limit)
      if [[ ! "$2" =~ ^[0-9]+$ ]]; then
        echo "Invalid --limit: must be a number" >&2; exit 1
      fi
      PARAMS="${PARAMS}&limit=$(urlencode "$2")"; shift 2 ;;
    --cursor)
      if [[ ! "$2" =~ ^[0-9]+$ ]]; then
        echo "Invalid --cursor: must be a number" >&2; exit 1
      fi
      PARAMS="${PARAMS}&cursor=$(urlencode "$2")"; shift 2 ;;
    *) echo "Unknown flag: $1" >&2; exit 1 ;;
  esac
done

# Strip leading & and prepend ?
if [ -n "$PARAMS" ]; then
  PARAMS="?${PARAMS:1}"
fi

curl -s "$BASE/feed${PARAMS}" \
  -H "Authorization: Bearer $API_KEY" | jq '.data'
