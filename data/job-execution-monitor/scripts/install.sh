#!/usr/bin/env bash
set -euo pipefail

# Job Execution Monitor installation script
# Sets up a systemd *user* timer (preferred) or a per-user cron entry.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
CONFIG_FILE="${WORKSPACE}/job-execution-monitor.json"
HEALTHCHECK_SCRIPT="${SCRIPT_DIR}/healthcheck.sh"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
  echo "ERROR: Don't run as root. User-level systemd/cron is preferred." >&2
  exit 1
fi

# Check dependencies
for cmd in jq; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "ERROR: $cmd not found. Install with: sudo apt install $cmd" >&2
    exit 1
  fi
done

# Copy example config if not exists
if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "📝 Creating default config: $CONFIG_FILE"
  cp "${SCRIPT_DIR}/../config/job-execution-monitor.example.json" "$CONFIG_FILE"
  echo "⚠️  Edit config before enabling monitoring!"
  echo "   nano $CONFIG_FILE"
fi

# Load check interval
CHECK_INTERVAL=$(jq -r '.checkIntervalMin // 10' "$CONFIG_FILE")

# Prefer systemd user timers
if command -v systemctl &>/dev/null && systemctl --user status &>/dev/null; then
  echo "✅ Using systemd user timer"
  
  # Create service file
  SERVICE_FILE="$HOME/.config/systemd/user/openclaw-job-execution-monitor.service"
  TIMER_FILE="$HOME/.config/systemd/user/openclaw-job-execution-monitor.timer"
  
  mkdir -p "$HOME/.config/systemd/user"
  
  cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=OpenClaw Job Execution Monitor healthcheck
After=network.target

[Service]
Type=oneshot
ExecStart=${HEALTHCHECK_SCRIPT}
Environment="OPENCLAW_WORKSPACE=${WORKSPACE}"
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF

  cat > "$TIMER_FILE" <<EOF
[Unit]
Description=OpenClaw Job Execution Monitor timer
Requires=openclaw-job-execution-monitor.service

[Timer]
OnBootSec=2min
OnUnitActiveSec=${CHECK_INTERVAL}min
AccuracySec=1min

[Install]
WantedBy=timers.target
EOF

  # Reload and enable
  systemctl --user daemon-reload
  systemctl --user enable openclaw-job-execution-monitor.timer
  systemctl --user start openclaw-job-execution-monitor.timer
  
  echo "✅ Systemd timer installed and started"
  echo ""
  echo "Commands:"
  echo "  systemctl --user status openclaw-job-execution-monitor.timer"
  echo "  systemctl --user stop openclaw-job-execution-monitor.timer"
  echo "  journalctl --user -u openclaw-job-execution-monitor.service -f"
  
else
  # Fallback to cron
  echo "✅ Using cron"
  
  CRON_LINE="*/${CHECK_INTERVAL} * * * * OPENCLAW_WORKSPACE=${WORKSPACE} ${HEALTHCHECK_SCRIPT} >> ${WORKSPACE}/job-execution-monitor.log 2>&1"
  
  # Check if already in crontab
  if crontab -l 2>/dev/null | grep -qF "$HEALTHCHECK_SCRIPT"; then
    echo "⚠️  Cron entry already exists"
  else
    (crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -
    echo "✅ Cron job added"
  fi
  
  echo ""
  echo "Commands:"
  echo "  crontab -l  # view"
  echo "  crontab -e  # edit"
  echo "  tail -f ${WORKSPACE}/job-execution-monitor.log"
fi

echo ""
echo "🎯 Job Execution Monitor installed!"
echo "   Config: $CONFIG_FILE"
echo "   Check interval: ${CHECK_INTERVAL} minutes"
echo ""
echo "Next steps:"
echo "  1. Edit config: nano $CONFIG_FILE"
echo "  2. Test manually: $HEALTHCHECK_SCRIPT"
echo "  3. Monitor logs (see commands above)"
