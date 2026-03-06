#!/usr/bin/env bash
#
# resolve-library.sh — Search for a Context7-compatible library ID
#
# Usage:
#   bash resolve-library.sh --query "your question" --library-name "library-name"
#
# Environment:
#   CONTEXT7_API_KEY (optional) — API key for higher rate limits
#
# Dependencies: curl, jq

set -euo pipefail

# ── Defaults ──────────────────────────────────────────────────────────────────
QUERY=""
LIBRARY_NAME=""
API_BASE="https://context7.com/api"

# ── Parse arguments ───────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --query)
      QUERY="$2"
      shift 2
      ;;
    --library-name)
      LIBRARY_NAME="$2"
      shift 2
      ;;
    --help|-h)
      echo "Usage: bash resolve-library.sh --query \"your question\" --library-name \"library-name\""
      echo ""
      echo "Options:"
      echo "  --query          The question or task (used for relevance ranking)"
      echo "  --library-name   The library/package name to search for"
      echo "  --help, -h       Show this help message"
      echo ""
      echo "Environment:"
      echo "  CONTEXT7_API_KEY   Optional API key for higher rate limits"
      exit 0
      ;;
    *)
      echo "Error: Unknown option '$1'. Use --help for usage." >&2
      exit 1
      ;;
  esac
done

# ── Validate inputs ──────────────────────────────────────────────────────────
if [[ -z "$QUERY" ]]; then
  echo "Error: --query is required." >&2
  echo "Usage: bash resolve-library.sh --query \"your question\" --library-name \"library-name\"" >&2
  exit 1
fi

if [[ -z "$LIBRARY_NAME" ]]; then
  echo "Error: --library-name is required." >&2
  echo "Usage: bash resolve-library.sh --query \"your question\" --library-name \"library-name\"" >&2
  exit 1
fi

# ── Check dependencies ────────────────────────────────────────────────────────
for cmd in curl jq; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "Error: '$cmd' is required but not found. Please install it." >&2
    exit 1
  fi
done

# ── Build request ─────────────────────────────────────────────────────────────
AUTH_HEADER=""
if [[ -n "${CONTEXT7_API_KEY:-}" ]]; then
  AUTH_HEADER="Authorization: Bearer $CONTEXT7_API_KEY"
fi

PAYLOAD=$(jq -n \
  --arg query "$QUERY" \
  --arg libraryName "$LIBRARY_NAME" \
  '{query: $query, libraryName: $libraryName}')

# ── Make API call ─────────────────────────────────────────────────────────────
HTTP_RESPONSE=$(curl -s -w "\n%{http_code}" \
  "${API_BASE}/search" \
  -H "Content-Type: application/json" \
  ${AUTH_HEADER:+-H "$AUTH_HEADER"} \
  -d "$PAYLOAD" 2>&1) || {
  echo "Error: curl request failed." >&2
  exit 1
}

# Split response body and status code
HTTP_BODY=$(echo "$HTTP_RESPONSE" | sed '$d')
HTTP_CODE=$(echo "$HTTP_RESPONSE" | tail -n1)

# ── Handle errors ─────────────────────────────────────────────────────────────
if [[ "$HTTP_CODE" -ge 400 ]]; then
  echo "Error: API returned HTTP $HTTP_CODE" >&2
  echo "$HTTP_BODY" >&2
  exit 1
fi

# ── Format output ─────────────────────────────────────────────────────────────
# Check if results exist
RESULT_COUNT=$(echo "$HTTP_BODY" | jq -r 'if type == "array" then length elif .results then (.results | length) else 0 end' 2>/dev/null || echo "0")

if [[ "$RESULT_COUNT" == "0" ]]; then
  echo "No libraries found matching '$LIBRARY_NAME'."
  echo "Try a different or broader library name."
  exit 0
fi

echo "=== Context7 Library Search Results ==="
echo "Query: $QUERY"
echo "Library Name: $LIBRARY_NAME"
echo "Results: $RESULT_COUNT"
echo ""

# Handle both array and {results: [...]} response shapes
echo "$HTTP_BODY" | jq -r '
  (if type == "array" then . elif .results then .results else [] end) |
  to_entries[] |
  "--- Result \(.key + 1) ---",
  "Library ID: \(.value.id // .value.libraryId // "N/A")",
  "Name: \(.value.name // .value.title // "N/A")",
  "Description: \(.value.description // "N/A")",
  "Code Snippets: \(.value.codeSnippets // .value.snippetCount // "N/A")",
  "Benchmark Score: \(.value.benchmarkScore // .value.benchmark // "N/A")",
  "Source Reputation: \(.value.sourceReputation // .value.reputation // "N/A")",
  (if .value.versions then "Versions: \(.value.versions | join(", "))" else empty end),
  ""
' 2>/dev/null || {
  # Fallback: just output raw JSON if parsing fails
  echo "Raw response:"
  echo "$HTTP_BODY" | jq . 2>/dev/null || echo "$HTTP_BODY"
}
