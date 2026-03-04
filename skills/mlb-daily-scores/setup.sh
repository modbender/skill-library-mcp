#!/usr/bin/env bash
# setup.sh — Install dependencies for the mlb-daily-scores skill.
# Creates a virtual environment in .venv/ and installs packages there.
# Run once after installing the skill.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "=== mlb-daily-scores: Installing dependencies ==="

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR ..."
    python3 -m venv "$VENV_DIR"
fi

VENV_PYTHON="$VENV_DIR/bin/python3"
if [ ! -f "$VENV_PYTHON" ]; then
    VENV_PYTHON="$VENV_DIR/bin/python"
fi

# Install packages into the venv
if command -v uv &>/dev/null; then
    echo "Using uv..."
    uv pip install --python "$VENV_PYTHON" MLB-StatsAPI requests
else
    echo "Using pip..."
    "$VENV_PYTHON" -m pip install MLB-StatsAPI requests
fi

echo "=== mlb-daily-scores: Dependencies installed successfully ==="
echo "    Virtual environment: $VENV_DIR"
echo ""
echo "Next steps:"
echo "  1. Add config to ~/.openclaw/openclaw.json (see SKILL.md)"
echo "  2. Set up the daily cron job (see SKILL.md)"
echo ""
