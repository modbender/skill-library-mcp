#!/usr/bin/env bash
# jina-deepsearch.sh — Deep research via Jina DeepSearch API
#
# SECURITY MANIFEST:
#   Environment variables accessed: JINA_API_KEY (only)
#   External endpoints called: https://deepsearch.jina.ai/v1/chat/completions (only)
#   Local files read: none
#   Local files written: none
#   Data sent: Research question provided as argument + JINA_API_KEY via Authorization header
#   Data received: JSON response with research answer (content extracted to stdout)
#
# Usage: jina-deepsearch.sh "<question>"

set -euo pipefail

if [[ -z "${JINA_API_KEY:-}" ]]; then
  echo "Error: JINA_API_KEY environment variable is not set." >&2
  echo "Get your key at https://jina.ai/" >&2
  exit 1
fi

if [[ $# -lt 1 || "$1" == "-h" || "$1" == "--help" ]]; then
  echo "Usage: $(basename "$0") \"<question>\""
  echo ""
  echo "Run a deep multi-step research query using Jina DeepSearch."
  echo "This uses multiple search + read + reasoning steps to answer"
  echo "complex research questions."
  echo ""
  echo "Note: DeepSearch can take 30-120 seconds depending on complexity."
  exit 0
fi

QUESTION="$1"

# Escape the question for JSON
JSON_QUESTION=$(printf '%s' "$QUESTION" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')

response=$(curl -s -w "\n%{http_code}" "https://deepsearch.jina.ai/v1/chat/completions" \
  -H "Authorization: Bearer $JINA_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"jina-deepsearch-v1\",
    \"messages\": [{\"role\": \"user\", \"content\": ${JSON_QUESTION}}],
    \"stream\": false
  }")

http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | sed '$d')

if [[ "$http_code" -ge 400 ]]; then
  echo "Error: HTTP $http_code" >&2
  echo "$body" >&2
  exit 1
fi

# Extract the content from the response
if command -v python3 &>/dev/null; then
  echo "$body" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data['choices'][0]['message']['content'])
except (KeyError, IndexError, json.JSONDecodeError):
    print(sys.stdin.read() if hasattr(sys.stdin, 'read') else '')
" 2>/dev/null || echo "$body"
else
  echo "$body"
fi
