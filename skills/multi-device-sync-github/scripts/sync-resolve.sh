#!/bin/bash
# Interactive conflict resolution

set -e

SYNC_REPO="${SYNC_REPO:-$HOME/openclaw-sync}"
cd "$SYNC_REPO"

# Check if in conflict state or rebase in progress
IN_CONFLICT=false

if [[ -f ".sync-conflicts" ]]; then
    IN_CONFLICT=true
fi

if [[ -d ".git/rebase-merge" ]] || [[ -d ".git/rebase-apply" ]]; then
    IN_CONFLICT=true
fi

# Check for unmerged files
UNMERGED=$(git diff --name-only --diff-filter=U 2>/dev/null || echo "")

if [[ "$IN_CONFLICT" != "true" ]] && [[ -z "$UNMERGED" ]]; then
    echo "No active conflicts detected."
    echo "Repository is clean."
    exit 0
fi

echo "=== Sync Conflict Resolution ==="
echo ""

# List conflicted files
echo "Conflicted files:"
if [[ -n "$UNMERGED" ]]; then
    echo "$UNMERGED" | while read -r file; do
        echo "  - $file"
    done
elif [[ -f ".sync-conflicts" ]]; then
    cat ".sync-conflicts" | while read -r file; do
        echo "  - $file"
    done
fi
echo ""

# Options
echo "Resolution options:"
echo "  1) Keep LOCAL (your changes)"
echo "  2) Keep REMOTE (their changes)"
echo "  3) Merge manually (opens editor)"
echo "  4) View diff only"
echo "  5) Abort and keep investigating"
echo ""
read -p "Choose option (1-5): " choice

case $choice in
    1)
        echo "Keeping local changes..."
        git checkout --ours . 2>/dev/null || true
        git add -A
        git rebase --continue 2>/dev/null || {
            # If not in rebase, just commit
            git commit -m "resolve: kept local changes" 2>/dev/null || true
        }
        ;;
    2)
        echo "Keeping remote changes..."
        git checkout --theirs . 2>/dev/null || true
        git add -A
        git rebase --continue 2>/dev/null || {
            git commit -m "resolve: kept remote changes" 2>/dev/null || true
        }
        ;;
    3)
        echo "Opening editor for manual merge..."
        
        # Get list of conflicted files
        CONFLICT_FILES=$(git diff --name-only --diff-filter=U 2>/dev/null || echo "")
        
        if [[ -z "$CONFLICT_FILES" ]]; then
            CONFLICT_FILES=$(cat ".sync-conflicts" 2>/dev/null || echo "")
        fi
        
        # Use EDITOR or fall back to nano
        EDITOR_CMD="${EDITOR:-nano}"
        
        # Open each conflicted file in editor
        if [[ -n "$CONFLICT_FILES" ]]; then
            echo "$CONFLICT_FILES" | xargs $EDITOR_CMD
        else
            echo "No conflicted files found to edit."
            exit 0
        fi
        
        echo ""
        echo "After editing, run:"
        echo "  git add -A"
        echo "  git rebase --continue  # if in rebase"
        echo "  rm .sync-conflicts     # to resume sync"
        exit 0
        ;;
    4)
        echo "=== Diff View ==="
        echo ""
        git diff --name-only --diff-filter=U | while read -r file; do
            echo "=== $file ==="
            echo ""
            # Show conflict markers with context
            grep -n "^<<<<<<" "$file" 2>/dev/null | head -1 && echo "...(local section)..."
            grep -n "^======" "$file" 2>/dev/null | head -1 && echo "...(separator)..."
            grep -n "^>>>>>>" "$file" 2>/dev/null | head -1 && echo "...(remote section)..."
            echo ""
        done
        echo ""
        echo "Run 'sync-resolve' again to resolve."
        exit 0
        ;;
    5)
        echo "Aborted. Conflicts remain."
        echo "Investigate with: git status"
        exit 0
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

# Clean up conflict markers
rm -f ".sync-conflicts"
rm -f ".sync-conflict.log"

echo ""
echo "✓ Conflicts resolved. Sync will resume on next cycle."
