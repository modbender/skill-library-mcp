#!/bin/bash
set -euo pipefail

# list.sh — List all managed toolguard services
# Usage: list.sh

PLIST_DIR="$HOME/Library/LaunchAgents"
FOUND=false

for plist in "$PLIST_DIR"/ai.toolguard.*.plist; do
  [[ -f "$plist" ]] || continue
  FOUND=true

  LABEL=$(basename "$plist" .plist)
  SERVICE_NAME="${LABEL#ai.toolguard.}"

  if launchctl list "$LABEL" &>/dev/null; then
    STATE="running"
  else
    STATE="stopped"
  fi

  printf "%-30s %s\n" "$SERVICE_NAME" "$STATE"
done

if [[ "$FOUND" == "false" ]]; then
  echo "No toolguard services installed."
fi
