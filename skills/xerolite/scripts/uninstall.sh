#!/bin/bash
# Xerolite Skill - Uninstall Script
# Removes transform module and webhook mapping from OpenClaw config

set -e

SKILL_NAME="xerolite"
CONFIG_FILE="$HOME/.openclaw/openclaw.json"
TRANSFORMS_DIR="$HOME/.openclaw/hooks/transforms"

echo "🔧 Uninstalling $SKILL_NAME skill..."

# Check if config exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Error: OpenClaw config not found at $CONFIG_FILE"
    exit 1
fi

# Remove transform module
echo "📦 Removing transform module..."
if [ -f "$TRANSFORMS_DIR/xerolite.js" ]; then
    rm "$TRANSFORMS_DIR/xerolite.js"
    echo "✅ Removed $TRANSFORMS_DIR/xerolite.js"
else
    echo "ℹ️  Transform module not found (already removed)"
fi

# Remove xerolite mapping using node
echo "📝 Removing webhook mapping..."

node -e "
const fs = require('fs');
const config = JSON.parse(fs.readFileSync('$CONFIG_FILE', 'utf8'));

if (config.hooks?.mappings) {
  const before = config.hooks.mappings.length;
  config.hooks.mappings = config.hooks.mappings.filter(m => m.id !== 'xerolite');
  const after = config.hooks.mappings.length;
  
  if (before > after) {
    fs.writeFileSync('$CONFIG_FILE', JSON.stringify(config, null, 2));
    console.log('✅ Removed xerolite mapping');
  } else {
    console.log('ℹ️  No xerolite mapping found');
  }
} else {
  console.log('ℹ️  No mappings configured');
}
"

# Restart gateway
echo "🔄 Restarting gateway..."
openclaw gateway restart

echo ""
echo "🎉 $SKILL_NAME skill uninstalled!"
