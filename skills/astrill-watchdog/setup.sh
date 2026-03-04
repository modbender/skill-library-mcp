#!/usr/bin/env bash
# =============================================================================
# setup.sh — Astrill Watchdog one-time setup
#
# Run this once after installing the skill to enable auto-start on login.
# Creates a systemd user service that starts the watchdog automatically
# when you log in and restarts it if it ever crashes.
#
# Usage:
#   bash setup.sh
# =============================================================================

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WATCHDOG="$SKILL_DIR/astrill-watchdog.sh"
SERVICE_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="$SERVICE_DIR/astrill-watchdog.service"

echo "=== Astrill Watchdog Setup ==="
echo ""

# ── Preflight checks ──────────────────────────────────────────────────────────

if [[ ! -x "$WATCHDOG" ]]; then
    chmod +x "$WATCHDOG"
    echo "✓ Made watchdog script executable"
fi

if [[ ! -f "/usr/local/Astrill/astrill" ]]; then
    echo "✗ Astrill not found at /usr/local/Astrill/astrill"
    echo "  Is the Astrill deb package installed?"
    exit 1
fi
echo "✓ Astrill found at /usr/local/Astrill/astrill"

# ── Stop existing service if running ─────────────────────────────────────────

if systemctl --user is-active astrill-watchdog &>/dev/null; then
    echo "  Stopping existing watchdog service…"
    systemctl --user stop astrill-watchdog || true
fi

# Also kill any manually started instances
pkill -f "astrill-watchdog.sh _loop" 2>/dev/null || true
rm -f "${XDG_STATE_HOME:-$HOME/.local/state}/astrill-watchdog/watchdog.pid" \
       "${XDG_STATE_HOME:-$HOME/.local/state}/astrill-watchdog/watchdog.lock"

# ── Write systemd service ─────────────────────────────────────────────────────

mkdir -p "$SERVICE_DIR"

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Astrill VPN Watchdog
After=network.target default.target

[Service]
Type=simple
ExecStart=/bin/bash ${WATCHDOG} _loop
ExecStop=/bin/bash ${WATCHDOG} stop
Restart=on-failure
RestartSec=15

[Install]
WantedBy=default.target
EOF

echo "✓ Systemd service written to $SERVICE_FILE"

# ── Enable and start ──────────────────────────────────────────────────────────

systemctl --user daemon-reload
systemctl --user enable astrill-watchdog
systemctl --user start astrill-watchdog

echo "✓ Service enabled and started"
echo ""

# ── Verify ────────────────────────────────────────────────────────────────────

sleep 2
if systemctl --user is-active astrill-watchdog &>/dev/null; then
    echo "✓ Watchdog is running"
    echo ""
    systemctl --user status astrill-watchdog --no-pager
    echo ""
    echo "=== Setup complete! ==="
    echo ""
    echo "The watchdog will now:"
    echo "  • Start automatically when you log in"
    echo "  • Restart automatically if it crashes"
    echo "  • Check your VPN every 30 seconds"
    echo ""
    echo "Useful commands:"
    echo "  systemctl --user status astrill-watchdog   # service status"
    echo "  bash $WATCHDOG status                      # full VPN diagnostics"
    echo "  tail -f "${XDG_STATE_HOME:-$HOME/.local/state}/astrill-watchdog/watchdog.log"          # live log"
else
    echo "✗ Service failed to start. Check logs:"
    echo "  journalctl --user -u astrill-watchdog -n 30 --no-pager"
    exit 1
fi
