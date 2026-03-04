#!/bin/bash
# install_daemon.sh — Install proactive-claw as a background daemon
# Supports: macOS (launchd) | Linux (systemd user service)
# Run once after setup.sh

set -e

SKILL_DIR="$HOME/.openclaw/workspace/skills/proactive-claw"
PYTHON=$(command -v python3)
PLATFORM=$(uname -s)

echo "🦞 Proactive Agent Daemon Installer"
echo "====================================="
echo "Platform: $PLATFORM"
echo "Python: $PYTHON"
echo ""

if [ "$PLATFORM" = "Darwin" ]; then
  PLIST_DIR="$HOME/Library/LaunchAgents"
  PLIST="$PLIST_DIR/ai.openclaw.proactive-claw.plist"

  mkdir -p "$PLIST_DIR"

  cat > "$PLIST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>ai.openclaw.proactive-claw</string>

  <key>ProgramArguments</key>
  <array>
    <string>$PYTHON</string>
    <string>$SKILL_DIR/scripts/daemon.py</string>
  </array>

  <key>StartInterval</key>
  <integer>900</integer>

  <key>RunAtLoad</key>
  <true/>

  <key>StandardOutPath</key>
  <string>$SKILL_DIR/daemon.log</string>

  <key>StandardErrorPath</key>
  <string>$SKILL_DIR/daemon.log</string>

  <key>EnvironmentVariables</key>
  <dict>
    <key>HOME</key>
    <string>$HOME</string>
    <key>PATH</key>
    <string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
  </dict>

  <key>WorkingDirectory</key>
  <string>$SKILL_DIR</string>
</dict>
</plist>
EOF

  # Unload if already running
  launchctl unload "$PLIST" 2>/dev/null || true
  # Load
  launchctl load "$PLIST"
  echo "✅ Daemon installed and started (launchd)"
  echo "   Runs every 15 minutes automatically"
  echo "   Logs: $SKILL_DIR/daemon.log"
  echo ""
  echo "To stop:    launchctl unload \"$PLIST\""
  echo "To restart: launchctl unload \"$PLIST\" && launchctl load \"$PLIST\""
  echo "Status:     launchctl list | grep proactive-claw"

elif [ "$PLATFORM" = "Linux" ]; then
  SERVICE_DIR="$HOME/.config/systemd/user"
  SERVICE="$SERVICE_DIR/openclaw-proactive-claw.service"
  TIMER="$SERVICE_DIR/openclaw-proactive-claw.timer"

  mkdir -p "$SERVICE_DIR"

  cat > "$SERVICE" << EOF
[Unit]
Description=OpenClaw Proactive Agent
After=network.target

[Service]
Type=oneshot
ExecStart=$PYTHON $SKILL_DIR/scripts/daemon.py
StandardOutput=append:$SKILL_DIR/daemon.log
StandardError=append:$SKILL_DIR/daemon.log
Environment=HOME=$HOME
EOF

  cat > "$TIMER" << EOF
[Unit]
Description=Run OpenClaw Proactive Agent every 15 minutes

[Timer]
OnBootSec=2min
OnUnitActiveSec=15min
Unit=openclaw-proactive-claw.service

[Install]
WantedBy=timers.target
EOF

  systemctl --user daemon-reload
  systemctl --user enable --now openclaw-proactive-claw.timer
  echo "✅ Daemon installed and started (systemd user timer)"
  echo "   Runs every 15 minutes"
  echo "   Logs: $SKILL_DIR/daemon.log"
  echo ""
  echo "To stop:  systemctl --user stop openclaw-proactive-claw.timer"
  echo "Status:   systemctl --user status openclaw-proactive-claw.timer"

else
  echo "⚠️  Platform '$PLATFORM' not supported for auto-install."
  echo "   Run manually: python3 $SKILL_DIR/scripts/daemon.py --loop"
fi

echo ""
echo "====================================="
echo "✅ Daemon install complete!"
echo ""
echo "Test it now: python3 $SKILL_DIR/scripts/daemon.py --status"
