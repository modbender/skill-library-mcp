#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

SKILL_DIR="$(pwd)"
SCRIPT_PATH="${SKILL_DIR}/scripts/mcp_update.sh"
LOG_PATH="${SKILL_DIR}/logs/update.log"

echo "Autotask MCP — Weekly Auto-Update Installer"
echo "============================================"
echo ""
echo "This will install a weekly scheduled task to pull the latest Docker image."
echo ""
echo "  Schedule : Every Sunday at 03:00 AM"
echo "  Command  : ${SCRIPT_PATH}"
echo "  Log      : ${LOG_PATH}"
echo ""

read -rp "Install weekly auto-update? [y/N] " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
  echo "Aborted."
  exit 0
fi

mkdir -p "${SKILL_DIR}/logs"

OS="$(uname -s)"

if [[ "$OS" == "Darwin" ]]; then
  # --- macOS: use a LaunchAgent plist (no crontab modification) ---
  PLIST_LABEL="com.autotask-mcp.weekly-update"
  PLIST_DIR="$HOME/Library/LaunchAgents"
  PLIST_PATH="${PLIST_DIR}/${PLIST_LABEL}.plist"

  mkdir -p "$PLIST_DIR"

  cat > "$PLIST_PATH" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${PLIST_LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>${SCRIPT_PATH}</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Weekday</key>
    <integer>0</integer>
    <key>Hour</key>
    <integer>3</integer>
    <key>Minute</key>
    <integer>0</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>${LOG_PATH}</string>
  <key>StandardErrorPath</key>
  <string>${LOG_PATH}</string>
  <key>WorkingDirectory</key>
  <string>${SKILL_DIR}</string>
</dict>
</plist>
PLIST

  launchctl bootout "gui/$(id -u)" "$PLIST_PATH" 2>/dev/null || true
  launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH"

  echo ""
  echo "LaunchAgent installed: ${PLIST_PATH}"
  echo "To remove later, run: ./scripts/cron_uninstall.sh"

elif command -v systemctl &>/dev/null; then
  # --- Linux: use a systemd user timer (no crontab modification) ---
  TIMER_DIR="$HOME/.config/systemd/user"
  mkdir -p "$TIMER_DIR"

  cat > "${TIMER_DIR}/autotask-mcp-update.service" <<SVC
[Unit]
Description=Autotask MCP Docker image update

[Service]
Type=oneshot
ExecStart=${SCRIPT_PATH}
WorkingDirectory=${SKILL_DIR}
SVC

  cat > "${TIMER_DIR}/autotask-mcp-update.timer" <<TMR
[Unit]
Description=Weekly Autotask MCP update check

[Timer]
OnCalendar=Sun *-*-* 03:00:00
Persistent=true

[Install]
WantedBy=timers.target
TMR

  systemctl --user daemon-reload
  systemctl --user enable --now autotask-mcp-update.timer

  echo ""
  echo "Systemd user timer installed."
  echo "  Check status: systemctl --user status autotask-mcp-update.timer"
  echo "  To remove later, run: ./scripts/cron_uninstall.sh"

else
  echo "Error: No supported scheduler found (launchd or systemd required)."
  echo "You can run ./scripts/mcp_update.sh manually or set up your own cron job."
  exit 1
fi
