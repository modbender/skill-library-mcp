#!/bin/bash
# Get Moltbook user profile
# Usage: ./profile.sh [username] [--json]

set -e

USERNAME="${1:-me}"
JSON_MODE=false
[[ "${1:-}" == "--json" ]] && { USERNAME="me"; JSON_MODE=true; }
[[ "${2:-}" == "--json" ]] && JSON_MODE=true

if [ "$USERNAME" = "me" ]; then
    if [ -z "$MOLTBOOK_API_KEY" ]; then
        echo "Error: MOLTBOOK_API_KEY not set (required for 'me')"
        exit 1
    fi
    RESPONSE=$(curl -sf --max-time 10 "https://moltbook.com/api/v1/users/me" \
        -H "Authorization: Bearer $MOLTBOOK_API_KEY") || {
        echo "Error: request failed"; exit 1;
    }
else
    if [[ ! "$USERNAME" =~ ^[a-zA-Z0-9_-]+$ ]]; then
        echo "Error: invalid username"
        exit 1
    fi
    RESPONSE=$(curl -sf --max-time 10 "https://moltbook.com/api/v1/users/$USERNAME") || {
        echo "Error: request failed"; exit 1;
    }
fi

if [[ "$JSON_MODE" == true ]]; then
    echo "$RESPONSE"
else
    echo "$RESPONSE" | node -e "
const u = JSON.parse(require('fs').readFileSync(0, 'utf8'));
if (u.error) { console.log('Error:', u.error); process.exit(1); }
console.log(\`👤 @\${u.username || u.name || 'unknown'}\`);
if (u.bio) console.log(\`📝 \${u.bio}\`);
if (u.posts !== undefined) console.log(\`📊 Posts: \${u.posts} | Upvotes: \${u.upvotes || 0}\`);
if (u.joined) console.log(\`📅 Joined: \${u.joined}\`);
"
fi
