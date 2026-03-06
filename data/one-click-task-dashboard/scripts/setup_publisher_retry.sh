#!/bin/zsh
set -euo pipefail

LABEL="ai.x.publish-one-click-dashboard"
USER_ID="$(id -u)"
LOG_DIR="${HOME}/.openclaw/logs"
PLIST="${HOME}/Library/LaunchAgents/${LABEL}.plist"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RUNNER="${SKILL_DIR}/scripts/publish_to_clawhub.sh"

mkdir -p "${LOG_DIR}"

cat > "${PLIST}" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>${LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/zsh</string>
    <string>${RUNNER}</string>
  </array>
  <key>StartInterval</key><integer>1800</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>${LOG_DIR}/publish-one-click-dashboard.out.log</string>
  <key>StandardErrorPath</key><string>${LOG_DIR}/publish-one-click-dashboard.err.log</string>
</dict>
</plist>
PLIST

launchctl bootout "gui/${USER_ID}/${LABEL}" >/dev/null 2>&1 || true
launchctl bootstrap "gui/${USER_ID}" "${PLIST}"
launchctl kickstart -k "gui/${USER_ID}/${LABEL}" >/dev/null 2>&1 || true

echo "Publisher retry installed: ${LABEL} (every 30 minutes)"
