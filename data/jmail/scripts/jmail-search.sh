#!/usr/bin/env bash
# jmail-search.sh — Search Epstein email archive via jmail.world web API
# Usage: jmail-search.sh "query" [options]
#
# Options:
#   --from NAME     Filter by sender name
#   --limit N       Results per page (default: 20)
#   --page N        Page number (default: 1)
#   --source SRC    Source filter (default: all)
#
# Examples:
#   jmail-search.sh "flight manifest"
#   jmail-search.sh "scopolamine" --from "Verglas"
#   jmail-search.sh "island" --limit 50 --from "Ghislaine"

set -euo pipefail

# Parse args
QUERY=""
LIMIT=20
PAGE=1
FROM=""
SOURCE="all"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --from)   FROM="$2"; shift 2 ;;
    --limit)  LIMIT="$2"; shift 2 ;;
    --page)   PAGE="$2"; shift 2 ;;
    --source) SOURCE="$2"; shift 2 ;;
    -*)       echo "Unknown option: $1"; exit 1 ;;
    *)        QUERY="$1"; shift ;;
  esac
done

if [[ -z "$QUERY" ]]; then
  echo "Usage: jmail-search.sh \"query\" [--from NAME] [--limit N] [--page N]"
  exit 1
fi

BASE="https://jmail.world/api/emails/search"

# URL-encode safely — pass as env var, never interpolate into code
ENCODED_QUERY=$(VAL="$QUERY" python3 -c "import urllib.parse, os; print(urllib.parse.quote(os.environ['VAL']))")
URL="${BASE}?q=${ENCODED_QUERY}&limit=${LIMIT}&page=${PAGE}&source=${SOURCE}"

if [[ -n "$FROM" ]]; then
  ENCODED_FROM=$(VAL="$FROM" python3 -c "import urllib.parse, os; print(urllib.parse.quote(os.environ['VAL']))")
  URL="${URL}&from=${ENCODED_FROM}"
fi

echo "🔍 Searching: ${QUERY} (limit=${LIMIT}, page=${PAGE}${FROM:+, from=${FROM}})"
echo "   URL: ${URL}"
echo ""

RESPONSE=$(curl -sS "$URL")

if command -v jq &>/dev/null; then
  echo "$RESPONSE" | jq '.'
else
  echo "$RESPONSE"
fi
