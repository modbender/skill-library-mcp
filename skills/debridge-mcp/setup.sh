#!/bin/bash
# deBridge MCP Setup Script for OpenClaw

set -e

echo "🦞 Installing deBridge MCP for OpenClaw..."

# Check if already installed
if [ -d "$HOME/debridge-mcp" ]; then
    echo "deBridge MCP already cloned at ~/debridge-mcp"
else
    echo "Cloning deBridge MCP..."
    git clone https://github.com/debridge-finance/debridge-mcp.git ~/debridge-mcp
fi

cd ~/debridge-mcp
echo "Installing dependencies..."
npm install
echo "Building..."
npm run build

# Check if MCP adapter exists
if ! grep -q "mcp-adapter" ~/.openclaw/openclaw.json 2>/dev/null; then
    echo "Adding MCP adapter to OpenClaw config..."
    # Backup first
    cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak.$(date +%Y%m%d)
    
    # Add MCP config (simplified - user may need to manually merge)
    echo "⚠️ Manual step needed: Add MCP adapter config to openclaw.json"
    echo "See: ~/.openclaw/workspace/skills/debridge-mcp/SKILL.md"
else
    echo "MCP adapter already configured"
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Restart OpenClaw: openclaw gateway restart"
echo "2. Verify: openclaw plugins list"