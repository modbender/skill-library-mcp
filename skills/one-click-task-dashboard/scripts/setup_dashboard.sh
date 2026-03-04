#!/bin/zsh
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="${HOME}/.openclaw/dashboard"
REFRESH_LABEL="ai.x.task-dashboard-refresh"
HTTP_LABEL="ai.x.task-dashboard-http"
USER_ID="$(id -u)"

/usr/bin/python3 "${SKILL_DIR}/scripts/build_dashboard.py" --output-dir "${OUT_DIR}" >/dev/null

cat > "${HOME}/Library/LaunchAgents/${REFRESH_LABEL}.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>${REFRESH_LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>${SKILL_DIR}/scripts/build_dashboard.py</string>
    <string>--output-dir</string>
    <string>${OUT_DIR}</string>
  </array>
  <key>StartInterval</key><integer>300</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>${OUT_DIR}/dashboard-refresh.out.log</string>
  <key>StandardErrorPath</key><string>${OUT_DIR}/dashboard-refresh.err.log</string>
</dict>
</plist>
PLIST

cat > "${HOME}/Library/LaunchAgents/${HTTP_LABEL}.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>${HTTP_LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>-m</string>
    <string>http.server</string>
    <string>8787</string>
    <string>--bind</string>
    <string>127.0.0.1</string>
    <string>--directory</string>
    <string>${OUT_DIR}</string>
  </array>
  <key>KeepAlive</key><true/>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>${OUT_DIR}/dashboard-http.out.log</string>
  <key>StandardErrorPath</key><string>${OUT_DIR}/dashboard-http.err.log</string>
</dict>
</plist>
PLIST

launchctl bootout "gui/${USER_ID}/${REFRESH_LABEL}" >/dev/null 2>&1 || true
launchctl bootout "gui/${USER_ID}/${HTTP_LABEL}" >/dev/null 2>&1 || true
launchctl bootstrap "gui/${USER_ID}" "${HOME}/Library/LaunchAgents/${REFRESH_LABEL}.plist"
launchctl bootstrap "gui/${USER_ID}" "${HOME}/Library/LaunchAgents/${HTTP_LABEL}.plist"
launchctl kickstart -k "gui/${USER_ID}/${REFRESH_LABEL}" >/dev/null 2>&1 || true
launchctl kickstart -k "gui/${USER_ID}/${HTTP_LABEL}" >/dev/null 2>&1 || true

echo "Dashboard ready: http://127.0.0.1:8787/index.html"
