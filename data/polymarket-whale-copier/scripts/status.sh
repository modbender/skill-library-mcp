#!/bin/bash
# Check copier status
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🐋 Whale Copier Status"
echo "====================="

if screen -list | grep -q whale-copier; then
    echo "✅ Running"
else
    echo "❌ Not running"
fi

echo ""
echo "📊 Recent activity:"
tail -10 "$SCRIPT_DIR/trades.log" 2>/dev/null || echo "No logs yet"
