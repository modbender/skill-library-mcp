#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "=== HyperClaw Setup ==="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found. Install Python 3.10+."
    exit 1
fi

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

if [ "$PY_MAJOR" -lt 3 ] || ([ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]); then
    echo "Error: Python 3.10+ required (found $PY_VERSION)"
    exit 1
fi

echo "Python $PY_VERSION found."

# Create venv
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists."
fi

# Install dependencies
echo "Installing dependencies..."
"$VENV_DIR/bin/pip" install -q -r "$SCRIPT_DIR/requirements.txt"

# Create .env from example if it doesn't exist
if [ ! -f "$SKILL_DIR/.env" ]; then
    if [ -f "$SKILL_DIR/.env.example" ]; then
        cp "$SKILL_DIR/.env.example" "$SKILL_DIR/.env"
        echo ""
        echo "Created .env from .env.example"
    fi
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Edit .env with your Hyperliquid credentials:"
echo "     HL_ACCOUNT_ADDRESS=0x..."
echo "     HL_SECRET_KEY=0x..."
echo "     HL_TESTNET=true"
echo ""
echo "  2. Test with:"
echo "     $VENV_DIR/bin/python $SCRIPT_DIR/hyperliquid_tools.py price BTC"
