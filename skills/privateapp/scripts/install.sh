#!/usr/bin/env bash
# Private App install script
# Supports macOS and Linux
# Usage: bash scripts/install.sh [--port PORT]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PORT=8800
VENV_DIR="$PROJECT_DIR/.venv"

# ── Parse args ─────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --port) PORT="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: bash scripts/install.sh [--port PORT]"
            echo "  --port PORT   HTTP port (default: 8800)"
            exit 0 ;;
        *) echo "Unknown argument: $1"; exit 1 ;;
    esac
done

# ── Platform detection ─────────────────────────────────────────────────
OS="$(uname -s)"
case "$OS" in
    Darwin)  PLATFORM="macos" ;;
    Linux)   PLATFORM="linux" ;;
    *)       echo "❌ Unsupported platform: $OS"; exit 1 ;;
esac

echo "🏠 Private App Install"
echo "=================="
echo "Platform : $PLATFORM"
echo "Port     : $PORT"
echo "Project  : $PROJECT_DIR"
echo ""

# ── Helper functions ───────────────────────────────────────────────────
check_command() {
    command -v "$1" &>/dev/null
}

require_command() {
    if ! check_command "$1"; then
        echo "❌ Required command not found: $1"
        echo "   $2"
        exit 1
    fi
}

# ── 1. Python check ────────────────────────────────────────────────────
echo "🐍 Checking Python..."
PYTHON=""
for py in python3 python3.12 python3.11 python3.10 python3.9; do
    if check_command "$py"; then
        PY_VER="$($py -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
        PY_MAJOR="${PY_VER%%.*}"
        PY_MINOR="${PY_VER##*.}"
        if [[ "$PY_MAJOR" -ge 3 && "$PY_MINOR" -ge 9 ]]; then
            PYTHON="$py"
            echo "  ✅ Python $PY_VER ($py)"
            break
        fi
    fi
done
if [[ -z "$PYTHON" ]]; then
    echo "❌ Python 3.9+ required. Install from https://python.org"
    exit 1
fi

# ── 2. Node.js check ───────────────────────────────────────────────────
echo ""
echo "📦 Checking Node.js..."
if check_command node; then
    NODE_VER="$(node --version)"
    echo "  ✅ Node $NODE_VER"
else
    echo "  ⚠️  Node.js not found — frontend won't be built"
    echo "     Install from https://nodejs.org"
    BUILD_FRONTEND=false
fi
BUILD_FRONTEND=${BUILD_FRONTEND:-true}

# ── 3. VAPID email prompt ──────────────────────────────────────────────
echo ""
echo "🔔 Push Notifications Setup"
echo "   A VAPID email is required to enable push notifications."
echo "   It's used only as a contact identifier — never sent anywhere."
echo ""

VAPID_EMAIL=""
# Check if already configured
CONFIG_FILE="$SCRIPT_DIR/config.json"
if [[ -f "$CONFIG_FILE" ]]; then
    EXISTING_EMAIL="$(python3 -c "import json; d=json.load(open('$CONFIG_FILE')); print(d.get('push',{}).get('vapid_email',''))" 2>/dev/null || echo "")"
    if [[ -n "$EXISTING_EMAIL" && "$EXISTING_EMAIL" != "admin@localhost" ]]; then
        echo "  ✅ Using existing VAPID email: $EXISTING_EMAIL"
        VAPID_EMAIL="$EXISTING_EMAIL"
    fi
fi

if [[ -z "$VAPID_EMAIL" ]]; then
    while true; do
        read -r -p "  Enter VAPID email (e.g. you@example.com): " VAPID_EMAIL
        if [[ "$VAPID_EMAIL" =~ ^[^@]+@[^@]+\.[^@]+$ ]]; then
            break
        fi
        echo "  ⚠️  Please enter a valid email address."
    done
fi

# ── 4. Python virtual environment ─────────────────────────────────────
echo ""
echo "🐍 Setting up Python venv..."
if [[ ! -f "$VENV_DIR/bin/python3" ]]; then
    "$PYTHON" -m venv "$VENV_DIR"
    echo "  ✅ venv created at $VENV_DIR"
else
    echo "  ✅ venv already exists"
fi

PIP="$VENV_DIR/bin/pip"
VENV_PYTHON="$VENV_DIR/bin/python3"

echo ""
echo "📦 Installing Python dependencies..."
"$PIP" install -q --upgrade pip
"$PIP" install -q \
    "fastapi>=0.100" \
    "uvicorn[standard]>=0.20" \
    "psutil>=5.9" \
    "pywebpush>=2.0" \
    "py-vapid>=1.9" \
    "aiofiles>=23.0"
echo "  ✅ Python packages installed"

# ── 5. VAPID keys ─────────────────────────────────────────────────────
echo ""
echo "🔑 Setting up VAPID keys..."
DATA_DIR="$HOME/.local/share/privateapp"
mkdir -p "$DATA_DIR"

VAPID_PRIVATE="$DATA_DIR/vapid_private.pem"
VAPID_PUBLIC="$DATA_DIR/vapid_public.txt"

if [[ -f "$VAPID_PRIVATE" && -f "$VAPID_PUBLIC" ]]; then
    echo "  ✅ VAPID keys already exist"
else
    "$VENV_PYTHON" - <<'PYEOF'
import sys, os
data_dir = os.path.expanduser('~/.local/share/privateapp')
private_pem = os.path.join(data_dir, 'vapid_private.pem')
public_txt  = os.path.join(data_dir, 'vapid_public.txt')
try:
    from py_vapid import Vapid
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    from base64 import urlsafe_b64encode
    v = Vapid()
    v.generate_keys()
    v.save_key(private_pem)
    raw = v.public_key.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
    pub = urlsafe_b64encode(raw).rstrip(b'=').decode()
    open(public_txt, 'w').write(pub)
    print(f"  ✅ VAPID keys generated")
    print(f"  📄 Private: {private_pem}")
    print(f"  📄 Public:  {pub[:40]}...")
except Exception as e:
    print(f"  ⚠️  VAPID key generation failed: {e}")
    print("     Run scripts/install.py manually after install.")
PYEOF
fi

# ── 6. Write config.json ───────────────────────────────────────────────
echo ""
echo "⚙️  Writing config..."
cat > "$CONFIG_FILE" <<JSONEOF
{
  "host": "0.0.0.0",
  "port": $PORT,
  "data_dir": "$DATA_DIR",
  "file_browser": {
    "root": "~"
  },
  "push": {
    "vapid_email": "$VAPID_EMAIL"
  }
}
JSONEOF
echo "  ✅ Config written to $CONFIG_FILE"

# ── 7. Build all frontends ─────────────────────────────────────────────
if [[ "$BUILD_FRONTEND" == "true" ]]; then
    echo ""
    echo "🔨 Building shell frontend..."
    FRONTEND_DIR="$PROJECT_DIR/frontend"
    if [[ -f "$FRONTEND_DIR/package.json" ]]; then
        (cd "$FRONTEND_DIR" && npm install --silent && npm run build)
        echo "  ✅ Shell frontend built → static/dist/"
    else
        echo "  ⚠️  frontend/package.json not found — skipping shell build"
    fi

    echo ""
    echo "🔨 Building app frontends..."
    for APP_DIR in "$PROJECT_DIR"/apps/*/; do
        APP_NAME="$(basename "$APP_DIR")"
        APP_FRONTEND="$APP_DIR/frontend"
        if [[ -f "$APP_FRONTEND/package.json" ]]; then
            echo "  📦 Building $APP_NAME..."
            (cd "$APP_FRONTEND" && npm install --silent && npm run build)
            echo "  ✅ $APP_NAME built"
        fi
    done
    echo "  ✅ All app frontends built"
fi

# ── 8. Tailscale ──────────────────────────────────────────────────────
echo ""
echo "🌐 Tailscale..."
if check_command tailscale; then
    echo "  ✅ Tailscale found"
    read -r -p "  Set up Tailscale HTTPS serve? [Y/n]: " SETUP_TS
    SETUP_TS="${SETUP_TS:-Y}"
    if [[ "$SETUP_TS" =~ ^[Yy] ]]; then
        HTTPS_PORT=443
        if sudo tailscale serve --bg --https "$HTTPS_PORT" "http://127.0.0.1:$PORT" 2>/dev/null; then
            echo "  ✅ Tailscale serve configured (HTTPS on :$HTTPS_PORT)"
        else
            HTTPS_PORT=$((PORT + 443))
            if sudo tailscale serve --bg --https "$HTTPS_PORT" "http://127.0.0.1:$PORT" 2>/dev/null; then
                echo "  ✅ Tailscale serve configured (HTTPS on :$HTTPS_PORT)"
            else
                echo "  ⚠️  Tailscale serve failed. Try manually:"
                echo "     sudo tailscale serve --bg --https 443 http://127.0.0.1:$PORT"
            fi
        fi
        TS_HOST="$(tailscale status --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('Self',{}).get('DNSName','').rstrip('.'))" 2>/dev/null || echo "")"
        if [[ -n "$TS_HOST" ]]; then
            echo ""
            echo "  📱 Open on your phone: https://$TS_HOST/"
        fi
    else
        echo "  Skipping Tailscale serve setup."
    fi
else
    echo "  ℹ️  Tailscale not installed — server will only be accessible on this machine"
    echo "     Install: https://tailscale.com/download"
    read -r -p "  Install Tailscale now? [y/N]: " INSTALL_TS
    INSTALL_TS="${INSTALL_TS:-N}"
    if [[ "$INSTALL_TS" =~ ^[Yy] ]]; then
        if [[ "$PLATFORM" == "linux" ]]; then
            curl -fsSL https://tailscale.com/install.sh | sh
            echo "  ✅ Tailscale installed — run 'sudo tailscale up' to authenticate"
        elif [[ "$PLATFORM" == "macos" ]]; then
            if check_command brew; then
                brew install --cask tailscale
                echo "  ✅ Tailscale installed via Homebrew"
            else
                echo "  Download from: https://tailscale.com/download"
            fi
        fi
    fi
fi

# ── 9. System service ─────────────────────────────────────────────────
echo ""
echo "🔄 Setting up system service..."

SERVER_CMD="$VENV_DIR/bin/python3 $SCRIPT_DIR/server.py --config $CONFIG_FILE"

if [[ "$PLATFORM" == "linux" ]]; then
    SERVICE_DIR="$HOME/.config/systemd/user"
    mkdir -p "$SERVICE_DIR"
    SERVICE_FILE="$SERVICE_DIR/privateapp.service"
    cat > "$SERVICE_FILE" <<SVCEOF
[Unit]
Description=Private App Personal Dashboard
After=network-online.target

[Service]
Type=simple
WorkingDirectory=$PROJECT_DIR
ExecStart=$SERVER_CMD
Restart=on-failure
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=default.target
SVCEOF
    systemctl --user daemon-reload 2>/dev/null || true
    systemctl --user enable privateapp.service 2>/dev/null || true
    echo "  ✅ systemd service installed: privateapp.service"
    echo "     Start:   systemctl --user start privateapp"
    echo "     Status:  systemctl --user status privateapp"
    echo "     Logs:    journalctl --user -u privateapp -f"

elif [[ "$PLATFORM" == "macos" ]]; then
    PLIST_DIR="$HOME/Library/LaunchAgents"
    mkdir -p "$PLIST_DIR"
    PLIST_FILE="$PLIST_DIR/com.privateapp.server.plist"
    LOG_FILE="$HOME/Library/Logs/privateapp.log"
    cat > "$PLIST_FILE" <<PLISTEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.privateapp.server</string>
    <key>ProgramArguments</key>
    <array>
        <string>$VENV_DIR/bin/python3</string>
        <string>$SCRIPT_DIR/server.py</string>
        <string>--config</string>
        <string>$CONFIG_FILE</string>
    </array>
    <key>WorkingDirectory</key><string>$PROJECT_DIR</string>
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key><true/>
    <key>StandardOutPath</key><string>$LOG_FILE</string>
    <key>StandardErrorPath</key><string>$LOG_FILE</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PYTHONUNBUFFERED</key><string>1</string>
    </dict>
</dict>
</plist>
PLISTEOF
    launchctl unload "$PLIST_FILE" 2>/dev/null || true
    launchctl load "$PLIST_FILE" 2>/dev/null || true
    echo "  ✅ launchd plist installed: com.privateapp.server"
    echo "     Start:  launchctl load $PLIST_FILE"
    echo "     Stop:   launchctl unload $PLIST_FILE"
    echo "     Logs:   tail -f $LOG_FILE"
fi

# ── 10. Done ───────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════╗"
echo "║        ✅ Private App Installed!         ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "Start the server:"
echo "  $VENV_PYTHON $SCRIPT_DIR/server.py"
echo ""
echo "Then open http://localhost:$PORT in your browser."
echo ""
echo "📱 Add to Home Screen:"
echo "  iOS Safari  → Share → Add to Home Screen"
echo "  Android     → Chrome menu → Add to Home Screen"
echo ""
