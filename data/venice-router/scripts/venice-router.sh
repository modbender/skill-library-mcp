#!/usr/bin/env bash
# venice-router.sh — Thin wrapper for the Python router
# Usage: venice-router.sh [args...]
# All arguments are passed through to venice-router.py

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/venice-router.py" "$@"
