#!/bin/bash

echo "📊 OpenClaw Menu Bar Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if running
if pgrep -f "openclaw-menubar.*electron" > /dev/null; then
    PID=$(pgrep -f "openclaw-menubar.*electron")
    echo "Status: ✅ Running"
    echo "PID: $PID"
    
    # Get memory usage
    MEM=$(ps -o rss= -p $PID | awk '{printf "%.1f MB", $1/1024}')
    echo "Memory: $MEM"
else
    echo "Status: ❌ Not running"
    echo ""
    echo "Start with: scripts/start.sh"
fi

echo ""

# Check OpenClaw Gateway
echo "OpenClaw Gateway"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if curl -s http://localhost:18789/health > /dev/null 2>&1; then
    echo "Status: ✅ Running"
else
    echo "Status: ❌ Not running"
    echo "Start with: openclaw gateway start"
fi
