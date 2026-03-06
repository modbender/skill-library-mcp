#!/bin/bash
# Batch check multiple TestFlight links, silent unless status changes

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
STATE_FILE="$SKILL_ROOT/config/batch-state.json"
CONFIG_FILE="$SKILL_ROOT/config/batch-config.json"
LOOKUP="$SCRIPT_DIR/lookup.sh"
CHECKER="$SCRIPT_DIR/check-single.sh"

# Initialize state file if it doesn't exist
if [[ ! -f "$STATE_FILE" ]]; then
  echo '{}' > "$STATE_FILE"
fi

# Initialize config file if it doesn't exist
if [[ ! -f "$CONFIG_FILE" ]]; then
  echo '{"links":[],"interval_minutes":60}' > "$CONFIG_FILE"
fi

# Read tracked links from config
TRACKED_LINKS=$(jq -r '.links[]' "$CONFIG_FILE" 2>/dev/null || echo "")

if [[ -z "$TRACKED_LINKS" ]]; then
  echo "No TestFlight URLs configured for monitoring."
  echo "Add URLs with: testflight-monitor.sh add <url>"
  exit 0
fi

CHANGES=()

while IFS= read -r URL; do
  # Extract code from URL
  CODE=$(echo "$URL" | grep -oE '[A-Za-z0-9]{8}$')
  
  # Look up app name
  APP_NAME=$("$LOOKUP" "$CODE" 2>/dev/null || echo "$CODE")
  
  # Check current status (suppress output)
  if bash "$CHECKER" "$URL" 2>&1 | grep -q "AVAILABLE"; then
    CURRENT_STATUS="available"
  else
    CURRENT_STATUS="full"
  fi
  
  # Get previous status
  PREV_STATUS=$(jq -r --arg code "$CODE" '.[$code] // "unknown"' "$STATE_FILE")
  
  # Detect change
  if [[ "$PREV_STATUS" == "full" && "$CURRENT_STATUS" == "available" ]]; then
    CHANGES+=("🎉 **$APP_NAME** beta now has open slots! $URL")
  elif [[ "$PREV_STATUS" == "unknown" && "$CURRENT_STATUS" == "available" ]]; then
    CHANGES+=("🎉 **$APP_NAME** beta has open slots! $URL")
  fi
  
  # Update state
  jq --arg code "$CODE" --arg status "$CURRENT_STATUS" '.[$code] = $status' "$STATE_FILE" > "$STATE_FILE.tmp"
  mv "$STATE_FILE.tmp" "$STATE_FILE"
  
done <<< "$TRACKED_LINKS"

# Output
if [[ ${#CHANGES[@]} -gt 0 ]]; then
  echo "TestFlight Status Changes:"
  echo ""
  for change in "${CHANGES[@]}"; do
    echo "$change"
  done
else
  echo "SILENT: No status changes detected."
fi
