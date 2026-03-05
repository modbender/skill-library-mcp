#!/bin/bash
set -e
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GUARD_DIR="$HOME/.openclaw/workspace/tools/claw-guard"

echo "🛡️ Installing ClawGuard..."
mkdir -p "$GUARD_DIR"
cp "$SKILL_DIR/scripts/claw-guard.py" "$GUARD_DIR/claw-guard.py"
cp "$SKILL_DIR/scripts/claw-guard-cli.py" "$GUARD_DIR/claw-guard-cli.py"
chmod +x "$GUARD_DIR/claw-guard.py" "$GUARD_DIR/claw-guard-cli.py"

PYTHON="$(command -v python3 2>/dev/null || true)"
[ -z "$PYTHON" ] && echo "❌ Python3 not found in PATH" && exit 1
echo "  Python: $PYTHON"

# CLI wrapper
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/claw-guard" << CLI
#!/bin/bash
exec $PYTHON $GUARD_DIR/claw-guard-cli.py "\$@"
CLI
chmod +x "$HOME/.local/bin/claw-guard"

# Detect OS and install service
OS="$(uname -s)"
CURRENT_PATH="$PATH"

if [ "$OS" = "Darwin" ]; then
    # macOS — launchd plist
    PLIST_DIR="$HOME/Library/LaunchAgents"
    PLIST="$PLIST_DIR/com.openclaw.claw-guard.plist"
    mkdir -p "$PLIST_DIR"
    cat > "$PLIST" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.claw-guard</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON</string>
        <string>$GUARD_DIR/claw-guard.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$GUARD_DIR/claw-guard.stdout.log</string>
    <key>StandardErrorPath</key>
    <string>$GUARD_DIR/claw-guard.stderr.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>HOME</key>
        <string>$HOME</string>
        <key>PATH</key>
        <string>$CURRENT_PATH</string>
    </dict>
</dict>
</plist>
PLIST

    launchctl unload "$PLIST" 2>/dev/null || true
    launchctl load "$PLIST"
    sleep 2
    if launchctl list | grep -q com.openclaw.claw-guard; then
        echo "✅ ClawGuard running (launchd)"
    else
        echo "⚠️ Failed to start — check: launchctl list | grep claw-guard"
    fi

else
    # Linux — systemd user service
    SERVICE_DIR="$HOME/.config/systemd/user"
    mkdir -p "$SERVICE_DIR"
    cat > "$SERVICE_DIR/claw-guard.service" << UNIT
[Unit]
Description=ClawGuard — OpenClaw task watchdog
After=network.target

[Service]
Type=simple
ExecStart=$PYTHON $GUARD_DIR/claw-guard.py
Restart=always
RestartSec=10
Environment=HOME=$HOME
Environment=PATH=$CURRENT_PATH

[Install]
WantedBy=default.target
UNIT

    systemctl --user daemon-reload
    systemctl --user enable claw-guard.service
    systemctl --user restart claw-guard.service
    sleep 2
    if systemctl --user is-active claw-guard.service > /dev/null 2>&1; then
        echo "✅ ClawGuard running (systemd)"
    else
        echo "⚠️ Failed to start"
        systemctl --user status claw-guard.service
    fi
fi

echo "  CLI: claw-guard register|register-restart|status|remove|clear-done"
echo "  Log: $GUARD_DIR/claw-guard.log"
