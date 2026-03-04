#!/usr/bin/env bash
# Setup venv and install dependencies for tradingview-screener skill
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
REQ_FILE="$SCRIPT_DIR/scripts/requirements.txt"

# Find Python 3
find_python() {
  for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
      ver=$("$cmd" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
      major=$(echo "$ver" | cut -d. -f1)
      if [ "$major" = "3" ]; then
        echo "$cmd"
        return 0
      fi
    fi
  done
  return 1
}

PYTHON=$(find_python) || {
  echo "ERROR: Python 3 not found. Install Python 3.9+ first."
  exit 1
}

echo "Using $PYTHON ($($PYTHON --version 2>&1))"

# Create venv if missing
if [ ! -f "$VENV_DIR/bin/python3" ] && [ ! -f "$VENV_DIR/Scripts/python.exe" ]; then
  echo "Creating venv at $VENV_DIR..."
  "$PYTHON" -m venv "$VENV_DIR"
fi

# Determine pip path (cross-platform)
if [ -f "$VENV_DIR/bin/pip" ]; then
  PIP="$VENV_DIR/bin/pip"
elif [ -f "$VENV_DIR/Scripts/pip.exe" ]; then
  PIP="$VENV_DIR/Scripts/pip.exe"
else
  echo "ERROR: pip not found in venv"
  exit 1
fi

# Install dependencies
echo "Installing dependencies..."
"$PIP" install --no-user -q -r "$REQ_FILE"

echo "Setup complete."
