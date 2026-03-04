#!/usr/bin/env bash
# OpenClaw Failover Health Monitor
# Pings primary gateway every CHECK_INTERVAL seconds.
# After FAIL_THRESHOLD consecutive failures, promotes this node.
# Auto-demotes when primary recovers.
#
# Usage: Install as systemd service on your standby node.
# Configure the variables below for your setup.

# === CONFIGURE THESE ===
PRIMARY_IP="${PRIMARY_IP:-100.99.118.75}"       # Primary gateway Tailscale/LAN IP
PRIMARY_PORT="${PRIMARY_PORT:-18789}"            # Primary gateway port
FAIL_THRESHOLD="${FAIL_THRESHOLD:-3}"           # Failures before promotion
CHECK_INTERVAL="${CHECK_INTERVAL:-10}"          # Seconds between checks
WORKSPACE="${WORKSPACE:-/home/openclaw/.openclaw/workspace}"
SECRETS_HOST="${SECRETS_HOST:-}"                # e.g., "ember@100.120.142.74" (optional)
OPENCLAW_USER="${OPENCLAW_USER:-openclaw}"
# === END CONFIG ===

FAIL_COUNT=0
PROMOTED=false
LOG_TAG="openclaw-health"

log() { logger -t "$LOG_TAG" "$1"; echo "$(date -Is) $1"; }

check_primary() {
    curl -sf -o /dev/null --connect-timeout 5 \
        "http://${PRIMARY_IP}:${PRIMARY_PORT}/health" 2>/dev/null
}

promote() {
    log "PROMOTING: Primary unreachable after ${FAIL_THRESHOLD} checks. Starting failover gateway."

    # Pull latest workspace from git (best effort)
    if [ -d "$WORKSPACE/.git" ]; then
        cd "$WORKSPACE"
        sudo -u "$OPENCLAW_USER" git pull --ff-only 2>&1 | logger -t "$LOG_TAG" \
            || log "WARNING: git pull failed, using last sync"
    fi

    # Sync secrets from remote host (optional, best effort)
    if [ -n "$SECRETS_HOST" ]; then
        sudo -u "$OPENCLAW_USER" rsync -a "${SECRETS_HOST}:~/.secrets/" \
            "/home/${OPENCLAW_USER}/.secrets/" 2>&1 | logger -t "$LOG_TAG" \
            || log "WARNING: secrets sync failed, using cached"
    fi

    # Start OpenClaw
    systemctl start openclaw
    sleep 5

    if systemctl is-active --quiet openclaw; then
        log "PROMOTED: Failover gateway is ACTIVE."
        PROMOTED=true
    else
        log "ERROR: Failed to start openclaw service after promotion"
    fi
}

demote() {
    log "DEMOTING: Primary is back. Stopping failover gateway."
    systemctl stop openclaw
    PROMOTED=false
    FAIL_COUNT=0
    log "DEMOTED: Failover gateway stopped. Primary has recovered."
}

log "Health monitor starting. Watching primary at ${PRIMARY_IP}:${PRIMARY_PORT}"

while true; do
    if check_primary; then
        if [ "$PROMOTED" = true ]; then
            demote
        fi
        FAIL_COUNT=0
    else
        if [ "$PROMOTED" = false ]; then
            FAIL_COUNT=$((FAIL_COUNT + 1))
            log "Primary check FAILED (${FAIL_COUNT}/${FAIL_THRESHOLD})"
            if [ "$FAIL_COUNT" -ge "$FAIL_THRESHOLD" ]; then
                promote
            fi
        fi
    fi
    sleep "$CHECK_INTERVAL"
done
