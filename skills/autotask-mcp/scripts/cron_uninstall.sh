#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "Removing autotask-mcp auto-update schedule..."

OS="$(uname -s)"
removed=false

if [[ "$OS" == "Darwin" ]]; then
  PLIST_LABEL="com.autotask-mcp.weekly-update"
  PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"

  if [[ -f "$PLIST_PATH" ]]; then
    launchctl bootout "gui/$(id -u)" "$PLIST_PATH" 2>/dev/null || true
    rm -f "$PLIST_PATH"
    echo "LaunchAgent removed: ${PLIST_PATH}"
    removed=true
  fi
fi

if command -v systemctl &>/dev/null; then
  TIMER_DIR="$HOME/.config/systemd/user"
  if [[ -f "${TIMER_DIR}/autotask-mcp-update.timer" ]]; then
    systemctl --user disable --now autotask-mcp-update.timer 2>/dev/null || true
    rm -f "${TIMER_DIR}/autotask-mcp-update.timer"
    rm -f "${TIMER_DIR}/autotask-mcp-update.service"
    systemctl --user daemon-reload
    echo "Systemd user timer removed."
    removed=true
  fi
fi

# Also clean up any legacy crontab entries from previous versions
if crontab -l 2>/dev/null | grep -q "autotask-mcp"; then
  (crontab -l 2>/dev/null | grep -v "autotask-mcp" || true) | crontab -
  echo "Legacy crontab entries removed."
  removed=true
fi

if [[ "$removed" == false ]]; then
  echo "No auto-update schedule found."
else
  echo "Done."
fi
