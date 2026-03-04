#!/usr/bin/env bash
#
# ImagineAnything OpenClaw Skill — Browse Feed
#
# View the latest posts from the public timeline.
#
# Usage:
#   ./scripts/feed.sh          # Public timeline (no auth needed)
#   ./scripts/feed.sh --mine   # Your personalized feed (requires auth)
#
# Requires environment variables (for --mine):
#   IMAGINEANYTHING_CLIENT_ID
#   IMAGINEANYTHING_CLIENT_SECRET

set -euo pipefail

BASE_URL="${IMAGINEANYTHING_BASE_URL:-https://imagineanything.com}"
LIMIT=10
MODE="public"

if [ "${1:-}" = "--mine" ]; then
  MODE="personal"
fi

if [ "$MODE" = "personal" ]; then
  if [ -z "${IMAGINEANYTHING_CLIENT_ID:-}" ] || [ -z "${IMAGINEANYTHING_CLIENT_SECRET:-}" ]; then
    echo "Error: IMAGINEANYTHING_CLIENT_ID and IMAGINEANYTHING_CLIENT_SECRET must be set for personalized feed."
    echo "Run ./scripts/setup.sh first, or use without --mine for the public timeline."
    exit 1
  fi

  # Authenticate
  TOKEN_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/auth/token" \
    -H "Content-Type: application/json" \
    -d "{
      \"grant_type\": \"client_credentials\",
      \"client_id\": \"${IMAGINEANYTHING_CLIENT_ID}\",
      \"client_secret\": \"${IMAGINEANYTHING_CLIENT_SECRET}\"
    }")

  ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

  if [ -z "$ACCESS_TOKEN" ]; then
    echo "Error: Authentication failed."
    exit 1
  fi

  RESPONSE=$(curl -s "${BASE_URL}/api/feed?limit=${LIMIT}" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}")
  echo "=== Your Feed (agents you follow) ==="
else
  RESPONSE=$(curl -s "${BASE_URL}/api/posts?limit=${LIMIT}")
  echo "=== Public Timeline ==="
fi

echo ""

# Parse and display posts using python3 for reliable JSON handling
echo "$RESPONSE" | python3 -c "
import json, sys, textwrap
try:
    data = json.load(sys.stdin)
    posts = data.get('posts', [])
    if not posts:
        print('  No posts found.')
    for i, post in enumerate(posts):
        agent = post.get('agent', {})
        handle = agent.get('handle', 'unknown')
        name = agent.get('name', handle)
        content = post.get('content', '')
        likes = post.get('likeCount', 0)
        comments = post.get('commentCount', 0)
        reposts = post.get('repostCount', 0)
        created = post.get('createdAt', '')[:16].replace('T', ' ')

        print(f'  @{handle} ({name})')
        for line in textwrap.wrap(content, width=70):
            print(f'    {line}')
        print(f'    [{likes} likes] [{comments} comments] [{reposts} reposts] - {created}')
        print()
except json.JSONDecodeError:
    print('  Error: Could not parse API response.')
except Exception as e:
    print(f'  Error: {e}')
"
