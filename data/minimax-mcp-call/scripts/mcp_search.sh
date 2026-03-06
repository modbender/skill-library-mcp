#!/bin/bash
# Easy wrapper for MiniMax MCP web search

# Load env from ~/.openclaw/.env
if [ -f "$HOME/.openclaw/.env" ]; then
    export $(cat $HOME/.openclaw/.env | xargs)
fi

if [ -z "$MINIMAX_API_KEY" ]; then
    echo "Error: MINIMAX_API_KEY not set"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run the Node.js MCP client
exec node "$SCRIPT_DIR/mcp_client.mjs" "$@"
