#!/bin/bash
# meeting-prep/scripts/setup.sh — Initialize meeting-prep config and brief storage

set -euo pipefail

PREP_DIR="${PREP_DIR:-$HOME/.config/meeting-prep}"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "🎯 Meeting Prep Setup"
echo "━━━━━━━━━━━━━━━━━━━━"

# Create config directory
mkdir -p "$PREP_DIR/briefs"
echo "✓ Created $PREP_DIR"
echo "✓ Created $PREP_DIR/briefs"

# Copy example config if none exists
if [ ! -f "$PREP_DIR/config.json" ]; then
  cp "$SKILL_DIR/config.example.json" "$PREP_DIR/config.json"
  echo "✓ Created config.json (from example — edit with your calendar and preferences)"
else
  echo "• config.json already exists (skipped)"
fi

# Initialize data files
if [ ! -f "$PREP_DIR/brief-history.json" ]; then
  echo '{"events":{}}' > "$PREP_DIR/brief-history.json"
  echo "✓ Created brief-history.json"
else
  echo "• brief-history.json already exists (skipped)"
fi

if [ ! -f "$PREP_DIR/prep-log.json" ]; then
  echo '{"preps":[]}' > "$PREP_DIR/prep-log.json"
  echo "✓ Created prep-log.json"
else
  echo "• prep-log.json already exists (skipped)"
fi

# Check for gog (calendar integration)
if command -v gog &> /dev/null; then
  echo "✓ gog CLI found (calendar integration ready)"
else
  echo "⚠ gog CLI not found"
  echo "  Install gog skill for calendar integration"
fi

# Check for calendar access
if [ -f "$HOME/.config/gog/config.json" ]; then
  echo "✓ gog config found"
else
  echo "⚠ gog not configured"
  echo "  Run: gog auth login to set up calendar access"
fi

echo ""
echo "Next steps:"
echo "  1. Edit $PREP_DIR/config.json with your calendar email and preferences"
echo "  2. Ensure gog is installed and authenticated (for calendar access)"
echo "  3. Test: $(dirname "$0")/prep.sh \"test@example.com\" --dry-run"
echo "  4. Set up cron: 0 */3 * * * $(dirname "$0")/auto-prep.sh"
echo ""
echo "🎯 Meeting Prep is ready. Never walk in blind again."
