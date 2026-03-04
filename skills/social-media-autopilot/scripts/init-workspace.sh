#!/usr/bin/env bash
# Initialize the social media workspace directory structure
set -euo pipefail

BASE_DIR="${SOCIAL_MEDIA_DIR:-$HOME/.openclaw/workspace/social-media}"

echo "Initializing social media workspace at: $BASE_DIR"

mkdir -p "$BASE_DIR"/{drafts,published,templates,analytics}

# Create calendar.json if it doesn't exist
if [ ! -f "$BASE_DIR/calendar.json" ]; then
  echo '{"posts": [], "updated_at": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' > "$BASE_DIR/calendar.json"
  echo "Created calendar.json"
fi

# Create default config if it doesn't exist
if [ ! -f "$BASE_DIR/config.json" ]; then
  cat > "$BASE_DIR/config.json" << 'EOF'
{
  "auto_approve": false,
  "default_platforms": ["x"],
  "timezone": "America/Los_Angeles",
  "posting_hours": {"start": 9, "end": 18},
  "max_posts_per_day": 5,
  "platforms": {
    "x": {"enabled": false, "api_method": "xurl"},
    "linkedin": {"enabled": false},
    "instagram": {"enabled": false}
  }
}
EOF
  echo "Created config.json"
fi

echo "✅ Social media workspace initialized"
echo ""
echo "Next steps:"
echo "  1. Edit $BASE_DIR/config.json to enable platforms"
echo "  2. Set API credentials in your environment"
echo "  3. Optionally create $BASE_DIR/brand-voice.md for tone guidelines"
