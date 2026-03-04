#!/bin/bash
# Auto-refresh Claude Code OAuth token

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
TOKEN_FILE="$BASE_DIR/.tokens"

if [ ! -f "$TOKEN_FILE" ]; then
  echo "ERROR: No tokens configured" >&2
  exit 1
fi

source "$TOKEN_FILE"

if [ -z "$REFRESH_TOKEN" ]; then
  echo "ERROR: No refresh token found" >&2
  exit 1
fi

# Refresh via Anthropic API
# Note: This endpoint may not be public yet, using alternative approach
# For now, manual re-login via `claude auth login` is needed

echo "⚠️  Auto-refresh not yet implemented"
echo "Please run: claude auth login"
echo "Then update .tokens file with new credentials"
exit 1

# TODO: Implement proper OAuth refresh flow when API is documented
