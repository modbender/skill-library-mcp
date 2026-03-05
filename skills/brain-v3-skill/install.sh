#!/bin/bash
# ClawBrain Installation Script
# Automatically sets up hooks and dependencies for ClawdBot/OpenClaw

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_NAME="clawbrain-startup"

echo "🧠 ClawBrain Installation Script"
echo "================================"

# Detect platform
detect_platform() {
    if [ -d "$HOME/.openclaw" ]; then
        echo "openclaw"
    elif [ -d "$HOME/.clawdbot" ]; then
        echo "clawdbot"
    elif [ -d "$HOME/clawd" ]; then
        # Check if it's clawdbot or openclaw style
        if [ -f "$HOME/.clawdbot/clawdbot.json" ]; then
            echo "clawdbot"
        else
            echo "clawdbot"  # Default to clawdbot for ~/clawd
        fi
    else
        echo "unknown"
    fi
}

PLATFORM=$(detect_platform)
echo "📍 Detected platform: $PLATFORM"

# Set paths based on platform
case "$PLATFORM" in
    openclaw)
        CONFIG_DIR="$HOME/.openclaw"
        HOOKS_DIR="$HOME/.openclaw/hooks"
        SERVICE_NAME="openclaw"
        ;;
    clawdbot)
        CONFIG_DIR="$HOME/.clawdbot"
        HOOKS_DIR="$HOME/.clawdbot/hooks"
        SERVICE_NAME="clawdbot"
        ;;
    *)
        echo "❌ Could not detect ClawdBot/OpenClaw installation"
        echo "   Please ensure you have ClawdBot or OpenClaw installed first."
        exit 1
        ;;
esac

echo "📁 Config directory: $CONFIG_DIR"
echo "📁 Hooks directory: $HOOKS_DIR"

# Create hooks directory if needed
mkdir -p "$HOOKS_DIR/$HOOK_NAME"

# Copy hook files
echo "📋 Installing hook: $HOOK_NAME"
cp "$SCRIPT_DIR/hooks/$HOOK_NAME/HOOK.md" "$HOOKS_DIR/$HOOK_NAME/"
cp "$SCRIPT_DIR/hooks/$HOOK_NAME/handler.js" "$HOOKS_DIR/$HOOK_NAME/"

echo "✅ Hook installed to $HOOKS_DIR/$HOOK_NAME"

# Check Python dependencies
echo ""
echo "🐍 Checking Python dependencies..."
if ! python3 -c "import psycopg2" 2>/dev/null; then
    echo "   ⚠️  psycopg2 not installed (PostgreSQL support disabled)"
    echo "   Run: pip3 install psycopg2-binary"
fi

if ! python3 -c "import redis" 2>/dev/null; then
    echo "   ⚠️  redis not installed (Redis caching disabled)"
    echo "   Run: pip3 install redis"
fi

if ! python3 -c "import cryptography" 2>/dev/null; then
    echo "   ⚠️  cryptography not installed (encryption disabled)"
    echo "   Run: pip3 install cryptography"
fi

# Check for sentence-transformers (optional)
if ! python3 -c "import sentence_transformers" 2>/dev/null; then
    echo "   ℹ️  sentence-transformers not installed (semantic search disabled)"
fi

echo "   All dependencies are optional - SQLite works out of the box!"

# Test the installation
echo ""
echo "🧪 Testing installation..."
if python3 "$SCRIPT_DIR/scripts/brain_bridge.py" <<< '{"command": "health_check", "args": {}}' 2>/dev/null | grep -q '"success": true'; then
    echo "✅ Brain bridge is working!"
else
    echo "⚠️  Brain bridge test failed - check Python dependencies"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "🎉 ClawBrain is ready to use! Just restart your service:"
echo "   sudo systemctl restart $SERVICE_NAME"
echo ""
echo "📋 Optional Configuration (most users don't need this):"
echo "   • BRAIN_AGENT_ID - Custom agent name (default: 'default')"
echo "   • BRAIN_POSTGRES_HOST - Use PostgreSQL instead of SQLite"
echo "   • BRAIN_REDIS_HOST - Enable Redis caching"
echo ""
echo "   To set these, create: /etc/systemd/system/${SERVICE_NAME}.service.d/brain.conf"
