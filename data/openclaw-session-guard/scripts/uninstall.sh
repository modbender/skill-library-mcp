#!/usr/bin/env bash
set -euo pipefail

LABEL="ai.openclaw.session.rotator"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"

launchctl bootout "gui/$(id -u)" "$PLIST" >/dev/null 2>&1 || true
rm -f "$PLIST"
rm -f "$HOME/bin/openclaw-session-rotator.sh"

echo "[uninstall] removed launch agent and script"
