#!/bin/bash
# competitor-watch/scripts/setup.sh — Initialize config and data directories

set -euo pipefail

CONFIG_DIR="${CW_CONFIG_DIR:-$HOME/.config/competitor-watch}"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "🔍 Competitor Watch Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━"

# Create main config directory
mkdir -p "$CONFIG_DIR"
echo "✓ Created config directory: $CONFIG_DIR"

# Copy example config if none exists
if [ ! -f "$CONFIG_DIR/config.json" ]; then
  cp "$SKILL_DIR/config.example.json" "$CONFIG_DIR/config.json"
  echo "✓ Copied example configuration to config.json"
  echo "  ↪ Please edit this file with your competitors and settings."
else
  echo "• config.json already exists (skipped copy)"
fi

# Create data directories
mkdir -p "$CONFIG_DIR/data/snapshots"
mkdir -p "$CONFIG_DIR/reports"
echo "✓ Created data and reports directories"

# Initialize data files
for file in change-log.json last-checks.json alert-history.json; do
  if [ ! -f "$CONFIG_DIR/data/$file" ]; then
    echo '{}' > "$CONFIG_DIR/data/$file"
    echo "✓ Created empty data file: $file"
  else
    echo "• Data file $file already exists (skipped creation)"
  fi
done

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit $CONFIG_DIR/config.json to define your competitors and tiers."
echo "  2. Use the 'add-competitor.sh' script to easily add new companies."
echo "     → scripts/add-competitor.sh \"Acme Corp\" https://acme.com --tier fierce"
echo "  3. Run your first check (in dry-run mode to test):"
echo "     → scripts/check.sh --dry-run"
echo ""
echo "🎯 Your agent is now ready to watch the competition."
