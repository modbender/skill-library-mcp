#!/bin/bash
# Xerolite Skill - Install Script
# Installs transform module and adds webhook mapping to OpenClaw config

set -e

SKILL_NAME="xerolite"
CONFIG_FILE="$HOME/.openclaw/openclaw.json"
TRANSFORMS_DIR="$HOME/.openclaw/hooks/transforms"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "🔧 Installing $SKILL_NAME skill..."

# Check if config exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Error: OpenClaw config not found at $CONFIG_FILE"
    exit 1
fi

# Create transforms directory if it doesn't exist
echo "📁 Setting up transforms directory..."
mkdir -p "$TRANSFORMS_DIR"

# Copy transform module
echo "📦 Installing transform module..."
cp "$SKILL_DIR/transforms/xerolite.js" "$TRANSFORMS_DIR/"
echo "✅ Copied xerolite.js to $TRANSFORMS_DIR/"

# Add xerolite mapping using node
echo "📝 Adding webhook mapping..."

node -e "
const fs = require('fs');
const config = JSON.parse(fs.readFileSync('$CONFIG_FILE', 'utf8'));

// Ensure hooks structure exists
if (!config.hooks) config.hooks = {};
if (!config.hooks.enabled) config.hooks.enabled = true;
if (!config.hooks.mappings) config.hooks.mappings = [];

// Set transforms directory
config.hooks.transformsDir = '$TRANSFORMS_DIR';

// Xerolite mapping with transform module
const xeroliteMapping = {
  id: 'xerolite',
  match: { path: 'xerolite' },
  transform: { module: 'xerolite.js' }
};

// Check if xerolite mapping already exists
const existingIndex = config.hooks.mappings.findIndex(m => m.id === 'xerolite');

if (existingIndex >= 0) {
  config.hooks.mappings[existingIndex] = xeroliteMapping;
  console.log('✅ Updated existing xerolite mapping');
} else {
  config.hooks.mappings.push(xeroliteMapping);
  console.log('✅ Added xerolite mapping');
}

fs.writeFileSync('$CONFIG_FILE', JSON.stringify(config, null, 2));
"

# Restart gateway
echo "🔄 Restarting gateway..."
openclaw gateway restart

echo ""
echo "✅ Transform module installed: $TRANSFORMS_DIR/xerolite.js"
echo ""
echo "📋 Webhook endpoint ready:"
echo "   POST http://localhost:18789/hooks/xerolite"
echo "   Header: Authorization: Bearer <your-hooks-token>"
echo ""
echo "🎉 $SKILL_NAME skill installed!"
