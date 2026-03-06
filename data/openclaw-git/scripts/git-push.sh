#!/bin/bash
# OpenClaw Git Push Script
# Usage: git-push.sh [commit-message]

set -e

REPO_DIR="/home/roger/.openclaw"
DEFAULT_MSG="update: $(date '+%Y-%m-%d %H:%M:%S')"
COMMIT_MSG="${1:-$DEFAULT_MSG}"

echo "====================================="
echo "OpenClaw Git Push"
echo "====================================="
echo ""

# Check if repo exists
if [ ! -d "$REPO_DIR/.git" ]; then
    echo "Error: Not a git repository: $REPO_DIR"
    exit 1
fi

cd "$REPO_DIR"

echo "Repository: $REPO_DIR"
echo "Commit message: $COMMIT_MSG"
echo ""

# Check git status
echo "=== Git Status ==="
git status --short

# Check if there are changes
if [ -z "$(git status --porcelain)" ]; then
    echo ""
    echo "No changes to commit."
    exit 0
fi

echo ""
echo "=== Adding changes ==="
git add .
echo "✅ Changes staged"

echo ""
echo "=== Committing ==="
git commit -m "$COMMIT_MSG"
echo "✅ Committed: $COMMIT_MSG"

echo ""
echo "=== Pushing to origin main ==="
# Push with embedded credentials
git push https://Roger0808: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@github.com/Roger0808/openclaw.git main
echo "✅ Pushed to origin main"

echo ""
echo "====================================="
echo "Success! Changes pushed."
echo "====================================="
