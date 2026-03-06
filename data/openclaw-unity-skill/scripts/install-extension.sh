#!/bin/bash
# Install OpenClaw Unity Gateway Extension
# Usage: ./install-extension.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
EXTENSION_SRC="$SKILL_DIR/extension"
EXTENSION_DST="$HOME/.openclaw/extensions/unity"

# Check source exists
if [ ! -d "$EXTENSION_SRC" ]; then
    echo "❌ Extension source not found: $EXTENSION_SRC"
    exit 1
fi

# Create destination if needed
mkdir -p "$EXTENSION_DST"

# Copy extension files
cp -r "$EXTENSION_SRC"/* "$EXTENSION_DST"/

echo "✅ Unity extension installed to: $EXTENSION_DST"
echo ""
echo "Files:"
ls -la "$EXTENSION_DST"
echo ""
echo "Next: Restart OpenClaw gateway"
echo "  openclaw gateway restart"
