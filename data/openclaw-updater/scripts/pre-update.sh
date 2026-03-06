#!/bin/bash
# Pre-update safety checks: commit all workspaces + backup config
set -e

OPENCLAW_DIR="${OPENCLAW_DIR:-$HOME/.openclaw}"
BACKUP_SCRIPT="${BACKUP_SCRIPT:-}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🔍 Finding workspaces from config..."
mapfile -t WORKSPACES < <(bash "$SCRIPT_DIR/find-workspaces.sh" 2>/dev/null)

if [ ${#WORKSPACES[@]} -eq 0 ]; then
  echo "⚠️  No workspaces found. Check your openclaw.json"
  exit 1
fi

# 1. Git commit all workspaces
for ws in "${WORKSPACES[@]}"; do
  name=$(basename "$ws")
  if [ ! -d "$ws/.git" ]; then
    echo "📦 $name: no git — initializing..."
    cd "$ws" && git init && git add -A && git commit -m "init before update $(date +%Y%m%d-%H%M%S)"
  else
    cd "$ws"
    git add -A 2>/dev/null
    if git diff --cached --quiet 2>/dev/null; then
      echo "✅ $name: clean"
    else
      git commit -m "pre-update snapshot $(date +%Y%m%d-%H%M%S)"
      echo "✅ $name: committed"
    fi
  fi
done

# 2. Backup openclaw.json
if [ -f "$OPENCLAW_DIR/openclaw.json" ]; then
  cp "$OPENCLAW_DIR/openclaw.json" /tmp/openclaw.json.bak
  echo "✅ Config backed up to /tmp/openclaw.json.bak"
fi

# 3. Run backup script if provided
if [ -n "$BACKUP_SCRIPT" ] && [ -x "$BACKUP_SCRIPT" ]; then
  echo "📦 Running backup script..."
  "$BACKUP_SCRIPT"
fi

# 4. Record current version for rollback
VERSION=$(openclaw --version 2>/dev/null || echo "unknown")
echo "$VERSION" > /tmp/openclaw-prev-version.txt
echo "✅ Current version: $VERSION (saved to /tmp/openclaw-prev-version.txt)"

echo ""
echo "🟢 Pre-update checks complete. Safe to run: openclaw update"
