#!/bin/bash
# TestFlight Monitor - Main CLI entry point
# Usage: testflight-monitor.sh <command> [args...]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$SCRIPT_DIR/lib"

# Commands
CMD_LOOKUP="$LIB_DIR/lookup.sh"
CMD_CHECK_SINGLE="$LIB_DIR/check-single.sh"
CMD_CHECK_BATCH="$LIB_DIR/check-batch.sh"
CMD_UPDATE_LOOKUP="$SCRIPT_DIR/tools/update-lookup.sh"

usage() {
  cat << EOF
TestFlight Monitor v1.0.0
Monitor TestFlight beta availability with smart lookups and batch checking

USAGE:
  testflight-monitor.sh <command> [args...]

COMMANDS:
  lookup <code>              Look up app name by TestFlight code
  check <url>                Check single TestFlight URL for availability
  batch                      Check all configured URLs (silent unless changed)
  update-lookup              Refresh lookup table from awesome-testflight-link
  config                     Show batch configuration
  add <url>                  Add URL to batch monitoring
  remove <url>               Remove URL from batch monitoring
  list                       List all monitored URLs
  state                      Show current state (last known status)
  help                       Show this help

EXAMPLES:
  # Look up an app name
  testflight-monitor.sh lookup BnjD4BEf

  # Check a single URL
  testflight-monitor.sh check https://testflight.apple.com/join/BnjD4BEf

  # Run batch check (for cron)
  testflight-monitor.sh batch

  # Add URL to monitoring
  testflight-monitor.sh add https://testflight.apple.com/join/Sq8bYSnJ

  # List monitored apps
  testflight-monitor.sh list

  # Update lookup table
  testflight-monitor.sh update-lookup

For more details, see SKILL.md
EOF
}

case "${1:-help}" in
  lookup)
    [[ $# -lt 2 ]] && { echo "Error: lookup requires a code"; exit 1; }
    exec "$CMD_LOOKUP" "$2"
    ;;
  
  check)
    [[ $# -lt 2 ]] && { echo "Error: check requires a URL"; exit 1; }
    exec "$CMD_CHECK_SINGLE" "$2"
    ;;
  
  batch)
    exec "$CMD_CHECK_BATCH"
    ;;
  
  update-lookup)
    exec "$CMD_UPDATE_LOOKUP"
    ;;
  
  config)
    cat "$SCRIPT_DIR/config/batch-config.json"
    ;;
  
  add)
    [[ $# -lt 2 ]] && { echo "Error: add requires a URL"; exit 1; }
    URL="$2"
    jq --arg url "$URL" '.links += [$url] | .links |= unique' "$SCRIPT_DIR/config/batch-config.json" > "$SCRIPT_DIR/config/batch-config.json.tmp"
    mv "$SCRIPT_DIR/config/batch-config.json.tmp" "$SCRIPT_DIR/config/batch-config.json"
    echo "✓ Added: $URL"
    ;;
  
  remove)
    [[ $# -lt 2 ]] && { echo "Error: remove requires a URL"; exit 1; }
    URL="$2"
    jq --arg url "$URL" '.links -= [$url]' "$SCRIPT_DIR/config/batch-config.json" > "$SCRIPT_DIR/config/batch-config.json.tmp"
    mv "$SCRIPT_DIR/config/batch-config.json.tmp" "$SCRIPT_DIR/config/batch-config.json"
    echo "✓ Removed: $URL"
    ;;
  
  list)
    echo "Monitored TestFlight Apps:"
    jq -r '.links[]' "$SCRIPT_DIR/config/batch-config.json" | while read -r url; do
      CODE=$(echo "$url" | grep -oE '[A-Za-z0-9]{8}$')
      APP_NAME=$("$CMD_LOOKUP" "$CODE" 2>/dev/null || echo "$CODE")
      echo "  - $APP_NAME ($url)"
    done
    ;;
  
  state)
    cat "$SCRIPT_DIR/config/batch-state.json"
    ;;
  
  help|--help|-h)
    usage
    ;;
  
  *)
    echo "Error: Unknown command '$1'"
    echo ""
    usage
    exit 1
    ;;
esac
