#!/bin/bash
# Push local changes to remote
# Safety: Only operates on files in sync config

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYNC_REPO="${SYNC_REPO:-$HOME/openclaw-sync}"
CONFIG_FILE="$HOME/.config/openclaw/sync-config.yaml"

# Load config
if [[ -f "$CONFIG_FILE" ]]; then
    DEVICE_NAME=$(grep "device_name:" "$CONFIG_FILE" | awk '{print $2}' | tr -d '"')
    AUTO_PUSH=$(grep "auto_push_enabled:" "$CONFIG_FILE" | awk '{print $2}' | tr -d '"' || echo "false")
else
    DEVICE_NAME="unknown"
    AUTO_PUSH="false"
fi
DEVICE_NAME="${DEVICE_NAME:-unknown}"

cd "$SYNC_REPO"

# Check if git repo
if [[ ! -d ".git" ]]; then
    echo "Error: Not a git repository. Run sync-init.sh first."
    exit 1
fi

# Check if remote is configured
if ! git remote | grep -q "origin"; then
    echo "Error: No remote 'origin' configured."
    echo "Run: git remote add origin <your-repo-url>"
    exit 1
fi

# === SAFETY: Only add specific files from config ===
# Read sync paths from config
if [[ -f "$CONFIG_FILE" ]]; then
    SYNC_PATHS=$(grep -A 10 "paths:" "$CONFIG_FILE" | grep "^    - " | sed 's/^    - //' | tr -d '"')
fi

# If no config, use defaults
if [[ -z "$SYNC_PATHS" ]]; then
    SYNC_PATHS="USER.md MEMORY.md SOUL.md skills/ memory/ TOOLS.md"
fi

# Add only configured paths
echo "Adding configured files..."
for path in $SYNC_PATHS; do
    if [[ -e "$path" ]]; then
        git add "$path"
    fi
done

# Check if there's anything to commit
if git diff --cached --quiet 2>/dev/null; then
    echo "No changes to commit"
    exit 0
fi

# Show what will be committed
echo ""
echo "Files to be committed:"
git diff --cached --stat
echo ""

# Confirm before commit (unless auto-push)
if [[ "$AUTO_PUSH" != "true" ]]; then
    read -p "Commit and push? [y/N]: " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        echo "Cancelled"
        exit 0
    fi
fi

# Commit with device info
COMMIT_MSG="sync(${DEVICE_NAME}): update at $(date '+%Y-%m-%d %H:%M:%S')"
git commit -m "$COMMIT_MSG"

# Determine the main branch
MAIN_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || git branch --show-current)

if [[ -z "$MAIN_BRANCH" ]]; then
    MAIN_BRANCH="main"
fi

# Try to push
MAX_RETRIES=2
RETRY_COUNT=0

while [[ $RETRY_COUNT -lt $MAX_RETRIES ]]; do
    if git push origin "$MAIN_BRANCH" 2>/dev/null; then
        echo "✓ Pushed: $COMMIT_MSG"
        exit 0
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        
        if [[ $RETRY_COUNT -lt $MAX_RETRIES ]]; then
            echo "⚠ Push failed, pulling and retrying..."
            
            # Pull first
            "$SCRIPT_DIR/sync-pull.sh" || true
            
            # Rebase our commit on top
            git rebase "origin/$MAIN_BRANCH" 2>/dev/null || {
                echo "⚠ Rebase failed, conflict detected"
                exit 1
            }
        fi
    fi
done

echo "⚠ Push failed after $MAX_RETRIES attempts"
exit 1
