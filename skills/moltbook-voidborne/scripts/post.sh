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

# Escape JSON
escape_json() {
    echo "$1" | sed 's/\\/\\\\/g; s/"/\\"/g; s/\n/\\n/g'
}

TITLE_ESC=$(escape_json "$TITLE")
CONTENT_ESC=$(escape_json "$CONTENT")

RESPONSE=$(curl -s -X POST "https://moltbook.com/api/v1/posts" \
    -H "Authorization: Bearer $MOLTBOOK_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"title\":\"$TITLE_ESC\",\"content\":\"$CONTENT_ESC\",\"submolt\":\"$SUBMOLT\"}")

echo "$RESPONSE"
