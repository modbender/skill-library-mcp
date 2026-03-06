#!/bin/bash
# invoice-chaser/scripts/setup.sh — Initialize Invoice Chaser config and data directories

set -euo pipefail

CHASER_DIR="${CHASER_DIR:-$HOME/.config/invoice-chaser}"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "💸 Invoice Chaser Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━"

# Create config directory
mkdir -p "$CHASER_DIR"
mkdir -p "$CHASER_DIR/archives"
echo "✓ Created $CHASER_DIR"

# Copy example config if none exists
if [ ! -f "$CHASER_DIR/config.json" ]; then
  cp "$SKILL_DIR/config.example.json" "$CHASER_DIR/config.json"
  echo "✓ Created config.json (from example — edit with your business details and templates)"
else
  echo "• config.json already exists (skipped)"
fi

# Initialize data files
for file in invoices.json chase-log.json; do
  if [ ! -f "$CHASER_DIR/$file" ]; then
    if [ "$file" = "invoices.json" ]; then
      echo '{"invoices":{}}' > "$CHASER_DIR/$file"
    elif [ "$file" = "chase-log.json" ]; then
      echo '{"log":[]}' > "$CHASER_DIR/$file"
    fi
    echo "✓ Created $file"
  else
    echo "• $file already exists (skipped)"
  fi
done

# Check for gog skill and GOG_DEFAULT_ACCOUNT
if command -v gog &> /dev/null; then
    echo "✓ 'gog' skill found"
else
    echo "⚠ 'gog' skill not found. Please install it to send emails."
fi

if [ -f "$HOME/.clawdbot/secrets.env" ]; then
  if grep -q "GOG_DEFAULT_ACCOUNT" "$HOME/.clawdbot/secrets.env" 2>/dev/null; then
    echo "✓ GOG_DEFAULT_ACCOUNT found in secrets.env"
  else
    echo "⚠ GOG_DEFAULT_ACCOUNT not found in secrets.env"
    echo "  Add: GOG_DEFAULT_ACCOUNT=your-email@gmail.com to ~/.clawdbot/secrets.env"
  fi
else
  echo "⚠ ~/.clawdbot/secrets.env not found"
  echo "  Create it and add: GOG_DEFAULT_ACCOUNT=your-email@gmail.com"
fi

echo ""
echo "Next steps:"
echo "  1. Edit $CHASER_DIR/config.json with your business details"
echo "  2. Ensure GOG_DEFAULT_ACCOUNT is set correctly for sending emails"
echo "  3. Add your first invoice: $(dirname "$0")/add-invoice.sh --help"
echo ""
echo "💰 Ready to get paid."
