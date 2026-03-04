#!/bin/bash
# Memory Maintenance Skill - Install Script

set -e

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔧 Installing Memory Maintenance Skill..."

# Check dependencies
echo "Checking dependencies..."
if ! command -v gemini &> /dev/null; then
    echo "⚠️  Gemini CLI not found. Install with: brew install gemini-cli"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "⚠️  jq not found. Install with: brew install jq"
    exit 1
fi

# Check Gemini auth
if [ -z "$GEMINI_API_KEY" ]; then
    if [ -f "$WORKSPACE/.env" ]; then
        set -a
        source "$WORKSPACE/.env"
        set +a
    fi
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  GEMINI_API_KEY not set. Add to $WORKSPACE/.env"
    exit 1
fi

echo "✅ Dependencies OK"

# Create directories
mkdir -p "$WORKSPACE/agents/memory/archive"
mkdir -p "$WORKSPACE/agents/memory/.trash"
mkdir -p "$WORKSPACE/agents/cron"
mkdir -p "$WORKSPACE/memory/archive"

# Copy scripts
echo "Installing scripts..."
cp "$SCRIPT_DIR/review.sh" "$WORKSPACE/agents/cron/memory-maintenance-review.sh"
cp "$SCRIPT_DIR/apply.sh" "$WORKSPACE/agents/cron/memory-maintenance-apply.sh"
cp "$SCRIPT_DIR/cleanup.sh" "$WORKSPACE/agents/cron/memory-maintenance-cleanup.sh"

chmod +x "$WORKSPACE/agents/cron"/memory-maintenance-*.sh

# Install config if not exists
if [ ! -f "$WORKSPACE/skills/memory-maintenance/config/settings.json" ]; then
    echo "Creating default config..."
    mkdir -p "$WORKSPACE/skills/memory-maintenance/config"
    cat > "$WORKSPACE/skills/memory-maintenance/config/settings.json" << 'EOF'
{
  "version": "2.0.0",
  "schedule": {
    "enabled": true,
    "time": "23:00",
    "timezone": "Europe/London"
  },
  "review": {
    "lookback_days": 7,
    "gemini_model": "gemini-2.5-flash",
    "max_suggestions": 10
  },
  "maintenance": {
    "archive_after_days": 7,
    "retention_days": 30,
    "consolidate_fragments": true,
    "auto_archive_safe": true
  },
  "safety": {
    "require_approval_for_content": true,
    "require_approval_for_delete": true,
    "trash_instead_of_delete": true
  }
}
EOF
fi

# Add cron job if not exists
echo "Checking cron job..."
if ! openclaw cron list 2>/dev/null | grep -q "memory-maintenance"; then
    echo "Adding daily cron job..."
    openclaw cron add --name "memory-maintenance" \
        --schedule "0 23 * * *" \
        --command "Run memory maintenance review" \
        --model gemini
fi

echo ""
echo "✅ Memory Maintenance Skill installed!"
echo ""
echo "Next steps:"
echo "  1. Review config: $WORKSPACE/skills/memory-maintenance/config/settings.json"
echo "  2. Test manually: bash $WORKSPACE/agents/cron/memory-maintenance-review.sh"
echo "  3. Check output: $WORKSPACE/agents/memory/"
echo ""
echo "Commands:"
echo "  openclaw skill memory-maintenance review    # Run review"
echo "  openclaw skill memory-maintenance apply     # Apply changes"
echo "  openclaw skill memory-maintenance cleanup   # Run cleanup"
