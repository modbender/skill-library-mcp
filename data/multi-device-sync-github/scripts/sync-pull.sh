#!/bin/bash
# Pull remote changes, handle conflicts

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYNC_REPO="${SYNC_REPO:-$HOME/openclaw-sync}"
CONFIG_FILE="$HOME/.config/openclaw/sync-config.yaml"

cd "$SYNC_REPO"

# Check if git repo
if [[ ! -d ".git" ]]; then
    echo "Error: Not a git repository. Run sync-init first."
    exit 1
fi

# Check if remote is configured
if ! git remote | grep -q "origin"; then
    echo "Error: No remote 'origin' configured."
    echo "Run: git remote add origin <your-repo-url>"
    exit 1
fi

# Fetch remote changes
git fetch origin 2>/dev/null || {
    echo "Warning: Failed to fetch from origin (network issue?)"
    exit 0
}

# Determine the main branch
MAIN_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')

if [[ -z "$MAIN_BRANCH" ]]; then
    MAIN_BRANCH=$(git branch -r | grep -o 'origin/[^ ]*' | head -1 | sed 's@origin/@@' || echo "main")
fi

# Check if remote branch exists
if ! git rev-parse "origin/$MAIN_BRANCH" >/dev/null 2>&1; then
    # Try master if main doesn't exist
    if git rev-parse "origin/master" >/dev/null 2>&1; then
        MAIN_BRANCH="master"
    else
        echo "No remote branch found. Nothing to pull."
        exit 0
    fi
fi

# Check if there are remote changes
LOCAL=$(git rev-parse HEAD 2>/dev/null || echo "")
REMOTE=$(git rev-parse "origin/$MAIN_BRANCH")

if [[ -z "$LOCAL" ]]; then
    # No local commits, just checkout remote
    git checkout -B "$MAIN_BRANCH" "origin/$MAIN_BRANCH"
    echo "✓ Checked out $MAIN_BRANCH from remote"
    exit 0
fi

if [[ "$LOCAL" == "$REMOTE" ]]; then
    # No changes to pull
    exit 0
fi

# Check if we have uncommitted changes
if ! git diff --quiet HEAD 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
    # Stash changes before pull
    echo "Stashing local changes..."
    git stash push -m "auto-stash before pull at $(date '+%H:%M:%S')"
    STASHED=true
fi

# Try to pull (rebase)
if git pull --rebase origin "$MAIN_BRANCH" 2>/dev/null; then
    echo "✓ Pulled remote changes at $(date '+%H:%M:%S')"
    
    # Restore stashed changes if any
    if [[ "$STASHED" == "true" ]]; then
        if git stash pop 2>/dev/null; then
            echo "✓ Restored local changes"
        fi
    fi
    
    exit 0
fi

# Conflict detected
echo "⚠ CONFLICT DETECTED"

# Get conflicted files
CONFLICTS=$(git diff --name-only --diff-filter=U 2>/dev/null || echo "")

if [[ -z "$CONFLICTS" ]]; then
    # Rebase conflict, get files from status
    CONFLICTS=$(git status --porcelain | grep "^UU\|^AA\|^DD" | cut -c4-)
fi

# Send notification
if command -v "$SCRIPT_DIR/sync-notify" &> /dev/null; then
    "$SCRIPT_DIR/sync-notify" "conflict" "$CONFLICTS"
fi

# Mark conflict state
echo "$(date): CONFLICT - $CONFLICTS" >> "$SYNC_REPO/.sync-conflict.log"
echo "$CONFLICTS" > "$SYNC_REPO/.sync-conflicts"

echo ""
echo "Conflicting files:"
echo "$CONFLICTS" | while read -r file; do
    echo "  - $file"
done
echo ""
echo "Run to resolve: sync-resolve"
echo "Auto-sync paused until resolved."

exit 1
