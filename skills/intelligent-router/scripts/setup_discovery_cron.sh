#!/bin/bash
# Setup hourly model discovery cron job

set -e

echo "Setting up hourly model discovery cron..."

# Create cron job via OpenClaw
cat > /tmp/model-discovery-cron.json << 'EOF'
{
  "name": "Model Discovery Refresh",
  "schedule": {
    "kind": "every",
    "everyMs": 3600000
  },
  "payload": {
    "kind": "systemEvent",
    "text": "Run: bash skills/intelligent-router/scripts/auto_refresh_models.sh",
    "model": "ollama/glm-4.7-flash"
  },
  "sessionTarget": "main",
  "enabled": true
}
EOF

# Add cron job
if command -v openclaw &> /dev/null; then
    openclaw cron add --job /tmp/model-discovery-cron.json
    echo "✓ Cron job added: Model Discovery Refresh (every hour)"
    rm /tmp/model-discovery-cron.json
else
    echo "⚠️  OpenClaw CLI not found. Please run manually:"
    echo "   openclaw cron add --job /tmp/model-discovery-cron.json"
fi

echo ""
echo "Next steps:"
echo "  1. Run discovery now: python3 skills/intelligent-router/scripts/discover_models.py --auto-update"
echo "  2. Check results: cat skills/intelligent-router/discovered-models.json"
echo "  3. Monitor cron: openclaw cron list"
