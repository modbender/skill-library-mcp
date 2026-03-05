#!/bin/bash
# Kimi Usage Check - Browser-based version
# Usage: ./check_usage.sh [--json]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
python3 scripts/fetch_usage.py "$@"
