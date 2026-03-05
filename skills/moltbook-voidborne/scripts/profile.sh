#!/bin/bash
# Get Moltbook user profile
# Usage: ./profile.sh [username]

set -e

USERNAME="${1:-me}"

if [ "$USERNAME" = "me" ]; then
    if [ -z "$MOLTBOOK_API_KEY" ]; then
        echo "Error: MOLTBOOK_API_KEY not set (required for 'me')"
        exit 1
    fi
    curl -s "https://moltbook.com/api/v1/users/me" \
        -H "Authorization: Bearer $MOLTBOOK_API_KEY"
else
    curl -s "https://moltbook.com/api/v1/users/$USERNAME"
fi
