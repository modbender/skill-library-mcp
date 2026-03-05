#!/bin/bash
# Check for ClawLife skill updates and apply if available
# Usage: update.sh [--check-only]
# Returns: "UP_TO_DATE" or "UPDATED from X to Y" or "UPDATE_AVAILABLE X -> Y" (check-only)

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VERSION_FILE="$SKILL_DIR/VERSION"
CHECK_ONLY=false

[ "${1:-}" = "--check-only" ] && CHECK_ONLY=true

LOCAL_VERSION="unknown"
[ -f "$VERSION_FILE" ] && LOCAL_VERSION=$(cat "$VERSION_FILE" | tr -d '[:space:]')

# Fetch remote version (lightweight, just the VERSION file)
REMOTE_VERSION=$(curl -fsSL --max-time 5 \
  "https://raw.githubusercontent.com/mithri-claws/clawlife-skill/main/VERSION" 2>/dev/null | tr -d '[:space:]') || {
  echo "⚠️  Could not check for updates (network error)"
  exit 0
}

if [ "$LOCAL_VERSION" = "$REMOTE_VERSION" ]; then
  echo "UP_TO_DATE ($LOCAL_VERSION)"
  exit 0
fi

if $CHECK_ONLY; then
  echo "UPDATE_AVAILABLE $LOCAL_VERSION -> $REMOTE_VERSION"
  exit 0
fi

# Apply update via git
echo "🔄 Updating ClawLife skill: $LOCAL_VERSION → $REMOTE_VERSION"
cd "$SKILL_DIR"
git checkout -- . 2>/dev/null || true
git pull --quiet origin main 2>/dev/null || git pull --quiet
chmod +x scripts/*.sh 2>/dev/null || true

NEW_VERSION=$(cat VERSION | tr -d '[:space:]')
echo "UPDATED $LOCAL_VERSION -> $NEW_VERSION"
