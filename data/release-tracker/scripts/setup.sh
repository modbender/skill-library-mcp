#!/usr/bin/env bash
# release-tracker setup script
# Creates config and state files, and sets up cron job
set -euo pipefail

WORKSPACE="${1:-.}"
CONFIG_FILE="${WORKSPACE}/release-tracker.json"
STATE_FILE="${WORKSPACE}/release-tracker-state.json"

# Check prerequisites
if ! command -v gh &>/dev/null; then
  echo "❌ gh CLI not found. Install: https://cli.github.com"
  exit 1
fi

if ! gh auth status &>/dev/null 2>&1; then
  echo "❌ gh not authenticated. Run: gh auth login"
  exit 1
fi

echo "✅ gh CLI ready"

# Create default config if not exists
if [ ! -f "$CONFIG_FILE" ]; then
  cat > "$CONFIG_FILE" << 'EOF'
{
  "repos": [
    {
      "owner": "openclaw",
      "repo": "openclaw",
      "displayName": "OpenClaw",
      "priorities": ["discord", "voice", "telegram", "cron", "agent"],
      "outputFormat": "text",
      "language": "en",
      "includePrerelease": false
    }
  ],
  "versionStore": "release-tracker-state.json",
  "schedule": "0 10 * * *",
  "timezone": "UTC"
}
EOF
  echo "✅ Created $CONFIG_FILE (edit to customize)"
else
  echo "ℹ️  $CONFIG_FILE already exists"
fi

# Create empty state if not exists
if [ ! -f "$STATE_FILE" ]; then
  echo "{}" > "$STATE_FILE"
  echo "✅ Created $STATE_FILE"
else
  echo "ℹ️  $STATE_FILE already exists"
fi

echo ""
echo "📝 Next steps:"
echo "  1. Edit $CONFIG_FILE to add your repos and preferences"
echo "  2. Set outputChannel for Discord delivery"
echo "  3. Ask your agent to set up the cron job using this skill"
echo "  4. Or run manually: 'check for new releases'"
