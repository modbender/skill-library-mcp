#!/usr/bin/env bash
set -euo pipefail
TARGET_DIR="${1:-./multi-agent-system}"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$SKILL_DIR/assets/blueprint"
mkdir -p "$TARGET_DIR"
cp -R "$SRC"/* "$TARGET_DIR"/
chmod +x "$TARGET_DIR"/scripts/taskctl.py "$TARGET_DIR"/scripts/mailboxctl.py
printf "installed:%s\n" "$TARGET_DIR"
