#!/bin/bash
# Check prerequisites for LuLu Monitor

set -e

echo "🔍 Checking prerequisites for LuLu Monitor..."
echo ""

ERRORS=0

# 1. Check LuLu Firewall
echo -n "1. LuLu Firewall: "
if [ -d "/Applications/LuLu.app" ]; then
    echo "✅ Installed"
else
    echo "❌ Not installed"
    echo "   → Install with: brew install --cask lulu"
    echo "   → Or download from: https://objective-see.org/products/lulu.html"
    ERRORS=$((ERRORS + 1))
fi

# 2. Check LuLu running
echo -n "2. LuLu Running: "
if pgrep -x "LuLu" > /dev/null; then
    echo "✅ Running"
else
    echo "⚠️  Not running"
    echo "   → Start with: open -a LuLu"
fi

# 3. Check Node.js
echo -n "3. Node.js: "
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    echo "✅ Installed ($NODE_VERSION)"
else
    echo "❌ Not installed"
    echo "   → Install with: brew install node"
    ERRORS=$((ERRORS + 1))
fi

# 4. Check Accessibility permission (can only hint, can't verify programmatically)
echo -n "4. Accessibility Permission: "
echo "⚠️  Manual check required"
echo "   → System Settings > Privacy & Security > Accessibility"
echo "   → Enable: Terminal (or your terminal app)"
echo "   → Enable: osascript"

# 5. Check OpenClaw Gateway
echo -n "5. OpenClaw Gateway: "
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:18789/health 2>/dev/null | grep -q "200"; then
    echo "✅ Running"
else
    # Try to find port from config
    OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"
    if [ -f "$OPENCLAW_CONFIG" ]; then
        PORT=$(grep -o '"port":[0-9]*' "$OPENCLAW_CONFIG" | head -1 | cut -d: -f2)
        if [ -n "$PORT" ] && curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:$PORT/health" 2>/dev/null | grep -q "200"; then
            echo "✅ Running on port $PORT"
        else
            echo "⚠️  Not running or not reachable"
            echo "   → Start OpenClaw Gateway first"
        fi
    else
        echo "⚠️  Config not found"
        echo "   → Ensure OpenClaw is installed and configured"
    fi
fi

# 6. Check Telegram configured
echo -n "6. Telegram Channel: "
OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"
if [ -f "$OPENCLAW_CONFIG" ] && grep -q '"telegram"' "$OPENCLAW_CONFIG"; then
    echo "✅ Configured"
else
    echo "⚠️  Not configured"
    echo "   → Add Telegram channel to OpenClaw config"
    echo "   → See: https://docs.openclaw.ai/channels/telegram"
fi

echo ""
if [ $ERRORS -eq 0 ]; then
    echo "✅ All critical prerequisites met! You can proceed with installation."
    exit 0
else
    echo "❌ $ERRORS critical prerequisite(s) missing. Please install them first."
    exit 1
fi
