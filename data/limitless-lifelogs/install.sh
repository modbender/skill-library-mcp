#!/usr/bin/env bash
# Installs the limitless_lifelogs OpenClaw skill.

set -e

SKILL_NAME="limitless_lifelogs"
SKILL_DIR="$HOME/.openclaw/workspace/skills/$SKILL_NAME"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing $SKILL_NAME skill to $SKILL_DIR ..."

mkdir -p "$SKILL_DIR"

# Copy skill files
cp "$SCRIPT_DIR/SKILL.md" "$SKILL_DIR/SKILL.md"

# Copy agents.json only if it doesn't already exist (preserve user edits)
if [ ! -f "$SKILL_DIR/agents.json" ]; then
  cp "$SCRIPT_DIR/agents.json" "$SKILL_DIR/agents.json"
  echo "  Created agents.json — edit it to add your agents."
else
  echo "  agents.json already exists, skipping (preserved your edits)."
fi

echo ""
echo "Done. Next steps:"
echo ""
echo "  1. Set your API key:"
echo "       export LIMITLESS_API_KEY=your_key_here"
echo "       # Add to ~/.zshrc or ~/.bashrc to persist it."
echo ""
echo "  2. Set your timezone (optional, defaults to UTC):"
echo "       export LIMITLESS_TIMEZONE=America/Los_Angeles"
echo ""
echo "  3. Edit your agent roster:"
echo "       \$EDITOR $SKILL_DIR/agents.json"
echo ""
echo "  4. Refresh skills in OpenClaw, then try:"
echo "       openclaw agent --message \"summarize my logs from today\""
