#!/bin/bash
# Wrapper: activate venv and run get-stats.py
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."
source venv/bin/activate
python scripts/get-stats.py "$@"
