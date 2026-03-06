#!/usr/bin/env bash
set -euo pipefail

# Skytale OpenClaw Skill setup script
# Installs the skytale-sdk with MCP support

PYTHON=""
if command -v python3 &>/dev/null; then
    PYTHON="python3"
elif command -v python &>/dev/null; then
    PYTHON="python"
else
    echo "Error: python3 or python is required but not found."
    echo "Install Python 3.9+ and try again."
    exit 1
fi

echo "Using $($PYTHON --version)"
echo "Installing skytale-sdk[mcp]..."

$PYTHON -m pip install "skytale-sdk[mcp]"

echo ""
echo "Skytale SDK installed successfully."
echo ""
echo "Next steps:"
echo "  1. Get an API key at https://api.skytale.sh"
echo "  2. Set SKYTALE_API_KEY in your environment"
echo "  3. Add the skytale MCP server to your openclaw.json"
echo "     (see examples/openclaw-config.json in this skill directory)"
