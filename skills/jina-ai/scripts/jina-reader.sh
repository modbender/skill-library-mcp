#!/usr/bin/env bash
# jina-reader.sh — Read any URL via Jina Reader API
#
# SECURITY MANIFEST:
#   Environment variables accessed: JINA_API_KEY (only)
#   External endpoints called: https://r.jina.ai/ (only)
#   Local files read: none
#   Local files written: none
#   Data sent: URL provided as argument + JINA_API_KEY via Authorization header
#   Data received: Markdown/JSON content via stdout
#
# Usage: jina-reader.sh <url> [--json]

set -euo pipefail

if [[ -z "${JINA_API_KEY:-}" ]]; then
  echo "Error: JINA_API_KEY environment variable is not set." >&2
  echo "Get your key at https://jina.ai/" >&2
  exit 1
fi

if [[ $# -lt 1 || "$1" == "-h" || "$1" == "--help" ]]; then
  echo "Usage: $(basename "$0") <url> [--json]"
  echo ""
  echo "Read any URL (web page or PDF) and return clean markdown."
  echo ""
  echo "Options:"
  echo "  --json    Return JSON output (includes url, title, content)"
  echo "  -h        Show this help"
  exit 0
fi

URL="$1"
ACCEPT="text/plain"

if [[ "${2:-}" == "--json" ]]; then
  ACCEPT="application/json"
fi

# Sanitize URL: percent-encode to prevent shell injection via $() or backticks
SAFE_URL=$(printf '%s' "$URL" | python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.stdin.read().strip(), safe=":/?#[]@!$&'\''()*+,;=-._~%"))')

response=$(curl -s -w "\n%{http_code}" "https://r.jina.ai/${SAFE_URL}" \
  -H "Authorization: Bearer $JINA_API_KEY" \
  -H "Accept: $ACCEPT")

http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | sed '$d')

if [[ "$http_code" -ge 400 ]]; then
  echo "Error: HTTP $http_code" >&2
  echo "$body" >&2
  exit 1
fi

echo "$body"
