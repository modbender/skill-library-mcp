#!/bin/bash
# Start QMD MCP server for multi-agent memory sharing
echo "🚀 Starting QMD MCP Server..."
echo "   All agents can now query shared memory at localhost:8181"
echo ""
qmd mcp --http --daemon
echo ""
echo "✅ MCP Server running!"
echo "   Stop with: qmd mcp stop"
echo "   Status:    qmd status"
