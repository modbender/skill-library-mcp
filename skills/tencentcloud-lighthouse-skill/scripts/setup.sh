#!/usr/bin/env bash
set -euo pipefail

# Lighthouse MCP Setup — installs mcporter (if needed) and writes config
# Usage:
#   setup.sh --secret-id <ID> --secret-key <KEY> [--config-path <path>] [--check-only]
#
# Examples:
#   setup.sh --secret-id AKIDxxxx --secret-key yyyyyyy
#   setup.sh --check-only
#   setup.sh --secret-id AKIDxxxx --secret-key yyyyyyy --config-path /root/.mcporter/mcporter.json

CONFIG_PATH="${HOME}/.mcporter/mcporter.json"
SECRET_ID=""
SECRET_KEY=""
CHECK_ONLY=false

usage() {
  cat >&2 <<'EOF'
Usage:
  setup.sh --secret-id <TENCENTCLOUD_SECRET_ID> --secret-key <TENCENTCLOUD_SECRET_KEY> [--config-path <path>]
  setup.sh --check-only

Options:
  --secret-id     Tencent Cloud SecretId (required unless --check-only)
  --secret-key    Tencent Cloud SecretKey (required unless --check-only)
  --config-path   mcporter config file path (default: ~/.mcporter/mcporter.json)
  --check-only    Only check if mcporter and config are ready, don't modify anything
  -h, --help      Show this help
EOF
  exit 2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --secret-id)   SECRET_ID="${2:-}";   shift 2 ;;
    --secret-key)  SECRET_KEY="${2:-}";  shift 2 ;;
    --config-path) CONFIG_PATH="${2:-}"; shift 2 ;;
    --check-only)  CHECK_ONLY=true;      shift   ;;
    -h|--help)     usage ;;
    *)             echo "Unknown arg: $1" >&2; usage ;;
  esac
done

# --- Check mode ---
if $CHECK_ONLY; then
  echo "=== Lighthouse MCP Status Check ==="

  # Check mcporter
  if command -v mcporter &>/dev/null; then
    echo "[OK] mcporter installed: $(mcporter --version 2>/dev/null || echo 'unknown version')"
  else
    echo "[MISSING] mcporter not installed"
    echo "  Fix: npm install -g mcporter"
  fi

  # Check config file
  if [[ -f "$CONFIG_PATH" ]]; then
    echo "[OK] Config file exists: $CONFIG_PATH"
    # Check if lighthouse server is configured
    if grep -q '"lighthouse"' "$CONFIG_PATH" 2>/dev/null; then
      echo "[OK] lighthouse MCP server configured"
      # Check if credentials are present (not placeholder)
      if grep -q 'TENCENTCLOUD_SECRET_ID' "$CONFIG_PATH" 2>/dev/null; then
        echo "[OK] Tencent Cloud credentials found in config"
      else
        echo "[WARN] Tencent Cloud credentials may be missing"
      fi
    else
      echo "[MISSING] lighthouse MCP server not in config"
    fi
  else
    echo "[MISSING] Config file not found: $CONFIG_PATH"
  fi

  # Try listing servers
  if command -v mcporter &>/dev/null && [[ -f "$CONFIG_PATH" ]]; then
    echo ""
    echo "=== MCP Servers ==="
    mcporter list --config "$CONFIG_PATH" 2>/dev/null || echo "[ERROR] Failed to list servers"
  fi

  exit 0
fi

# --- Setup mode: validate inputs ---
if [[ -z "$SECRET_ID" ]]; then
  echo "[ERROR] --secret-id is required" >&2
  exit 1
fi
if [[ -z "$SECRET_KEY" ]]; then
  echo "[ERROR] --secret-key is required" >&2
  exit 1
fi

echo "=== Lighthouse MCP Auto Setup ==="

# Step 1: Check/install mcporter
if command -v mcporter &>/dev/null; then
  echo "[OK] mcporter already installed"
else
  echo "[INSTALL] Installing mcporter via npm..."
  npm install -g mcporter
  if command -v mcporter &>/dev/null; then
    echo "[OK] mcporter installed successfully"
  else
    echo "[ERROR] mcporter installation failed" >&2
    exit 1
  fi
fi

# Step 2: Create config directory
CONFIG_DIR="$(dirname "$CONFIG_PATH")"
if [[ ! -d "$CONFIG_DIR" ]]; then
  mkdir -p "$CONFIG_DIR"
  echo "[OK] Created config directory: $CONFIG_DIR"
fi

# Step 3: Write/update config with lighthouse server
# If config exists, try to merge; otherwise create new
if [[ -f "$CONFIG_PATH" ]]; then
  echo "[INFO] Updating existing config: $CONFIG_PATH"
  # Use a temp file for safe write
  TEMP_CONFIG="$(mktemp)"
  # Simple JSON merge using node (available since mcporter requires node)
  node -e "
    const fs = require('fs');
    let config = {};
    try { config = JSON.parse(fs.readFileSync('$CONFIG_PATH', 'utf8')); } catch {}
    if (!config.mcpServers) config.mcpServers = {};
    config.mcpServers.lighthouse = {
      command: 'npx',
      args: ['-y', 'lighthouse-mcp-server'],
      env: {
        TENCENTCLOUD_SECRET_ID: '$SECRET_ID',
        TENCENTCLOUD_SECRET_KEY: '$SECRET_KEY'
      }
    };
    fs.writeFileSync('$TEMP_CONFIG', JSON.stringify(config, null, 2));
  "
  mv "$TEMP_CONFIG" "$CONFIG_PATH"
else
  echo "[INFO] Creating new config: $CONFIG_PATH"
  cat > "$CONFIG_PATH" <<JSONEOF
{
  "mcpServers": {
    "lighthouse": {
      "command": "npx",
      "args": ["-y", "lighthouse-mcp-server"],
      "env": {
        "TENCENTCLOUD_SECRET_ID": "$SECRET_ID",
        "TENCENTCLOUD_SECRET_KEY": "$SECRET_KEY"
      }
    }
  }
}
JSONEOF
fi

echo "[OK] Config written: $CONFIG_PATH"

# Step 4: Verify
echo ""
echo "=== Verification ==="
echo "Listing MCP servers..."
mcporter list --config "$CONFIG_PATH" 2>/dev/null || echo "[WARN] mcporter list failed (server may need first-run initialization)"

echo ""
echo "Testing lighthouse connection (listing tools)..."
if mcporter list lighthouse --config "$CONFIG_PATH" --schema 2>/dev/null; then
  echo ""
  echo "[OK] Lighthouse MCP setup complete! All tools available."
else
  echo "[WARN] Could not list lighthouse tools yet. This is normal on first run."
  echo "  The MCP server will be started on first call."
fi

echo ""
echo "=== Setup Complete ==="
echo "Config: $CONFIG_PATH"
echo "Server: lighthouse (via npx lighthouse-mcp-server)"