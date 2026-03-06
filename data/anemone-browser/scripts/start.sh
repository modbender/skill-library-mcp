#!/bin/bash
# === Start headful Chrome + VNC + noVNC environment ===
# Usage: bash start.sh [password] [novnc_port] [cdp_port]

# Generate random 14-char password if not specified
generate_password() {
  cat /dev/urandom | tr -dc 'a-zA-Z0-9' | head -c 14
}

VNC_PASS="${1:-$(generate_password)}"
NOVNC_PORT="${2:-6080}"
CDP_PORT="${3:-9222}"
VNC_PORT=5900
RESOLUTION="${4:-1920x1080x24}"
DISPLAY_NUM=99

echo "=== Stopping existing processes ==="
pkill -9 -f Xvfb 2>/dev/null
pkill -9 -f x11vnc 2>/dev/null
pkill -9 -f websockify 2>/dev/null
pkill -9 -f fluxbox 2>/dev/null
pkill -9 -f "chrome" 2>/dev/null
sleep 2

# === SSL cert (self-signed, reuse if exists) ===
mkdir -p /root/.vnc
if [ ! -f /root/.vnc/combined.pem ]; then
  echo "Generating self-signed SSL certificate..."
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /root/.vnc/key.pem -out /root/.vnc/cert.pem \
    -subj "/CN=openclaw-vnc" 2>/dev/null
  cat /root/.vnc/key.pem /root/.vnc/cert.pem > /root/.vnc/combined.pem
fi

# === VNC password file ===
x11vnc -storepasswd "$VNC_PASS" /root/.vnc/passwd 2>/dev/null

# === Xvfb (virtual display) ===
echo "Starting Xvfb..."
Xvfb :$DISPLAY_NUM -screen 0 $RESOLUTION &
sleep 1
export DISPLAY=:$DISPLAY_NUM

# === Window manager ===
fluxbox &>/dev/null &
sleep 1

# === Chrome policy: block file:// access ===
mkdir -p /etc/opt/chrome/policies/managed
cat > /etc/opt/chrome/policies/managed/security.json << 'POLICY'
{
  "URLBlocklist": ["file://*", "javascript://*", "data:text/html*"],
  "DeveloperToolsAvailability": 0,
  "ExtensionInstallBlocklist": ["*"],
  "BrowserAddPersonEnabled": false
}
POLICY

# === Chrome headful with anti-detection ===
echo "Starting Chrome (CDP port $CDP_PORT)..."
google-chrome-stable \
  --no-sandbox \
  --disable-gpu \
  --disable-dev-shm-usage \
  --disable-blink-features=AutomationControlled \
  --user-data-dir=/root/.chrome-profile \
  --remote-debugging-port=$CDP_PORT \
  --remote-debugging-address=127.0.0.1 \
  --display=:$DISPLAY_NUM \
  --window-size=$(echo $RESOLUTION | cut -dx -f1),$(echo $RESOLUTION | cut -dx -f2) \
  --start-maximized \
  &>/dev/null &
sleep 3

# === x11vnc (localhost only, password protected, shared) ===
echo "Starting x11vnc..."
x11vnc -display :$DISPLAY_NUM -forever -shared \
  -rfbauth /root/.vnc/passwd \
  -rfbport $VNC_PORT \
  -bg -o /tmp/x11vnc.log
sleep 1

# === noVNC with SSL ===
echo "Starting noVNC (port $NOVNC_PORT)..."
websockify --web=/usr/share/novnc --cert=/root/.vnc/combined.pem \
  $NOVNC_PORT localhost:$VNC_PORT &>/tmp/novnc.log &
sleep 1

# === Verify ===
FAIL=0
pgrep -f "Xvfb :$DISPLAY_NUM" > /dev/null || { echo "ERROR: Xvfb failed"; FAIL=1; }
pgrep -f "x11vnc" | grep -v defunct > /dev/null || { echo "ERROR: x11vnc failed"; cat /tmp/x11vnc.log; FAIL=1; }
pgrep -f "websockify.*$NOVNC_PORT" > /dev/null || { echo "ERROR: websockify failed"; FAIL=1; }
pgrep -f "chrome.*$CDP_PORT" > /dev/null || { echo "ERROR: Chrome failed"; FAIL=1; }

if [ $FAIL -eq 0 ]; then
  echo ""
  echo "=========================================="
  echo "  VNC Browser Environment Ready!"
  echo "=========================================="
  echo "  noVNC:    https://<YOUR_IP>:${NOVNC_PORT}/vnc.html?password=${VNC_PASS}&autoconnect=true&resize=scale"
  echo "  Password: ${VNC_PASS}"
  echo "  CDP:      http://127.0.0.1:${CDP_PORT}/json/version"
  echo "=========================================="
else
  echo "Some services failed to start. Check logs above."
  exit 1
fi
