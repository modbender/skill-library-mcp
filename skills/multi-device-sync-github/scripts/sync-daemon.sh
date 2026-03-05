#!/bin/bash
# Sync daemon - manages background sync process with auto-push
# Supports both Linux (inotifywait) and macOS (fswatch)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYNC_REPO="${SYNC_REPO:-$HOME/openclaw-sync}"
PIDFILE="$HOME/.openclaw/sync-daemon.pid"
PUSH_PIDFILE="$HOME/.openclaw/sync-push-watcher.pid"
LOGFILE="$HOME/.openclaw/sync-daemon.log"
CONFIG_FILE="$HOME/.config/openclaw/sync-config.yaml"

# Detect OS
OS="$(uname -s)"

# Load interval from config
INTERVAL=300  # default 5 minutes
if [[ -f "$CONFIG_FILE" ]]; then
    CONFIG_INTERVAL=$(grep "sync_interval_minutes:" "$CONFIG_FILE" | awk '{print $2}')
    if [[ -n "$CONFIG_INTERVAL" ]]; then
        INTERVAL=$((CONFIG_INTERVAL * 60))
    fi
fi

# Get file watcher command based on OS
get_watcher_cmd() {
    if [[ "$OS" == "Darwin" ]]; then
        # macOS - use fswatch
        if ! command -v fswatch &> /dev/null; then
            echo ""
            return 1
        fi
        echo "fswatch"
    else
        # Linux - use inotifywait
        if ! command -v inotifywait &> /dev/null; then
            echo ""
            return 1
        fi
        echo "inotifywait"
    fi
}

start_push_watcher() {
    if [[ -f "$PUSH_PIDFILE" ]] && kill -0 $(cat "$PUSH_PIDFILE") 2>/dev/null; then
        echo "Push watcher already running (PID: $(cat $PUSH_PIDFILE))"
        return 0
    fi
    
    WATCHER_CMD=$(get_watcher_cmd)
    
    if [[ -z "$WATCHER_CMD" ]]; then
        echo "⚠ No file watcher found. Auto-push disabled."
        if [[ "$OS" == "Darwin" ]]; then
            echo "  Install: brew install fswatch"
        else
            echo "  Install: sudo apt-get install inotify-tools"
        fi
        return 1
    fi
    
    mkdir -p "$(dirname "$PUSH_PIDFILE")"
    
    # Start file watcher in background
    (
        exec >> "$LOGFILE" 2>&1
        echo "=== Push Watcher Started at $(date) ==="
        echo "OS: $OS, Watcher: $WATCHER_CMD"
        
        cd "$SYNC_REPO"
        
        if [[ "$WATCHER_CMD" == "fswatch" ]]; then
            # macOS - fswatch
            fswatch -r --exclude "\.git" --exclude "\.sync-conflicts" . 2>/dev/null | while read -r file; do
                
                # Skip if in conflict state
                if [[ -f "$SYNC_REPO/.sync-conflicts" ]]; then
                    continue
                fi
                
                # Debounce: wait 2 seconds for more changes
                sleep 2
                
                # Check if still changes pending
                if git diff --quiet HEAD 2>/dev/null && git diff --cached --quiet 2>/dev/null; then
                    continue
                fi
                
                echo "[$(date)] File changed: $file, pushing..."
                "$SCRIPT_DIR/sync-push.sh" || echo "[$(date)] Push failed"
            done
        else
            # Linux - inotifywait
            inotifywait -m -r -e modify,create,delete,move \
                --exclude '\.git|\.sync-conflicts|\.sync-conflict\.log' \
                . 2>/dev/null | while read path action file; do
                    
                    # Skip if in conflict state
                    if [[ -f "$SYNC_REPO/.sync-conflicts" ]]; then
                        continue
                    fi
                    
                    # Debounce: wait 2 seconds for more changes
                    sleep 2
                    
                    # Check if still changes pending
                    if git diff --quiet HEAD 2>/dev/null && git diff --cached --quiet 2>/dev/null; then
                        continue
                    fi
                    
                    echo "[$(date)] File changed: $path$file ($action), pushing..."
                    "$SCRIPT_DIR/sync-push.sh" || echo "[$(date)] Push failed"
                done
        fi
    ) &
    
    echo $! > "$PUSH_PIDFILE"
    echo "Push watcher started (PID: $(cat $PUSH_PIDFILE), using $WATCHER_CMD)"
}

stop_push_watcher() {
    if [[ -f "$PUSH_PIDFILE" ]]; then
        PID=$(cat "$PUSH_PIDFILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID" 2>/dev/null || true
            # Also kill any child processes
            pkill -P "$PID" 2>/dev/null || true
            rm -f "$PUSH_PIDFILE"
            echo "Push watcher stopped"
        else
            rm -f "$PUSH_PIDFILE"
            echo "Push watcher not running (stale pidfile removed)"
        fi
    else
        echo "Push watcher not running"
    fi
}

start_daemon() {
    if [[ -f "$PIDFILE" ]] && kill -0 $(cat "$PIDFILE") 2>/dev/null; then
        echo "Pull daemon already running (PID: $(cat $PIDFILE))"
    else
        mkdir -p "$(dirname "$PIDFILE")"
        
        # Start pull daemon in background
        (
            exec >> "$LOGFILE" 2>&1
            echo "=== Pull Daemon Started at $(date) ==="
            echo "OS: $OS, Interval: ${INTERVAL}s"
            
            # Initial pull on start
            if [[ -f "$CONFIG_FILE" ]]; then
                AUTO_PULL=$(grep "auto_pull_on_start:" "$CONFIG_FILE" | awk '{print $2}')
                if [[ "$AUTO_PULL" == "true" ]]; then
                    echo "[$(date)] Initial pull..."
                    "$SCRIPT_DIR/sync-pull.sh" || true
                fi
            fi
            
            # Main loop
            while true; do
                sleep "$INTERVAL"
                
                # Skip if in conflict state
                if [[ -f "$SYNC_REPO/.sync-conflicts" ]]; then
                    echo "[$(date)] Conflict state, skipping pull"
                    continue
                fi
                
                # Pull remote changes
                if ! "$SCRIPT_DIR/sync-pull.sh"; then
                    echo "[$(date)] Pull failed or conflict detected"
                fi
            done
        ) &
        
        echo $! > "$PIDFILE"
        echo "Pull daemon started (PID: $(cat $PIDFILE), Interval: ${INTERVAL}s)"
    fi
    
    # Also start push watcher
    start_push_watcher
    
    echo "Log: $LOGFILE"
}

stop_daemon() {
    stop_push_watcher
    
    if [[ -f "$PIDFILE" ]]; then
        PID=$(cat "$PIDFILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            rm -f "$PIDFILE"
            echo "Pull daemon stopped"
        else
            rm -f "$PIDFILE"
            echo "Pull daemon not running (stale pidfile removed)"
        fi
    else
        echo "Pull daemon not running"
    fi
}

status_daemon() {
    echo "=== Sync Daemon Status ==="
    echo ""
    echo "OS: $OS"
    echo ""
    
    # Pull daemon
    if [[ -f "$PIDFILE" ]] && kill -0 $(cat "$PIDFILE") 2>/dev/null; then
        echo "Pull daemon: Running (PID: $(cat $PIDFILE))"
    else
        echo "Pull daemon: Not running"
        rm -f "$PIDFILE" 2>/dev/null
    fi
    
    # Push watcher
    if [[ -f "$PUSH_PIDFILE" ]] && kill -0 $(cat "$PUSH_PIDFILE") 2>/dev/null; then
        echo "Push watcher: Running (PID: $(cat $PUSH_PIDFILE))"
        WATCHER_CMD=$(get_watcher_cmd)
        [[ -n "$WATCHER_CMD" ]] && echo "  Using: $WATCHER_CMD"
    else
        echo "Push watcher: Not running"
        rm -f "$PUSH_PIDFILE" 2>/dev/null
    fi
    
    echo ""
    echo "Log: $LOGFILE"
    if [[ -f "$LOGFILE" ]]; then
        echo "Last 5 log entries:"
        tail -5 "$LOGFILE" 2>/dev/null | sed 's/^/  /'
    fi
}

case "${1:-}" in
    start)
        start_daemon
        ;;
    stop)
        stop_daemon
        ;;
    restart)
        stop_daemon
        sleep 1
        start_daemon
        ;;
    status)
        status_daemon
        ;;
    *)
        echo "Usage: sync-daemon {start|stop|restart|status}"
        exit 1
        ;;
esac
