#!/bin/bash
# Browser Control - Start all services

set -e

SKILL_DIR=~/.openclaw/skills/browser-control
CONFIG_FILE=$SKILL_DIR/config.json
NGROK_CONFIG=$SKILL_DIR/ngrok-config.json
TOOLS_FILE=~/.openclaw/workspace/TOOLS.md
VNC_PASSWORD=$(cat $SKILL_DIR/vnc-password 2>/dev/null || echo "")

echo "🖥️  Browser Control - Starting..."
echo ""

# Check ngrok config
if [ ! -f "$NGROK_CONFIG" ]; then
    echo "❌ ngrok not configured. Run install.sh first."
    exit 1
fi

ALLOWED_EMAIL=$(jq -r '.email' "$NGROK_CONFIG")
if [ -z "$ALLOWED_EMAIL" ] || [ "$ALLOWED_EMAIL" = "null" ]; then
    echo "❌ No email configured. Run install.sh first."
    exit 1
fi

#######################################
# DETECT OS
#######################################

if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="mac"
    VNC_PORT=5900
    NOVNC_WEB="$SKILL_DIR/novnc"
    # Fallback to Homebrew paths if skill dir doesn't have it
    [ ! -d "$NOVNC_WEB" ] && NOVNC_WEB=$(brew --prefix 2>/dev/null)/share/novnc
    [ ! -d "$NOVNC_WEB" ] && NOVNC_WEB="/opt/homebrew/share/novnc"
    [ ! -d "$NOVNC_WEB" ] && NOVNC_WEB="/usr/local/share/novnc"
else
    OS="linux"
    VNC_PORT=5901
    NOVNC_WEB="/usr/share/novnc"
fi

#######################################
# START VNC (Linux only)
#######################################

if [[ "$OS" == "linux" ]]; then
    if pgrep -f "Xtightvnc.*:1" > /dev/null; then
        echo "✅ VNC already running"
    else
        echo "🖥️  Starting VNC server..."
        vncserver -kill :1 2>/dev/null || true
        vncserver :1 -geometry 1280x800 -depth 24
        sleep 2
        echo "✅ VNC started on display :1"
    fi
fi

if [[ "$OS" == "mac" ]]; then
    if ! pgrep -x "screensharingd" > /dev/null; then
        echo "⚠️  Screen Sharing doesn't seem to be running."
        echo "   Enable it in System Preferences → Sharing → Screen Sharing"
    else
        echo "✅ Screen Sharing is running"
    fi
    
    if ! pgrep -f "remote-debugging-port=9222" > /dev/null; then
        echo "🌐 Starting Chrome with remote debugging..."
        $SKILL_DIR/start-chrome.sh
        sleep 2
    else
        echo "✅ Chrome already running with remote debugging"
    fi
fi

#######################################
# START NOVNC
#######################################

echo "🌐 Starting noVNC..."
pkill -f "websockify.*6080" 2>/dev/null || true
sleep 1

if [ ! -d "$NOVNC_WEB" ]; then
    echo "❌ noVNC not found at $NOVNC_WEB"
    exit 1
fi

# Try websockify command, fallback to python module
if command -v websockify &> /dev/null; then
    websockify --web=$NOVNC_WEB 6080 localhost:$VNC_PORT &
else
    python3 -m websockify --web=$NOVNC_WEB 6080 localhost:$VNC_PORT &
fi
WEBSOCKIFY_PID=$!
sleep 2

if ! kill -0 $WEBSOCKIFY_PID 2>/dev/null; then
    echo "❌ Failed to start noVNC"
    exit 1
fi
echo "✅ noVNC started on port 6080"

#######################################
# START NGROK TUNNEL
#######################################

echo "🚇 Starting ngrok tunnel with Google OAuth..."
echo "   Only $ALLOWED_EMAIL can access"
echo ""

# Kill any existing ngrok
pkill -f "ngrok.*http" 2>/dev/null || true
sleep 1

# Start ngrok in background
ngrok http 6080 \
    --oauth=google \
    --oauth-allow-email="$ALLOWED_EMAIL" \
    --log=stdout \
    > $SKILL_DIR/ngrok.log 2>&1 &

NGROK_PID=$!
echo $NGROK_PID > $SKILL_DIR/ngrok.pid

# Wait for tunnel to be ready
echo "   Waiting for tunnel..."
for i in {1..30}; do
    sleep 1
    # Query ngrok API for tunnel URL
    TUNNEL_URL=$(curl -s http://127.0.0.1:4040/api/tunnels 2>/dev/null | jq -r '.tunnels[0].public_url' 2>/dev/null)
    if [ -n "$TUNNEL_URL" ] && [ "$TUNNEL_URL" != "null" ]; then
        break
    fi
    echo -n "."
done
echo ""

if [ -z "$TUNNEL_URL" ] || [ "$TUNNEL_URL" = "null" ]; then
    echo "❌ Failed to get tunnel URL"
    echo "   Check log: $SKILL_DIR/ngrok.log"
    cat $SKILL_DIR/ngrok.log | tail -20
    exit 1
fi

# Build noVNC URL with auto-login password
if [ -n "$VNC_PASSWORD" ] && [ "$VNC_PASSWORD" != "(your Mac password)" ]; then
    NOVNC_URL="${TUNNEL_URL}/vnc.html?password=${VNC_PASSWORD}&autoconnect=true"
else
    NOVNC_URL="${TUNNEL_URL}/vnc.html?autoconnect=true"
fi

echo ""
echo "========================================="
echo "✅ TUNNEL ACTIVE!"
echo ""
echo "🔗 Link: $NOVNC_URL"
echo "🔐 Protected by: Google OAuth ($ALLOWED_EMAIL)"
echo ""
echo "Open from your phone or any browser!"
echo "You'll need to login with your Google account."
echo "========================================="
echo ""

# Save to config.json
cat > $CONFIG_FILE << CONF
{
    "novncUrl": "$NOVNC_URL",
    "tunnelUrl": "$TUNNEL_URL",
    "allowedEmail": "$ALLOWED_EMAIL",
    "cdpUrl": "http://localhost:9222",
    "updatedAt": "$(date -Iseconds)"
}
CONF

# Update TOOLS.md
if [ -f "$TOOLS_FILE" ]; then
    # Remove old Browser Control section
    grep -v "## Browser Control" "$TOOLS_FILE" | grep -v "noVNC URL:" | grep -v "Protected by:" | grep -v "Send the link" | grep -v "When you need the user" | grep -v "Google OAuth" > "$TOOLS_FILE.tmp" || true
    mv "$TOOLS_FILE.tmp" "$TOOLS_FILE"
fi

cat >> "$TOOLS_FILE" << TOOLS

## Browser Control

When you need the user to login, 2FA, captcha, or any manual verification:

- noVNC URL: $NOVNC_URL
- Protected by: Google OAuth ($ALLOWED_EMAIL)

Send the link and wait for the user to say "done".
The user will need to login with their Google account.
TOOLS

echo "📝 TOOLS.md updated"
echo "📝 Config saved to $CONFIG_FILE"
echo ""
echo "🔄 Tunnel running in background (PID: $NGROK_PID)"
echo "   Stop with: $SKILL_DIR/stop-tunnel.sh"
