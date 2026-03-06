#!/bin/bash

# Configuration script for Zulk MCP Skill

CONFIG_PATH=""

# Detect OS and set default config path for Claude Desktop
if [[ "$OSTYPE" == "darwin"* ]]; then
    CONFIG_PATH="$HOME/Library/Application Support/Claude/app_bundle.json"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    CONFIG_PATH="$HOME/.config/Claude/app_bundle.json"
fi

echo "--- Zulk MCP Skill Configuration ---"

if [ -z "$CONFIG_PATH" ]; then
    echo "Could not automatically detect your MCP configuration file path."
    echo "Please manually add the following JSON to your agent settings:"
else
    echo "Found potential configuration path: $CONFIG_PATH"
fi

cat <<EOF
{
  "mcpServers": {
    "zulk-url-shortener": {
      "url": "https://mcp.zu.lk/mcp"
    }
  }
}
EOF

echo ""
echo "For more details, visit: https://zu.lk/-/mcp"
