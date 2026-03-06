#!/bin/bash
# Postavel MCP Setup Script
# Run this after installing the postavel skill

echo "Setting up Postavel MCP connection..."

# Check if mcporter is installed
if ! command -v mcporter &> /dev/null; then
    echo "mcporter not found. Installing..."
    
    # Try brew first
    if command -v brew &> /dev/null; then
        brew install mcporter
    else
        echo "Please install mcporter manually:"
        echo "  brew install mcporter"
        echo "  or: npm install -g mcporter"
        exit 1
    fi
fi

# Create mcporter config directory
mkdir -p ~/.config/mcporter

# Generate config for Postavel
cat > ~/.config/mcporter/postavel.json <<EOF
{
  "mcpServers": {
    "postavel": {
      "command": "mcporter",
      "args": [
        "--url", "https://postavel.com/mcp/postavel",
        "--oauth",
        "--name", "postavel"
      ]
    }
  }
}
EOF

echo "✓ mcporter configured for Postavel"
echo ""
echo "NEXT STEPS:"
echo "1. Run: mcporter --config ~/.config/mcporter/postavel.json"
echo "2. Authenticate with your Postavel account in the browser"
echo "3. Once connected, restart your OpenClaw session"
echo ""
echo "Then you can say: 'Schedule a Facebook post for tomorrow'"
