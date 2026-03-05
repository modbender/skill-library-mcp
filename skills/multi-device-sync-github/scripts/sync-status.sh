#!/bin/bash
# Check sync status

SYNC_REPO="${SYNC_REPO:-$HOME/openclaw-sync}"
CONFIG_FILE="$HOME/.config/openclaw/sync-config.yaml"
PIDFILE="$HOME/.openclaw/sync-daemon.pid"
PUSH_PIDFILE="$HOME/.openclaw/sync-push-watcher.pid"

echo "=== OpenClaw Sync Status ==="
echo ""

# Device info
if [[ -f "$CONFIG_FILE" ]]; then
    echo "Config: $CONFIG_FILE"
    grep -E "(device_name|sync_interval|repo_url)" "$CONFIG_FILE" | sed 's/^/  /'
else
    echo "Config: Not found"
fi
echo ""

# Daemon status
echo "Daemons:"
if [[ -f "$PIDFILE" ]] && kill -0 $(cat "$PIDFILE") 2>/dev/null; then
    echo "  Pull daemon: Running (PID: $(cat $PIDFILE))"
else
    echo "  Pull daemon: Not running"
fi

if [[ -f "$PUSH_PIDFILE" ]] && kill -0 $(cat "$PUSH_PIDFILE") 2>/dev/null; then
    echo "  Push watcher: Running (PID: $(cat $PUSH_PIDFILE))"
else
    echo "  Push watcher: Not running"
fi
echo ""

# Git status
cd "$SYNC_REPO" 2>/dev/null || {
    echo "Error: Cannot access $SYNC_REPO"
    echo "Run: sync-init --device-name <name>"
    exit 1
}

echo "Repository: $SYNC_REPO"
echo ""

# Check remote
if git remote -v > /dev/null 2>&1; then
    echo "Remote:"
    git remote -v | head -2 | sed 's/^/  /'
else
    echo "Remote: Not configured"
fi
echo ""

# Branch status
echo "Branch:"
git status -sb | sed 's/^/  /'
echo ""

# Last sync info
if [[ -f "$SYNC_REPO/.git/FETCH_HEAD" ]]; then
    LAST_FETCH=$(stat -c %Y "$SYNC_REPO/.git/FETCH_HEAD" 2>/dev/null || stat -f %m "$SYNC_REPO/.git/FETCH_HEAD" 2>/dev/null)
    if [[ -n "$LAST_FETCH" ]]; then
        echo "Last fetch: $(date -d @$LAST_FETCH '+%Y-%m-%d %H:%M:%S')"
    fi
fi
echo ""

# Conflict state
if [[ -f ".sync-conflicts" ]]; then
    echo "⚠ CONFLICT STATE ACTIVE"
    echo "Conflicting files:"
    cat ".sync-conflicts" | sed 's/^/  /'
    echo ""
    echo "Run 'sync-resolve' to fix"
else
    # Check for unstaged changes
    if ! git diff --quiet HEAD 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
        echo "Local changes: Pending commit"
        git status -s | sed 's/^/  /'
    else
        echo "Status: Clean (up to date)"
    fi
fi

# Show recent commits
echo ""
echo "Recent commits:"
git log --oneline -5 2>/dev/null | sed 's/^/  /' || echo "  No commits yet"
