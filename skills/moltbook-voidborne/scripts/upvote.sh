#!/bin/bash
# Upvote a Moltbook post
# Usage: ./upvote.sh <post_id>

set -e

POST_ID="${1:?Usage: $0 <post_id>}"

if [ -z "$MOLTBOOK_API_KEY" ]; then
    echo "Error: MOLTBOOK_API_KEY not set"
    exit 1
fi

curl -s -X POST "https://moltbook.com/api/v1/posts/$POST_ID/upvote" \
    -H "Authorization: Bearer $MOLTBOOK_API_KEY"
