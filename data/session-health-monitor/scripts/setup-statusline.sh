#!/usr/bin/env bash
# session-health-monitor: setup-statusline.sh
# One-command installer for the context health statusline.
# Copies statusline.sh to ~/.claude/ and patches settings.local.json.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
SETTINGS_FILE="$CLAUDE_DIR/settings.local.json"
STATUSLINE_DEST="$CLAUDE_DIR/session-health-statusline.sh"

# Check dependencies
if ! command -v jq &>/dev/null; then
    echo "Error: jq is required but not installed."
    echo "  macOS: brew install jq"
    echo "  Linux: sudo apt-get install jq"
    exit 1
fi

# Ensure .claude directory exists
mkdir -p "$CLAUDE_DIR"

# Copy statusline script
cp "$SCRIPT_DIR/statusline.sh" "$STATUSLINE_DEST"
chmod +x "$STATUSLINE_DEST"
echo "Copied statusline.sh -> $STATUSLINE_DEST"

# Backup existing settings
if [[ -f "$SETTINGS_FILE" ]]; then
    backup="$SETTINGS_FILE.backup.$(date +%Y%m%d-%H%M%S)"
    cp "$SETTINGS_FILE" "$backup"
    echo "Backed up settings -> $backup"
else
    echo '{}' > "$SETTINGS_FILE"
    echo "Created new $SETTINGS_FILE"
fi

# Patch settings.local.json with statusLine config (preserves existing keys)
statusline_config='{"command":"bash '$STATUSLINE_DEST'"}'
tmp_file=$(mktemp)

jq --argjson sl "$statusline_config" '.statusLine = $sl' "$SETTINGS_FILE" > "$tmp_file" \
    && mv "$tmp_file" "$SETTINGS_FILE"

echo "Patched settings.local.json with statusLine config"
echo ""
echo "Setup complete! Restart Claude Code to see the statusline."
echo "Test: echo '{\"context_window\":{\"used_percentage\":42},\"session_id\":\"test\"}' | bash $STATUSLINE_DEST"
