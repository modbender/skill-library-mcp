#!/usr/bin/env bash
# Approve a draft post for publishing
set -euo pipefail

BASE_DIR="${SOCIAL_MEDIA_DIR:-$HOME/.openclaw/workspace/social-media}"
POST_ID="${1:-}"
[ -z "$POST_ID" ] && { echo "Usage: approve-post.sh <post-id>"; exit 1; }

DRAFT_FILE="$BASE_DIR/drafts/$POST_ID.json"
[ ! -f "$DRAFT_FILE" ] && { echo "❌ Draft not found: $POST_ID"; exit 1; }

python3 -c "
import json
with open('$DRAFT_FILE') as f:
    post = json.load(f)
post['approved'] = True
post['approved_at'] = '$(date -u +%Y-%m-%dT%H:%M:%SZ)'
with open('$DRAFT_FILE', 'w') as f:
    json.dump(post, f, indent=2)
print(f'✅ Post {post[\"id\"]} approved')
print(f'   Platforms: {\", \".join(post[\"platforms\"])}')
print(f'   Text: {post[\"text\"][:100]}...' if len(post['text']) > 100 else f'   Text: {post[\"text\"]}')
" "$DRAFT_FILE"
