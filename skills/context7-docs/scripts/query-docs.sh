#!/usr/bin/env bash
#
# query-docs.sh — Query Context7 for library documentation and code examples
#
# Usage:
#   bash query-docs.sh --library-id "/org/project" --query "your question"
#
# Environment:
#   CONTEXT7_API_KEY (optional) — API key for higher rate limits
#
# Dependencies: curl, jq

set -euo pipefail

# ── Defaults ──────────────────────────────────────────────────────────────────
LIBRARY_ID=""
QUERY=""
API_BASE="https://context7.com/api"

# ── Parse arguments ───────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --library-id)
      LIBRARY_ID="$2"
      shift 2
      ;;
    --query)
      QUERY="$2"
      shift 2
      ;;
    --help|-h)
      echo "Usage: bash query-docs.sh --library-id \"/org/project\" --query \"your question\""
      echo ""
      echo "Options:"
      echo "  --library-id   Context7 library ID (e.g., /vercel/next.js, /mongodb/docs)"
      echo "  --query        The question or task to get documentation for"
      echo "  --help, -h     Show this help message"
      echo ""
      echo "Environment:"
      echo "  CONTEXT7_API_KEY   Optional API key for higher rate limits"
      echo ""
      echo "Examples:"
      echo "  bash query-docs.sh --library-id \"/vercel/next.js\" --query \"middleware setup\""
      echo "  bash query-docs.sh --library-id \"/supabase/supabase\" --query \"authentication with email\""
      echo "  bash query-docs.sh --library-id \"/vercel/next.js/v14.3.0\" --query \"app router\""
      exit 0
      ;;
    *)
      echo "Error: Unknown option '$1'. Use --help for usage." >&2
      exit 1
      ;;
  esac
done

# ── Validate inputs ──────────────────────────────────────────────────────────
if [[ -z "$LIBRARY_ID" ]]; then
  echo "Error: --library-id is required." >&2
  echo "Usage: bash query-docs.sh --library-id \"/org/project\" --query \"your question\"" >&2
  echo "" >&2
  echo "First run resolve-library.sh to find the library ID." >&2
  exit 1
fi

if [[ -z "$QUERY" ]]; then
  echo "Error: --query is required." >&2
  echo "Usage: bash query-docs.sh --library-id \"/org/project\" --query \"your question\"" >&2
  exit 1
fi

# Validate library ID format (should start with /)
if [[ "$LIBRARY_ID" != /* ]]; then
  echo "Warning: Library ID should start with '/'. Prepending '/'." >&2
  LIBRARY_ID="/$LIBRARY_ID"
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
  --arg libraryId "$LIBRARY_ID" \
  '{query: $query, libraryId: $libraryId}')

# ── Make API call ─────────────────────────────────────────────────────────────
HTTP_RESPONSE=$(curl -s -w "\n%{http_code}" \
  "${API_BASE}/context" \
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

  if [[ "$HTTP_CODE" == "404" ]]; then
    echo "" >&2
    echo "Library '$LIBRARY_ID' was not found. Run resolve-library.sh to find the correct ID." >&2
  elif [[ "$HTTP_CODE" == "429" ]]; then
    echo "" >&2
    echo "Rate limit exceeded. Set CONTEXT7_API_KEY for higher limits." >&2
    echo "Get a free key at: https://context7.com/dashboard" >&2
  fi
  exit 1
fi

# ── Output documentation ─────────────────────────────────────────────────────
# Try to extract the text/data field; fall back to raw output
DOC_TEXT=$(echo "$HTTP_BODY" | jq -r '.data // .text // .content // empty' 2>/dev/null)

if [[ -n "$DOC_TEXT" && "$DOC_TEXT" != "null" ]]; then
  echo "=== Context7 Documentation ==="
  echo "Library: $LIBRARY_ID"
  echo "Query: $QUERY"
  echo "================================"
  echo ""
  echo "$DOC_TEXT"
else
  # If the response is plain text or a different structure, output as-is
  IS_JSON=$(echo "$HTTP_BODY" | jq empty 2>/dev/null && echo "yes" || echo "no")
  if [[ "$IS_JSON" == "yes" ]]; then
    echo "=== Context7 Documentation ==="
    echo "Library: $LIBRARY_ID"
    echo "Query: $QUERY"
    echo "================================"
    echo ""
    echo "$HTTP_BODY" | jq -r '
      if type == "array" then
        .[] | 
        (if .title then "## \(.title)\n" else "" end) +
        (if .content then .content else . end) +
        "\n---\n"
      else
        tostring
      end
    ' 2>/dev/null || echo "$HTTP_BODY"
  else
    echo "$HTTP_BODY"
  fi
fi
