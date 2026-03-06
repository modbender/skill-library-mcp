#!/usr/bin/env bash
set -euo pipefail

LABEL="ai.openclaw.session.rotator"
DOMAIN="gui/$(id -u)"
MAP_FILE="$HOME/.openclaw/state/session-rotator/active-session-map.json"
ARCHIVE_ROOT="$HOME/.openclaw/knowledge/session-archives"

echo "== launchctl =="
launchctl print "${DOMAIN}/${LABEL}" | sed -n '1,40p' || true

echo
echo "== recent archives =="
ls -lt "$ARCHIVE_ROOT" 2>/dev/null | sed -n '1,20p' || true

echo
echo "== latest map =="
if [[ -f "$MAP_FILE" ]]; then
  cat "$MAP_FILE"
else
  echo "(map not found)"
fi
