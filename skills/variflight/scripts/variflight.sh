#!/bin/bash
# Variflight API wrapper - Universal version
# Supports: OpenClaw, Claude Code, Cursor, and other AI clients
#
# Configuration priority:
# 1. Command line --api-key
# 2. Environment variable VARIFLIGHT_API_KEY
# 3. ./.variflight.json (project config)
# 4. ~/.variflight.json (user config)
# 5. ~/.config/variflight/config.json (XDG standard)
#
# Usage: variflight.sh [--api-key KEY] <endpoint> [key=value ...]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/variflight.py" "$@"
