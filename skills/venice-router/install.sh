#!/usr/bin/env bash
# install.sh — Install the venice-router skill into OpenClaw workspace
set -euo pipefail

SKILL_NAME="venice-router"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Determine target directory
if [[ -n "${OPENCLAW_WORKSPACE:-}" ]]; then
    TARGET="$OPENCLAW_WORKSPACE/skills/$SKILL_NAME"
elif [[ -d "$HOME/.openclaw/workspace/skills" ]]; then
    TARGET="$HOME/.openclaw/workspace/skills/$SKILL_NAME"
elif [[ -d "$HOME/.openclaw/skills" ]]; then
    TARGET="$HOME/.openclaw/skills/$SKILL_NAME"
else
    TARGET="$HOME/.openclaw/workspace/skills/$SKILL_NAME"
fi

echo "🦞 Installing venice-router skill..."
echo "   Target: $TARGET"

mkdir -p "$TARGET/scripts" "$TARGET/references"

cp "$SCRIPT_DIR/SKILL.md" "$TARGET/SKILL.md"
cp "$SCRIPT_DIR/scripts/venice-router.py" "$TARGET/scripts/venice-router.py"
cp "$SCRIPT_DIR/scripts/venice-router.sh" "$TARGET/scripts/venice-router.sh"
cp "$SCRIPT_DIR/references/models.md" "$TARGET/references/models.md"

chmod +x "$TARGET/scripts/venice-router.py" "$TARGET/scripts/venice-router.sh"

echo ""
echo "✅ Installed! Next steps:"
echo ""
echo "   1. Set your API key:"
echo "      export VENICE_API_KEY=\"your-key-here\""
echo ""
echo "   2. Or add to ~/.openclaw/openclaw.json:"
echo '      { "skills": { "entries": { "venice-router": { "enabled": true, "apiKey": "YOUR_KEY" } } } }'
echo ""
echo "   3. Test:"
echo "      python3 $TARGET/scripts/venice-router.py --list-models"
echo "      python3 $TARGET/scripts/venice-router.py --classify \"Design a system\""
echo ""
echo "   4. Restart OpenClaw gateway to pick up the new skill"
echo ""
