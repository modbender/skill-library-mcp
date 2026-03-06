#!/bin/bash
# Auto-sync heysummon skill to GitHub every hour
# Checks for changes and pushes if any are found

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$SKILL_DIR" || exit 1

# Check if there are any changes
git add -A
if git diff --cached --quiet; then
  # No changes
  exit 0
fi

# Commit and push changes
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
git commit -m "Auto-sync: $TIMESTAMP" --quiet
git push origin main --quiet

echo "✅ Synced to GitHub: $TIMESTAMP"
