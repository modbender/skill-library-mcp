#!/bin/bash
# Look up TestFlight app name by code

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CUSTOM_CODES="$SKILL_ROOT/config/custom-codes.json"
CODES_FILE="$SKILL_ROOT/config/testflight-codes.json"

CODE="${1:-}"

if [[ -z "$CODE" ]]; then
  echo "Usage: lookup.sh <code>" >&2
  exit 1
fi

if [[ ! -f "$CODES_FILE" ]]; then
  echo "Error: $CODES_FILE not found. Run update-lookup first." >&2
  exit 1
fi

# Check custom codes first (for private betas)
if [[ -f "$CUSTOM_CODES" ]]; then
  CUSTOM_NAME=$(jq -r --arg code "$CODE" '.[$code] // null' "$CUSTOM_CODES")
  if [[ "$CUSTOM_NAME" != "null" ]]; then
    echo "$CUSTOM_NAME"
    exit 0
  fi
fi

# Fall back to awesome-testflight-link list
APP_NAME=$(jq -r --arg code "$CODE" '.[$code] // "Unknown"' "$CODES_FILE")

if [[ "$APP_NAME" == "Unknown" ]]; then
  echo "$CODE"  # Return code itself if not found
  exit 0
fi

echo "$APP_NAME"
