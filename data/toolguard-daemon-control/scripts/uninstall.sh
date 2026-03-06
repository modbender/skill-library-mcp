#!/bin/bash
set -euo pipefail

# uninstall.sh — Stop and remove a launchd user agent
# Usage: uninstall.sh <service-name>

[[ $# -lt 1 ]] && { echo "Usage: $0 <service-name>"; exit 1; }

SERVICE_NAME="$1"
LABEL="ai.toolguard.${SERVICE_NAME}"
PLIST_PATH="$HOME/Library/LaunchAgents/${LABEL}.plist"

if [[ ! -f "$PLIST_PATH" ]]; then
  echo "Error: Service '${SERVICE_NAME}' not found (no plist at ${PLIST_PATH})"
  exit 1
fi

echo "Unloading service '${SERVICE_NAME}'..."
launchctl unload "$PLIST_PATH" 2>/dev/null || true

rm -f "$PLIST_PATH"
echo "Service '${SERVICE_NAME}' uninstalled."
echo "Logs preserved at: ~/Library/Logs/toolguard/${SERVICE_NAME}/"
