#!/usr/bin/env bash
# Create a new social media post draft
set -euo pipefail

BASE_DIR="${SOCIAL_MEDIA_DIR:-$HOME/.openclaw/workspace/social-media}"
DRAFTS_DIR="$BASE_DIR/drafts"

usage() {
  echo "Usage: draft-post.sh --platform <x|linkedin|instagram|all> --text \"Post content\" [--media path] [--schedule \"datetime\"] [--tags tag1,tag2] [--thread]"
  exit 1
}

PLATFORMS=""
TEXT=""
MEDIA=""
SCHEDULE=""
TAGS=""
THREAD="false"

while [[ $# -gt 0 ]]; do
  case $1 in
    --platform) PLATFORMS="$2"; shift 2 ;;
    --text) TEXT="$2"; shift 2 ;;
    --media) MEDIA="$2"; shift 2 ;;
    --schedule) SCHEDULE="$2"; shift 2 ;;
    --tags) TAGS="$2"; shift 2 ;;
    --thread) THREAD="true"; shift ;;
    *) usage ;;
  esac
done

[ -z "$PLATFORMS" ] || [ -z "$TEXT" ] && usage

# Generate UUID
POST_ID=$(uuidgen 2>/dev/null || python3 -c "import uuid; print(uuid.uuid4())")

# Expand "all" to individual platforms
if [ "$PLATFORMS" = "all" ]; then
  PLATFORMS_JSON='["x", "linkedin", "instagram"]'
else
  PLATFORMS_JSON=$(echo "$PLATFORMS" | tr ',' '\n' | sed 's/^/"/;s/$/"/' | paste -sd',' - | sed 's/^/[/;s/$/]/')
fi

# Handle media
MEDIA_JSON="[]"
if [ -n "$MEDIA" ]; then
  MEDIA_JSON="[\"$MEDIA\"]"
fi

# Handle schedule
SCHEDULE_JSON="null"
if [ -n "$SCHEDULE" ]; then
  # Try to parse the date
  SCHEDULE_JSON="\"$(date -jf "%Y-%m-%d %H:%M %Z" "$SCHEDULE" +%Y-%m-%dT%H:%M:%S%z 2>/dev/null || echo "$SCHEDULE")\""
fi

# Handle tags
TAGS_JSON="[]"
if [ -n "$TAGS" ]; then
  TAGS_JSON=$(echo "$TAGS" | tr ',' '\n' | sed 's/^/"/;s/$/"/' | paste -sd',' - | sed 's/^/[/;s/$/]/')
fi

NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)

cat > "$DRAFTS_DIR/$POST_ID.json" << EOF
{
  "id": "$POST_ID",
  "platforms": $PLATFORMS_JSON,
  "text": $(python3 -c "import json; print(json.dumps('''$TEXT'''))"),
  "media": $MEDIA_JSON,
  "scheduled_at": $SCHEDULE_JSON,
  "status": "draft",
  "created_at": "$NOW",
  "approved": false,
  "tags": $TAGS_JSON,
  "thread": $THREAD
}
EOF

echo "✅ Draft created: $POST_ID"
echo "   Platforms: $PLATFORMS"
echo "   File: $DRAFTS_DIR/$POST_ID.json"

if [ -n "$SCHEDULE" ]; then
  echo "   Scheduled: $SCHEDULE"
  # Add to calendar
  python3 -c "
import json
cal_path = '$BASE_DIR/calendar.json'
with open(cal_path) as f:
    cal = json.load(f)
cal['posts'].append({'id': '$POST_ID', 'scheduled_at': $SCHEDULE_JSON, 'status': 'draft'})
cal['updated_at'] = '$NOW'
with open(cal_path, 'w') as f:
    json.dump(cal, f, indent=2)
"
  echo "   Added to calendar"
fi
