#!/usr/bin/env bash
set -euo pipefail
cd /home/moltuser/clawd/skills/notebooklm-mcp
./scripts/notebooklm-auth.sh status
./scripts/notebooklm-list.sh
