#!/bin/bash
# Location awareness wrapper - loads credentials and runs location.py

# Source OpenClaw .env if available (provides HA_URL, HA_TOKEN, etc.)
[[ -f "$HOME/.openclaw/.env" ]] && set -a && source "$HOME/.openclaw/.env" && set +a

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/location.py" "$@"
