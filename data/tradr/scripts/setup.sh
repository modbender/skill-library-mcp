#!/usr/bin/env bash
# setup.sh — Install tradr: config init + exit-manager systemd service.
# Usage: ./scripts/setup.sh [--user]
#   --user: install as user service (systemctl --user) instead of system-wide

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
EXIT_SCRIPT="$SKILL_DIR/scripts/exit-manager.py"
ENTRY_SCRIPT="$SKILL_DIR/scripts/tradr-enter.py"
CONFIG="$SKILL_DIR/config.json"
TEMPLATE="$SKILL_DIR/config-template.json"
SERVICE_NAME="tradr-exit-manager"

echo "=== tradr setup ==="
echo ""

# Check Python 3
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 is required" >&2
    exit 1
fi
echo "✓ Python 3 found: $(python3 --version)"

# Check jq (needed by bankr.sh)
if ! command -v jq &>/dev/null; then
    echo "WARNING: jq not found — bankr.sh requires it"
fi

# Check bankr skill
BANKR_DEFAULT="$HOME/.openclaw/skills/bankr/scripts/bankr.sh"
if [ -f "$BANKR_DEFAULT" ]; then
    echo "✓ Bankr skill found"
else
    echo "⚠  Bankr skill not found at $BANKR_DEFAULT"
    echo "   Install the bankr skill first, or update bankr_script in config.json"
fi

# Create config from template if missing
if [ ! -f "$CONFIG" ]; then
    cp "$TEMPLATE" "$CONFIG"
    echo ""
    echo "✓ Created config.json from template"
    echo "  → Edit $CONFIG with your wallet addresses and strategy"
else
    echo "✓ config.json already exists"
fi

# Create workspace dirs for positions + trade log
WORKSPACE="$HOME/.openclaw/workspace"
mkdir -p "$WORKSPACE/signals"
echo "✓ Workspace directories ready"

# Make scripts executable
chmod +x "$EXIT_SCRIPT" "$ENTRY_SCRIPT"
ADAPTER_EXAMPLE="$SKILL_DIR/adapters/example-adapter.py"
[ -f "$ADAPTER_EXAMPLE" ] && chmod +x "$ADAPTER_EXAMPLE"
echo "✓ Scripts are executable"

# Parse args
USER_SERVICE=false
for arg in "$@"; do
    case "$arg" in
        --user) USER_SERVICE=true ;;
    esac
done

# Write systemd unit for exit-manager daemon
UNIT="[Unit]
Description=tradr Exit Manager — autonomous position management
After=network.target

[Service]
Type=simple
ExecStart=$(command -v python3) $EXIT_SCRIPT
Restart=on-failure
RestartSec=10
WorkingDirectory=$SKILL_DIR

[Install]
WantedBy=multi-user.target"

echo ""
if [ "$USER_SERVICE" = true ]; then
    UNIT_DIR="$HOME/.config/systemd/user"
    mkdir -p "$UNIT_DIR"
    echo "$UNIT" > "$UNIT_DIR/$SERVICE_NAME.service"
    systemctl --user daemon-reload
    systemctl --user enable "$SERVICE_NAME"
    echo "✓ Installed as user service"
    echo "  Start: systemctl --user start $SERVICE_NAME"
    echo "  Status: systemctl --user status $SERVICE_NAME"
else
    UNIT_DIR="/etc/systemd/system"
    UNIT_FILE="$UNIT_DIR/$SERVICE_NAME.service"
    if [ -w "$UNIT_DIR" ] || [ "$(id -u)" -eq 0 ]; then
        echo "$UNIT" > "$UNIT_FILE"
        systemctl daemon-reload
        systemctl enable "$SERVICE_NAME"
        echo "✓ Installed as system service"
        echo "  Start: sudo systemctl start $SERVICE_NAME"
        echo "  Status: sudo systemctl status $SERVICE_NAME"
    else
        echo "Need root to install system service. Run with sudo or use --user flag."
        echo "  sudo ./scripts/setup.sh"
        echo "  ./scripts/setup.sh --user"
        exit 1
    fi
fi

echo ""
echo "=== Setup complete ==="
echo ""
echo "Next steps:"
echo "  1. Edit config.json — add wallet addresses, tune scoring tiers and exit strategy"
echo "  2. Start the exit-manager: systemctl start $SERVICE_NAME"
echo "  3. Connect a signal adapter (see adapters/README.md) or feed trades manually:"
echo "     python3 scripts/tradr-enter.py <CA> --score <SCORE> [--chain <chain>]"
echo "  4. The exit manager handles all exits automatically"
echo ""
echo "Signal adapters:"
echo "  See adapters/example-adapter.py for a template"
echo "  See adapters/README.md for the full interface spec"
