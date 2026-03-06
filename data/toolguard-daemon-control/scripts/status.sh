#!/bin/bash
set -euo pipefail

# status.sh — Check service status
# Usage: status.sh [service-name]

if [[ $# -ge 1 ]]; then
  LABEL="ai.toolguard.${1}"
  PLIST_PATH="$HOME/Library/LaunchAgents/${LABEL}.plist"

  if [[ ! -f "$PLIST_PATH" ]]; then
    echo "Service '${1}' is not installed."
    exit 1
  fi

  echo "Service: ${1}"
  echo "Label:   ${LABEL}"
  echo "Plist:   ${PLIST_PATH}"

  if launchctl list "$LABEL" &>/dev/null; then
    echo "State:   running"
    launchctl list "$LABEL" 2>/dev/null
  else
    echo "State:   stopped"
  fi

  LOG_DIR="$HOME/Library/Logs/toolguard/${1}"
  if [[ -d "$LOG_DIR" ]]; then
    echo ""
    echo "Last 5 lines of stderr:"
    tail -5 "$LOG_DIR/stderr.log" 2>/dev/null || echo "  (no stderr log)"
  fi
else
  # Show all toolguard services
  echo "All ai.toolguard.* services:"
  echo ""
  launchctl list | grep "ai\.toolguard\." || echo "  (none found)"
fi
