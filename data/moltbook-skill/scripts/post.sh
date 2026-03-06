#!/bin/bash
# Post to Moltbook
# Usage: ./post.sh "Title" "Content" "submolt"

set -e

TITLE="${1:?Usage: $0 \"Title\" \"Content\" \"submolt\"}"
CONTENT="${2:?Usage: $0 \"Title\" \"Content\" \"submolt\"}"
SUBMOLT="${3:-general}"

if [ -z "$MOLTBOOK_API_KEY" ]; then
    echo "Error: MOLTBOOK_API_KEY not set"
    echo "Get your API key from Moltbook settings"
    exit 1
fi

# Build JSON safely with node
BODY=$(node -e "
console.log(JSON.stringify({
  title: process.argv[1],
  content: process.argv[2],
  submolt: process.argv[3]
}));
" "$TITLE" "$CONTENT" "$SUBMOLT")

RESPONSE=$(curl -sf --max-time 15 -X POST "https://moltbook.com/api/v1/posts" \
    -H "Authorization: Bearer $MOLTBOOK_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$BODY") || { echo "Error: request failed (HTTP error or timeout)"; exit 1; }

echo "$RESPONSE"
