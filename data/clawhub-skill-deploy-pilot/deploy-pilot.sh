#!/bin/bash
# deploy-pilot — Bash wrapper and helper functions

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/deploy-pilot.py"
WORKSPACE="${HOME}/.openclaw/workspace/deploy-pilot"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ensure Python script is executable
chmod +x "$PYTHON_SCRIPT" 2>/dev/null || true

# Delegate to Python for all commands
# This wrapper can be extended with bash-specific helpers if needed
exec python3 "$PYTHON_SCRIPT" "$@"
