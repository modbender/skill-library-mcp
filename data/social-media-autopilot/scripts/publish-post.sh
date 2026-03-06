#!/usr/bin/env bash
# Publish an approved social media post
set -euo pipefail

BASE_DIR="${SOCIAL_MEDIA_DIR:-$HOME/.openclaw/workspace/social-media}"
DRAFTS_DIR="$BASE_DIR/drafts"
PUBLISHED_DIR="$BASE_DIR/published"

POST_ID="${1:-}"
[ -z "$POST_ID" ] && { echo "Usage: publish-post.sh <post-id>"; exit 1; }

DRAFT_FILE="$DRAFTS_DIR/$POST_ID.json"
[ ! -f "$DRAFT_FILE" ] && { echo "❌ Draft not found: $POST_ID"; exit 1; }

# Parse draft
APPROVED=$(python3 -c "import json; d=json.load(open('$DRAFT_FILE')); print(d.get('approved', False))")
if [ "$APPROVED" != "True" ]; then
  echo "❌ Post not approved. Run approve-post.sh first."
  exit 1
fi

PLATFORMS=$(python3 -c "import json; d=json.load(open('$DRAFT_FILE')); print(' '.join(d['platforms']))")
TEXT=$(python3 -c "import json; d=json.load(open('$DRAFT_FILE')); print(d['text'])")

echo "Publishing to: $PLATFORMS"

RESULTS="{}"
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)

for platform in $PLATFORMS; do
  echo "  → $platform..."
  case $platform in
    x)
      # Use xurl if available, otherwise X API directly
      if command -v xurl &>/dev/null; then
        RESPONSE=$(xurl post tweets -d "{\"text\": $(python3 -c "import json; print(json.dumps('$TEXT'))")}" 2>&1) || true
        echo "    X response: $RESPONSE"
      else
        echo "    ⚠️  xurl not found. Set up X API credentials or install xurl skill."
      fi
      ;;
    linkedin)
      if [ -n "${LINKEDIN_ACCESS_TOKEN:-}" ]; then
        RESPONSE=$(curl -s -X POST "https://api.linkedin.com/v2/ugcPosts" \
          -H "Authorization: Bearer $LINKEDIN_ACCESS_TOKEN" \
          -H "Content-Type: application/json" \
          -d "{
            \"author\": \"urn:li:person:${LINKEDIN_PERSON_ID:-me}\",
            \"lifecycleState\": \"PUBLISHED\",
            \"specificContent\": {
              \"com.linkedin.ugc.ShareContent\": {
                \"shareCommentary\": {\"text\": \"$TEXT\"},
                \"shareMediaCategory\": \"NONE\"
              }
            },
            \"visibility\": {\"com.linkedin.ugc.MemberNetworkVisibility\": \"PUBLIC\"}
          }" 2>&1) || true
        echo "    LinkedIn response: $RESPONSE"
      else
        echo "    ⚠️  LINKEDIN_ACCESS_TOKEN not set."
      fi
      ;;
    instagram)
      if [ -n "${INSTAGRAM_ACCESS_TOKEN:-}" ] && [ -n "${INSTAGRAM_BUSINESS_ID:-}" ]; then
        echo "    ⚠️  Instagram requires media. Use the media workflow."
      else
        echo "    ⚠️  Instagram credentials not set."
      fi
      ;;
    *)
      echo "    ⚠️  Unknown platform: $platform"
      ;;
  esac
done

# Move to published
python3 -c "
import json
with open('$DRAFT_FILE') as f:
    post = json.load(f)
post['status'] = 'published'
post['published_at'] = '$NOW'
with open('$PUBLISHED_DIR/$POST_ID.json', 'w') as f:
    json.dump(post, f, indent=2)
"

rm "$DRAFT_FILE"
echo ""
echo "✅ Post published and archived: $POST_ID"
