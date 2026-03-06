#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
chmod +x "$SCRIPT_DIR/token-optimize" "$SCRIPT_DIR/token_optimize.py"
echo "Installed token-optimizer scripts."
