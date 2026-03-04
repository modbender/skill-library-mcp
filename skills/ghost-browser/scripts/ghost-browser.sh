#!/bin/bash
# Ghost Browser - CLI wrapper
# Provides a simple interface to the Python daemon

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_SCRIPT="$SKILL_DIR/scripts/ghost_browser.py"
VENV_PYTHON="$SKILL_DIR/.venv/bin/python3"

# Check for venv
if [[ -x "$VENV_PYTHON" ]]; then
    exec "$VENV_PYTHON" "$PYTHON_SCRIPT" "$@"
fi

# Fallback to system Python
if ! command -v python3 &> /dev/null; then
    echo '{"status":"error","error":"python_not_found","message":"Python3 is required. Run setup.sh first."}' >&2
    exit 1
fi

# Check nodriver
if ! python3 -c "import nodriver" 2>/dev/null; then
    echo '{"status":"error","error":"nodriver_not_installed","message":"nodriver not installed. Run setup.sh or: pip install nodriver"}' >&2
    exit 1
fi

exec python3 "$PYTHON_SCRIPT" "$@"
