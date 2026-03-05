#!/bin/bash
# FlowConcierge install bootstrap
# Run this once after installing the skill from ClaWHub

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FLOWCONCIERGE="$SCRIPT_DIR/scripts/flowconcierge.py"

echo "🦞 FlowConcierge — bootstrap installer"
echo ""

# Install scrapling
echo "📦 Installing scrapling..."
pip install scrapling -q
echo "   ✅ scrapling installed"

# Install playwright (scrapling uses it for Tier 2/3)
echo "🎭 Installing Playwright browsers (for stealth + JS tiers)..."
python3 -m playwright install chromium --quiet 2>/dev/null || true
echo "   ✅ Playwright ready"

# Create flowconcierge alias/symlink
SHELL_RC=""
if [ -f "$HOME/.zshrc" ]; then
  SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
  SHELL_RC="$HOME/.bashrc"
fi

ALIAS_LINE="alias flowconcierge='python3 $FLOWCONCIERGE'"

if [ -n "$SHELL_RC" ]; then
  if ! grep -q "alias flowconcierge=" "$SHELL_RC" 2>/dev/null; then
    echo "" >> "$SHELL_RC"
    echo "# FlowConcierge" >> "$SHELL_RC"
    echo "$ALIAS_LINE" >> "$SHELL_RC"
    echo "   ✅ Added 'flowconcierge' alias to $SHELL_RC"
    echo "   Run: source $SHELL_RC  (or open a new terminal)"
  else
    echo "   ✅ 'flowconcierge' alias already set"
  fi
else
  echo "   ℹ️  Add this to your shell profile manually:"
  echo "      $ALIAS_LINE"
fi

echo ""
echo "✅ FlowConcierge is ready!"
echo ""
echo "Quick start:"
echo "  flowconcierge setup https://yourbusiness.com \\"
echo "    --vapi-key YOUR_KEY \\"
echo "    --twilio-sid YOUR_SID \\"
echo "    --twilio-token YOUR_TOKEN"
echo ""
echo "Free from the Flow team 🦞"
