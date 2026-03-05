#!/bin/bash

# AI Bill Intelligence - macOS Launcher

cd ~/.openclaw/skills/ai-bill-intelligence

# Check if already running
if pgrep -f "node server.js" > /dev/null; then
    echo "✅ AI Bill is already running!"
    echo "🌐 Dashboard: http://localhost:8003"
    exit 0
fi

# Start services
echo "🚀 Starting AI Bill Intelligence..."
nohup node server.js > server.log 2>&1 &
nohup node collector.js > collector.log 2>&1 &

sleep 2

# Check if started
if pgrep -f "node server.js" > /dev/null; then
    echo "✅ Started!"
    echo "🌐 Dashboard: http://localhost:8003"
    echo ""
    echo "Commands:"
    echo "  View logs: tail -f ~/.openclaw/skills/ai-bill-intelligence/server.log"
    echo "  Stop: pkill -f 'node server.js'; pkill -f 'node collector.js'"
else
    echo "❌ Failed to start"
fi
