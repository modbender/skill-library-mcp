#!/bin/bash
# Obsidian OpenClaw Sync Skill
# This script is the entry point for the /obsidian-openclaw-sync skill

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/scripts/sync_helper.py"

# Find Python interpreter (prefer python3, fallback to python)
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Error: Python interpreter not found. Please install Python 3."
    exit 1
fi

# Run the Python script with all passed arguments
"$PYTHON_CMD" "$PYTHON_SCRIPT" "$@"
