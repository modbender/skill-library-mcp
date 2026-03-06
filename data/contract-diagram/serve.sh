#!/bin/bash
# Contract Diagram Engine - Read/Write Server Launcher

ENGINE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT=8080

echo "🏴 Contract Diagram Engine starting..."
echo "Engine: $ENGINE_DIR"
echo "Port: $PORT"
echo ""
echo "Usage: http://localhost:$PORT/?md=/path/to/file.md"
echo ""
echo "Example tape:"
echo "  http://localhost:$PORT/?md=contract-skill.md"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd "$ENGINE_DIR" && node server.js
