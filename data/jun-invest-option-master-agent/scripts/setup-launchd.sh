#!/usr/bin/env bash
set -euo pipefail

# macOS launchd helper: install two LaunchAgents
# - sync: (optional) not needed because we sync on commit, but can be used as fallback
# - publish: checks for new commits and publishes daily; also honors a force flag file

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLIST_DIR="$HOME/Library/LaunchAgents"

PUBLISH_LABEL="ai.openclaw.jun-invest-option-master-agent.publish"
PUBLISH_PLIST="${PLIST_DIR}/${PUBLISH_LABEL}.plist"

mkdir -p "${PLIST_DIR}"

CLAWHUB_BIN=$(command -v clawhub 2>/dev/null || true)

cat > "${PUBLISH_PLIST}" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key><string>${PUBLISH_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
      <string>/bin/bash</string>
      <string>${SKILL_DIR}/scripts/publish.sh</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
      <key>PATH</key><string>/Users/lijunsheng/.nvm/versions/node/v22.22.0/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
      <key>CLAWHUB_BIN</key><string>${CLAWHUB_BIN}</string>
      <key>CLAWHUB_REQUEST_TIMEOUT_MS</key><string>120000</string>
    </dict>
    <key>RunAtLoad</key><true/>
    <!-- Daily publish window: 03:15 local time -->
    <key>StartCalendarInterval</key>
    <dict>
      <key>Hour</key><integer>3</integer>
      <key>Minute</key><integer>15</integer>
    </dict>
    <!-- Also poll every 30 minutes to honor .publish-now flag without waiting until 03:15 -->
    <key>StartInterval</key><integer>1800</integer>
    <key>StandardOutPath</key><string>$HOME/.openclaw/logs/jun-invest-option-master-agent.publish.out.log</string>
    <key>StandardErrorPath</key><string>$HOME/.openclaw/logs/jun-invest-option-master-agent.publish.err.log</string>
  </dict>
</plist>
EOF

# Reload job
launchctl unload "${PUBLISH_PLIST}" >/dev/null 2>&1 || true
launchctl load "${PUBLISH_PLIST}" >/dev/null 2>&1 || true

echo "OK: launchd job installed/loaded: ${PUBLISH_LABEL}"
