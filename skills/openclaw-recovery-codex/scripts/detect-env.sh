#!/bin/bash
# OpenClaw Environment Detection Script
# Works on macOS, Linux. For Windows, use detect-env.ps1

echo "═══ OpenClaw Environment Detection ═══"

# OS
OS=$(uname -s 2>/dev/null || echo "Unknown")
echo "OS: $OS"

# OpenClaw binary
OC_BIN=$(which openclaw 2>/dev/null)
if [ -n "$OC_BIN" ]; then
  echo "Binary: $OC_BIN"
  echo "Version: $(openclaw --version 2>/dev/null)"
else
  echo "Binary: NOT FOUND in PATH"
  # Check common locations
  for p in /usr/local/bin/openclaw ~/.npm/bin/openclaw ~/node_modules/.bin/openclaw; do
    [ -x "$p" ] && echo "Found at: $p" && OC_BIN="$p" && break
  done
fi

# State directory
if [ -n "$OPENCLAW_STATE_DIR" ]; then
  echo "State dir (env): $OPENCLAW_STATE_DIR"
elif [ -d "$HOME/.openclaw/state" ]; then
  echo "State dir (default): $HOME/.openclaw/state"
else
  echo "State dir: NOT FOUND"
  # Search
  find "$HOME" -maxdepth 3 -name "openclaw.json" -type f 2>/dev/null | head -5 | while read f; do
    echo "Candidate config: $f"
  done
fi

# Config
if [ -n "$OPENCLAW_CONFIG_PATH" ]; then
  echo "Config (env): $OPENCLAW_CONFIG_PATH"
elif [ -n "$OPENCLAW_STATE_DIR" ] && [ -f "$OPENCLAW_STATE_DIR/openclaw.json" ]; then
  echo "Config: $OPENCLAW_STATE_DIR/openclaw.json"
fi

# Gateway port
if [ -n "$OC_BIN" ]; then
  PORT=$($OC_BIN status 2>/dev/null | grep -oP ':\K\d{4,5}' | head -1)
  [ -n "$PORT" ] && echo "Gateway port: $PORT"
fi

# Tailscale
TS=$(which tailscale 2>/dev/null)
if [ -n "$TS" ]; then
  echo "Tailscale: installed"
  tailscale status 2>/dev/null | head -3
else
  echo "Tailscale: not installed"
fi

echo "═══ END ═══"
