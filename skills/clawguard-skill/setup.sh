#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# ClawWall v0.3.0 — One-Command Installer
#
# Usage:  bash setup.sh
#
# This script installs the ClawWall DLP service, builds the OpenClaw plugin
# and startup hook, registers the plugin, sets up a systemd/launchd service,
# starts the service, and verifies the health endpoint.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

CLAWWALL_VERSION="0.3.0"
CLAWWALL_PORT=8642
CLAWWALL_CONFIG_DIR="$HOME/.config/clawwall"
OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"

# ── Colors ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

info()  { echo -e "${CYAN}[info]${NC}  $*"; }
ok()    { echo -e "${GREEN}[ok]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[warn]${NC}  $*"; }
fail()  { echo -e "${RED}[fail]${NC}  $*"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Step 1: Check Prerequisites ─────────────────────────────────────────────
echo ""
echo -e "${BOLD}ClawWall v${CLAWWALL_VERSION} — Installer${NC}"
echo "─────────────────────────────────────────"
echo ""

info "Checking prerequisites..."

# Python 3.10+
if ! command -v python3 &>/dev/null; then
  fail "python3 not found. Install Python 3.10+ and re-run."
fi
PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
  fail "Python 3.10+ required (found $PY_VERSION)"
fi
ok "Python $PY_VERSION"

# pip
if ! command -v pip &>/dev/null && ! python3 -m pip --version &>/dev/null 2>&1; then
  fail "pip not found. Install pip and re-run."
fi
ok "pip"

# Node.js
if ! command -v node &>/dev/null; then
  fail "node not found. Install Node.js 18+ and re-run."
fi
ok "node $(node --version)"

# npm
if ! command -v npm &>/dev/null; then
  fail "npm not found. Install npm and re-run."
fi
ok "npm $(npm --version)"

echo ""

# ── Step 2: Install ClawWall Python Service ──────────────────────────────────
info "Installing ClawWall Python service..."

if pip install "clawwall==$CLAWWALL_VERSION" 2>/dev/null; then
  ok "Installed clawwall $CLAWWALL_VERSION from PyPI"
elif pip install clawwall 2>/dev/null; then
  ok "Installed clawwall from PyPI (latest)"
else
  # Fallback: install from local source if we're in the repo
  REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
  if [ -f "$REPO_ROOT/pyproject.toml" ]; then
    info "PyPI install failed — installing from local source..."
    pip install "$REPO_ROOT"
    ok "Installed clawwall from local source"
  else
    fail "Could not install clawwall. Run 'pip install clawwall' manually."
  fi
fi

# Verify binary
if ! command -v clawwall &>/dev/null; then
  warn "clawwall binary not on PATH — it may be in a pip user bin directory"
  warn "Try: python3 -m clawguard"
fi

echo ""

# ── Step 3: Build the OpenClaw Plugin ────────────────────────────────────────
info "Building OpenClaw plugin..."

PLUGIN_DIR="$SCRIPT_DIR/plugin"
if [ -d "$PLUGIN_DIR" ]; then
  cd "$PLUGIN_DIR"
  npm install --silent 2>/dev/null
  npm run build --silent 2>/dev/null
  ok "Plugin built: $PLUGIN_DIR/dist/index.js"
  cd "$SCRIPT_DIR"
else
  warn "Plugin directory not found at $PLUGIN_DIR — skipping"
fi

echo ""

# ── Step 4: Build the Startup Hook ───────────────────────────────────────────
info "Building startup hook..."

HOOK_DIR="$SCRIPT_DIR/hooks/openclaw"
if [ -d "$HOOK_DIR" ]; then
  cd "$HOOK_DIR"
  npm install --silent 2>/dev/null
  npm run build --silent 2>/dev/null
  ok "Hook built: $HOOK_DIR/dist/handler.js"
  cd "$SCRIPT_DIR"
else
  warn "Hook directory not found at $HOOK_DIR — skipping"
fi

echo ""

# ── Step 5: Register Plugin in OpenClaw Config ───────────────────────────────
info "Registering plugin in OpenClaw config..."

PLUGIN_DIST="$PLUGIN_DIR/dist/index.js"
mkdir -p "$(dirname "$OPENCLAW_CONFIG")"

if [ -f "$OPENCLAW_CONFIG" ]; then
  # Check if jq is available for clean JSON manipulation
  if command -v jq &>/dev/null; then
    TEMP_CONFIG=$(mktemp)
    jq --arg path "$PLUGIN_DIST" \
      '.plugins.clawwall = {
        "path": $path,
        "config": {
          "serviceUrl": "http://127.0.0.1:8642",
          "blockOnError": false,
          "timeoutMs": 5000
        }
      }' "$OPENCLAW_CONFIG" > "$TEMP_CONFIG" && mv "$TEMP_CONFIG" "$OPENCLAW_CONFIG"
    ok "Plugin registered in $OPENCLAW_CONFIG (via jq)"
  else
    # Fallback: use node to merge JSON
    node -e "
      const fs = require('fs');
      const config = JSON.parse(fs.readFileSync('$OPENCLAW_CONFIG', 'utf-8'));
      config.plugins = config.plugins || {};
      config.plugins.clawwall = {
        path: '$PLUGIN_DIST',
        config: {
          serviceUrl: 'http://127.0.0.1:8642',
          blockOnError: false,
          timeoutMs: 5000,
        },
      };
      fs.writeFileSync('$OPENCLAW_CONFIG', JSON.stringify(config, null, 2) + '\n');
    "
    ok "Plugin registered in $OPENCLAW_CONFIG (via node)"
  fi
else
  # Create new config file
  cat > "$OPENCLAW_CONFIG" <<JSONEOF
{
  "plugins": {
    "clawwall": {
      "path": "$PLUGIN_DIST",
      "config": {
        "serviceUrl": "http://127.0.0.1:8642",
        "blockOnError": false,
        "timeoutMs": 5000
      }
    }
  }
}
JSONEOF
  ok "Created $OPENCLAW_CONFIG with ClawWall plugin"
fi

echo ""

# ── Step 6: Create System Service ────────────────────────────────────────────
info "Setting up system service for auto-start..."

mkdir -p "$CLAWWALL_CONFIG_DIR"

CLAWWALL_BIN=$(command -v clawwall 2>/dev/null || echo "$(python3 -c 'import sys; print(sys.prefix)')/bin/clawwall")

if [[ "$(uname)" == "Linux" ]] && command -v systemctl &>/dev/null; then
  # ── systemd user service (Linux) ──
  SYSTEMD_DIR="$HOME/.config/systemd/user"
  mkdir -p "$SYSTEMD_DIR"

  cat > "$SYSTEMD_DIR/clawwall.service" <<SVCEOF
[Unit]
Description=ClawWall DLP Service
After=network.target

[Service]
Type=simple
ExecStart=$CLAWWALL_BIN
Restart=on-failure
RestartSec=5
Environment=CLAWGUARD_HOST=0.0.0.0
Environment=CLAWGUARD_PORT=$CLAWWALL_PORT

[Install]
WantedBy=default.target
SVCEOF

  systemctl --user daemon-reload 2>/dev/null || true
  systemctl --user enable clawwall.service 2>/dev/null || true
  ok "Created systemd user service: $SYSTEMD_DIR/clawwall.service"

elif [[ "$(uname)" == "Darwin" ]]; then
  # ── launchd plist (macOS) ──
  PLIST_DIR="$HOME/Library/LaunchAgents"
  PLIST_FILE="$PLIST_DIR/com.clawwall.service.plist"
  mkdir -p "$PLIST_DIR"

  cat > "$PLIST_FILE" <<PLISTEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.clawwall.service</string>
  <key>ProgramArguments</key>
  <array>
    <string>$CLAWWALL_BIN</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>EnvironmentVariables</key>
  <dict>
    <key>CLAWGUARD_HOST</key>
    <string>0.0.0.0</string>
    <key>CLAWGUARD_PORT</key>
    <string>$CLAWWALL_PORT</string>
  </dict>
  <key>StandardOutPath</key>
  <string>$CLAWWALL_CONFIG_DIR/clawwall.log</string>
  <key>StandardErrorPath</key>
  <string>$CLAWWALL_CONFIG_DIR/clawwall.err</string>
</dict>
</plist>
PLISTEOF

  ok "Created launchd plist: $PLIST_FILE"
else
  warn "Could not detect systemd or launchd — skipping system service setup"
  warn "The gateway:startup hook will still auto-start the service"
fi

echo ""

# ── Step 7: Start Service & Verify ───────────────────────────────────────────
info "Starting ClawWall service..."

# Check if already running
if curl -sf "http://127.0.0.1:$CLAWWALL_PORT/api/v1/health" &>/dev/null; then
  ok "ClawWall is already running on port $CLAWWALL_PORT"
else
  # Start via systemd/launchd if available, otherwise direct
  if [[ "$(uname)" == "Linux" ]] && command -v systemctl &>/dev/null; then
    systemctl --user start clawwall.service 2>/dev/null || true
  elif [[ "$(uname)" == "Darwin" ]] && [ -f "$PLIST_FILE" ]; then
    launchctl load "$PLIST_FILE" 2>/dev/null || true
  fi

  # Fallback: direct start if service didn't start
  sleep 1
  if ! curl -sf "http://127.0.0.1:$CLAWWALL_PORT/api/v1/health" &>/dev/null; then
    if command -v clawwall &>/dev/null; then
      nohup clawwall > "$CLAWWALL_CONFIG_DIR/clawwall.log" 2>&1 &
      echo $! > "$CLAWWALL_CONFIG_DIR/clawwall.pid"
    else
      nohup python3 -m clawguard > "$CLAWWALL_CONFIG_DIR/clawwall.log" 2>&1 &
      echo $! > "$CLAWWALL_CONFIG_DIR/clawwall.pid"
    fi
  fi

  # Wait for health
  info "Waiting for health endpoint..."
  for i in $(seq 1 15); do
    if curl -sf "http://127.0.0.1:$CLAWWALL_PORT/api/v1/health" &>/dev/null; then
      break
    fi
    sleep 1
  done

  if curl -sf "http://127.0.0.1:$CLAWWALL_PORT/api/v1/health" &>/dev/null; then
    ok "ClawWall is running on port $CLAWWALL_PORT"
  else
    warn "Service started but health check did not respond in time"
    warn "Check logs: $CLAWWALL_CONFIG_DIR/clawwall.log"
  fi
fi

echo ""

# ── Summary ──────────────────────────────────────────────────────────────────
echo -e "${BOLD}──────────────────────────────────────────${NC}"
echo -e "${GREEN}${BOLD}  ClawWall v${CLAWWALL_VERSION} — Setup Complete${NC}"
echo -e "${BOLD}──────────────────────────────────────────${NC}"
echo ""
echo -e "  Service:    http://127.0.0.1:${CLAWWALL_PORT}"
echo -e "  Dashboard:  http://127.0.0.1:${CLAWWALL_PORT}/dashboard"
echo -e "  Health:     http://127.0.0.1:${CLAWWALL_PORT}/api/v1/health"
echo -e "  Config:     ${CLAWWALL_CONFIG_DIR}/"
echo -e "  Plugin:     ${PLUGIN_DIST}"
echo ""
echo -e "  The service auto-starts on OpenClaw gateway boot via the"
echo -e "  ${CYAN}gateway:startup${NC} hook. A systemd/launchd service is also"
echo -e "  installed as a fallback."
echo ""
echo -e "  ${BOLD}Verify:${NC}"
echo -e "    curl http://127.0.0.1:${CLAWWALL_PORT}/api/v1/health"
echo ""
