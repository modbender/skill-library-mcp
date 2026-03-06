#!/bin/bash
# Comment on a Moltbook post
# Usage: ./comment.sh <post_id> "comment text"

set -e

POST_ID="${1:?Usage: $0 <post_id> \"comment text\"}"
TEXT="${2:?Usage: $0 <post_id> \"comment text\"}"

if [ -z "$MOLTBOOK_API_KEY" ]; then
    echo "Error: MOLTBOOK_API_KEY not set"
    exit 1
fi

if [[ ! "$POST_ID" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    echo "Error: invalid post ID"
    exit 1
fi

BODY=$(node -e "console.log(JSON.stringify({ text: process.argv[1] }))" "$TEXT")

RESPONSE=$(curl -sf --max-time 10 -X POST "https://moltbook.com/api/v1/posts/$POST_ID/comments" \
    -H "Authorization: Bearer $MOLTBOOK_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$BODY") || {
    echo "Error: request failed"; exit 1;
}

echo "💬 Comment posted on $POST_ID"
echo "$RESPONSE"
