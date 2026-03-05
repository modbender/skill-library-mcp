#!/bin/bash
# Discord Project Manager - Bash CLI Wrapper

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
PYTHON_CLI="$SKILL_DIR/scripts/discord-pm.py"

# Check if Python CLI exists
if [ ! -f "$PYTHON_CLI" ]; then
    echo "Error: Python CLI not found at $PYTHON_CLI"
    exit 1
fi

# Execute Python CLI with all arguments
exec python3 "$PYTHON_CLI" "$@"
