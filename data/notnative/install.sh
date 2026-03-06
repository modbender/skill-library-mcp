#!/bin/bash
set -e

echo "🧠 Installing NotNative skill..."

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "✗ Node.js is required but not installed"
    exit 1
fi

# Detect if local or remote
echo ""
echo "🔍 Detecting connection type..."

# Try localhost first
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8788/health 2>/dev/null | grep -q "200"; then
    WS_URL="ws://127.0.0.1:8788"
    echo "✓ Local NotNative detected: $WS_URL"
    IS_LOCAL=true
elif curl -s -o /dev/null -w "%{http_code}" http://localhost:8788/health 2>/dev/null | grep -q "200"; then
    WS_URL="ws://localhost:8788"
    echo "✓ Local NotNative detected: $WS_URL"
    IS_LOCAL=true
else
    # Not local, ask for URL
    echo "✗ NotNative not detected locally"
    echo ""
    read -p "Enter your NotNative WebSocket URL (e.g., ws://your-ip:8788 or wss://domain.com): " WS_URL

    if [ -z "$WS_URL" ]; then
        echo "✗ URL is required"
        exit 1
    fi

    echo "Using: $WS_URL"
    IS_LOCAL=false
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
cd "$SCRIPT_DIR"
npm install

# Make script executable
chmod +x "$SCRIPT_DIR/scripts/mcp-client.js"

# Save config
mkdir -p "$SCRIPT_DIR/.config"
echo "NOTNATIVE_WS_URL=$WS_URL" > "$SCRIPT_DIR/.config/env"

# Add to PATH in .bashrc if not already
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"
if [ ! -L "$BIN_DIR/notnative" ]; then
    ln -sf "$SCRIPT_DIR/scripts/mcp-client.js" "$BIN_DIR/notnative"
fi

if ! grep -q "NOTNATIVE_WS_URL" "$HOME/.bashrc" 2>/dev/null; then
    echo "export NOTNATIVE_WS_URL=\"$WS_URL\"" >> "$HOME/.bashrc"
fi

echo ""
echo "✅ NotNative skill installed!"
echo ""
echo "Usage:"
echo "  node scripts/mcp-client.js search <query>    # Search notes"
echo "  node scripts/mcp-client.js store <text>     # Store memory"
echo "  node scripts/mcp-client.js recall <query>   # Search memory"
echo "  node scripts/mcp-client.js tasks            # List tasks"
echo "  node scripts/mcp-client.js events          # Calendar events"
echo "  node scripts/mcp-client.js run-python <code>  # Execute Python"
echo ""
echo "Or use directly: notnative <command> [args]"
