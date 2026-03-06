#!/bin/bash
# =============================================================
# OpenClaw Gateway Watchdog (v2 - with version check)
# Monitors gateway process and restarts if stuck/dead OR stale version.
# Designed to run via launchd every 10 minutes.
# =============================================================

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

LOG_DIR="$HOME/.openclaw/logs"
LOG_FILE="$LOG_DIR/gateway-watchdog.log"
LOCKFILE="/tmp/openclaw-gateway-watchdog.lock"
COOLDOWN_FILE="/tmp/openclaw-gateway-last-restart"
VERSION_RESTART_FILE="/tmp/openclaw-gateway-last-version-restart"

# Gateway config
GATEWAY_PLIST="$HOME/Library/LaunchAgents/ai.openclaw.gateway.plist"
GATEWAY_LABEL="ai.openclaw.gateway"

# Notification config
DISCORD_CHANNEL=""  # Set your Discord channel ID here for notifications

# Timing config
HEALTH_TIMEOUT=10         # seconds to wait for process check
RETRY_DELAY=10            # seconds between retries
MAX_RETRIES=3             # retries before restarting
COOLDOWN_SECONDS=300      # 5 min cooldown between restarts
VERSION_COOLDOWN=3600     # 1 hour cooldown for version restarts
STALE_THRESHOLD=300       # 5 min - consider gateway stuck if no session activity

mkdir -p "$LOG_DIR"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [watchdog] $1" >> "$LOG_FILE"
}

# Send Discord notification
notify() {
    local message="$1"
    openclaw message send --channel discord --to "$DISCORD_CHANNEL" --message "$message" 2>> "$LOG_FILE" &
}

# Check for version mismatch
check_version() {
    # Get CLI version
    CLI_VERSION=$(openclaw --version 2>/dev/null | head -1)
    if [ -z "$CLI_VERSION" ]; then
        return 0  # Can't determine, assume OK
    fi
    
    # Get running gateway version via status
    GATEWAY_VERSION=$(curl -sf "http://localhost:18789/health" 2>/dev/null | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
    if [ -z "$GATEWAY_VERSION" ]; then
        return 0  # Can't determine, assume OK
    fi
    
    if [ "$CLI_VERSION" != "$GATEWAY_VERSION" ]; then
        log "VERSION MISMATCH: CLI=$CLI_VERSION Gateway=$GATEWAY_VERSION"
        return 1
    fi
    return 0
}

# Rotate log if > 100KB
if [ -f "$LOG_FILE" ] && [ $(stat -f%z "$LOG_FILE" 2>/dev/null || echo 0) -gt 102400 ]; then
    mv "$LOG_FILE" "$LOG_FILE.old"
fi

# --- Prevent concurrent runs ---
if [ -f "$LOCKFILE" ]; then
    LOCK_PID=$(cat "$LOCKFILE" 2>/dev/null)
    if [ -n "$LOCK_PID" ] && kill -0 "$LOCK_PID" 2>/dev/null; then
        exit 0  # Silent exit, another instance running
    else
        rm -f "$LOCKFILE"
    fi
fi
echo $$ > "$LOCKFILE"
trap 'rm -f "$LOCKFILE"' EXIT

# --- Check cooldown (prevent restart loops) ---
if [ -f "$COOLDOWN_FILE" ]; then
    LAST_RESTART=$(cat "$COOLDOWN_FILE" 2>/dev/null)
    NOW=$(date +%s)
    ELAPSED=$((NOW - LAST_RESTART))
    if [ "$ELAPSED" -lt "$COOLDOWN_SECONDS" ]; then
        # Still in cooldown, silent exit
        exit 0
    fi
fi

# --- Health check: Is gateway process running? ---
check_process() {
    # Use ps + grep instead of pgrep (more reliable on macOS)
    ps aux | grep -q "[o]penclaw-gateway"
}

# --- Health check: Is gateway responsive? (session file recently modified) ---
check_responsive() {
    SESSION_FILE="$HOME/.openclaw/agents/main/sessions/sessions.json"
    if [ ! -f "$SESSION_FILE" ]; then
        return 0  # No session file yet, assume OK
    fi
    
    # Check if session file was modified in last STALE_THRESHOLD seconds
    NOW=$(date +%s)
    MTIME=$(stat -f%m "$SESSION_FILE" 2>/dev/null || echo 0)
    AGE=$((NOW - MTIME))
    
    if [ "$AGE" -gt "$STALE_THRESHOLD" ]; then
        return 1  # Stale - gateway might be stuck
    fi
    return 0
}

# --- Combined health check ---
check_health() {
    if ! check_process; then
        return 1  # Process not running
    fi
    # Process running - that's enough for basic health
    # (responsive check can give false positives during idle periods)
    return 0
}

# --- Restart the gateway ---
restart_gateway() {
    log "RESTART: Initiating gateway restart..."

    if [ ! -f "$GATEWAY_PLIST" ]; then
        log "ERROR: Gateway plist not found at $GATEWAY_PLIST"
        return 1
    fi

    # Step 1: Try launchctl kickstart -k (cleanest method)
    log "RESTART: Trying kickstart -k..."
    if launchctl kickstart -k "gui/$(id -u)/$GATEWAY_LABEL" 2>> "$LOG_FILE"; then
        sleep 10
        if check_process; then
            log "RESTART: SUCCESS via kickstart"
            date +%s > "$COOLDOWN_FILE"
            return 0
        fi
    fi

    # Step 2: Fallback - bootout then bootstrap
    log "RESTART: Kickstart failed, trying bootout/bootstrap..."
    launchctl bootout "gui/$(id -u)/$GATEWAY_LABEL" 2>> "$LOG_FILE" || true
    sleep 3

    # Kill any orphaned gateway processes
    ORPHAN_PIDS=$(ps aux | grep "[o]penclaw-gateway" | awk '{print $2}')
    if [ -n "$ORPHAN_PIDS" ]; then
        log "RESTART: Killing orphaned processes: $ORPHAN_PIDS"
        echo "$ORPHAN_PIDS" | xargs kill -9 2>/dev/null
        sleep 2
    fi

    # Bootstrap
    launchctl bootstrap "gui/$(id -u)" "$GATEWAY_PLIST" 2>> "$LOG_FILE"
    sleep 10

    if check_process; then
        log "RESTART: SUCCESS via bootstrap"
        date +%s > "$COOLDOWN_FILE"
        return 0
    else
        log "RESTART: FAILED - manual intervention needed"
        date +%s > "$COOLDOWN_FILE"
        return 1
    fi
}

# =============================================================
# Main watchdog logic
# =============================================================

# Quick health check
if check_health; then
    # Process is running - now check version
    if ! check_version; then
        # Version mismatch - check cooldown
        if [ -f "$VERSION_RESTART_FILE" ]; then
            LAST_VER_RESTART=$(cat "$VERSION_RESTART_FILE" 2>/dev/null)
            NOW=$(date +%s)
            ELAPSED=$((NOW - LAST_VER_RESTART))
            if [ "$ELAPSED" -lt "$VERSION_COOLDOWN" ]; then
                log "VERSION: Mismatch detected but in cooldown (${ELAPSED}s/${VERSION_COOLDOWN}s)"
                touch "$LOG_FILE"
                exit 0
            fi
        fi
        
        log "VERSION: Restarting gateway due to version mismatch..."
        CLI_VERSION=$(openclaw --version 2>/dev/null | head -1)
        
        if restart_gateway; then
            date +%s > "$VERSION_RESTART_FILE"
            notify "🔄 Gateway watchdog restarted due to version mismatch. Now running **$CLI_VERSION**"
            log "VERSION: Restart complete, notification sent"
        fi
        exit 0
    fi
    
    # All good - touch log file so dashboard knows we ran
    touch "$LOG_FILE"
    exit 0
fi

# Health check failed - start retry sequence
log "ALERT: Gateway health check failed (process not found)"

# Retry with delays
ATTEMPT=1
while [ "$ATTEMPT" -le "$MAX_RETRIES" ]; do
    log "RETRY: Attempt $ATTEMPT/$MAX_RETRIES (waiting ${RETRY_DELAY}s)..."
    sleep "$RETRY_DELAY"

    if check_health; then
        log "RECOVERED: Gateway process found on retry $ATTEMPT"
        exit 0
    fi

    ATTEMPT=$((ATTEMPT + 1))
done

# All retries exhausted - restart
log "FAILED: Gateway unresponsive after $MAX_RETRIES retries. Restarting..."
if restart_gateway; then
    notify "🚨 Gateway watchdog restarted OpenClaw — process was unresponsive"
    log "RESTART: Notification sent"
fi
exit $?
