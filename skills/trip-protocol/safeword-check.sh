#!/bin/bash
# safeword-check.sh - Detect safeword phrases and trigger bail
# Usage: ./safeword-check.sh "<message text>"
# Called when agent detects "bad trip" or "trip abort" in conversation

set -e

MESSAGE="${1:-}"
SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"

# Check for safeword phrases (case-insensitive)
if echo "$MESSAGE" | grep -qi -E "bad trip|trip abort|stop trip|end trip|safeword"; then
    echo "[trip] ⚡ Safeword detected! Initiating bail..."
    exec "$SKILL_DIR/restore.sh" --bail
fi
