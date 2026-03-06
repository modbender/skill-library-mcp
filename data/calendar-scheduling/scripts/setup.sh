#!/usr/bin/env bash
# setup.sh — Set up the Temporal Cortex MCP server and authenticate with a calendar provider
set -euo pipefail

PROVIDER="${1:-google}"

# Cloud mode: print hosted MCP config and exit
if [[ "$PROVIDER" == "--cloud" ]]; then
  echo "=== Temporal Cortex Cloud Mode ==="
  echo ""
  echo "No local setup required. Sign up at https://app.temporal-cortex.com"
  echo "to get your API key, then configure your MCP client:"
  echo ""
  echo '{'
  echo '  "mcpServers": {'
  echo '    "temporal-cortex": {'
  echo '      "url": "https://mcp.temporal-cortex.com/mcp",'
  echo '      "headers": { "Authorization": "Bearer YOUR_API_KEY" }'
  echo '    }'
  echo '  }'
  echo '}'
  echo ""
  echo "Replace YOUR_API_KEY with the key from your dashboard."
  echo "All 12 tools work identically in cloud mode."
  exit 0
fi

echo "=== Temporal Cortex Calendar Setup ==="
echo ""

# Check Node.js version
if ! command -v node &>/dev/null; then
  echo "ERROR: Node.js is not installed."
  echo "Install Node.js 18+ from https://nodejs.org"
  exit 1
fi

NODE_VERSION=$(node -v | sed 's/v//' | cut -d. -f1)
if [[ "$NODE_VERSION" -lt 18 ]]; then
  echo "ERROR: Node.js 18+ required (found v$(node -v))"
  echo "Update from https://nodejs.org"
  exit 1
fi

echo "Node.js $(node -v) detected"
echo ""

# Validate provider
case "$PROVIDER" in
  google|outlook|caldav)
    echo "Provider: ${PROVIDER}"
    ;;
  *)
    echo "ERROR: Unknown provider '${PROVIDER}'"
    echo "Supported providers: google, outlook, caldav"
    echo ""
    echo "Usage: setup.sh [provider|--cloud]"
    echo "  setup.sh           # defaults to google"
    echo "  setup.sh google"
    echo "  setup.sh outlook"
    echo "  setup.sh caldav"
    echo "  setup.sh --cloud   # print cloud mode config"
    exit 1
    ;;
esac

echo ""
echo "Starting setup flow..."
echo "This will guide you through calendar connection and configuration."
echo ""

# Prefer `setup` (interactive guided setup), fall back to `auth` for provider-specific flow
if npx -y @temporal-cortex/cortex-mcp@0.5.0 setup 2>/dev/null; then
  : # setup succeeded
else
  echo "Falling back to provider-specific auth flow..."
  echo "This will open your browser for calendar access consent."
  echo ""
  npx -y @temporal-cortex/cortex-mcp@0.5.0 auth "$PROVIDER"
fi

# Verify credentials
CONFIG_DIR="${HOME}/.config/temporal-cortex"
if [[ -f "${CONFIG_DIR}/credentials.json" ]]; then
  echo ""
  echo "Credentials saved to ${CONFIG_DIR}/credentials.json"

  if [[ -f "${CONFIG_DIR}/config.json" ]]; then
    echo "Configuration saved to ${CONFIG_DIR}/config.json"
  fi

  echo ""
  echo "Setup complete. All 12 MCP tools are now available:"
  echo "  Layer 0: list_calendars"
  echo "  Layer 1: get_temporal_context, resolve_datetime, convert_timezone,"
  echo "           compute_duration, adjust_timestamp"
  echo "  Layer 2: list_events, find_free_slots, expand_rrule, check_availability"
  echo "  Layer 3: get_availability"
  echo "  Layer 4: book_slot"
  echo ""
  echo "To connect additional providers, run:"
  echo "  bash setup.sh outlook"
  echo "  bash setup.sh caldav"
else
  echo ""
  echo "WARNING: Credentials file not found at ${CONFIG_DIR}/credentials.json"
  echo "Authentication may not have completed. Try running again."
  exit 1
fi
