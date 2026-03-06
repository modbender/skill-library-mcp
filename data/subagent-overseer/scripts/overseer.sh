#!/usr/bin/env bash
# subagent-overseer — Pull-based sub-agent monitor daemon.
#
# Accumulates process-level and session-level data every INTERVAL seconds.
# Writes a machine-readable status file. The heartbeat handler reads it.
# Zero AI tokens. Zero push notifications. Pure bash + /proc + openclaw CLI.
#
# Usage: overseer.sh [--interval 180] [--workdir /path] [--labels l1,l2,...] [--max-stale 4] [--voice]
# Defaults: interval=180, max-stale=4 (~12min), workdir=cwd

set -euo pipefail

# ── Defaults ──────────────────────────────────────────────────────────────────
INTERVAL=180
WORKDIR="$(pwd)"
LABELS=""
MAX_STALE=4
VOICE=false
STATUS_DIR="/tmp/overseer"
LOGFILE="/tmp/overseer/overseer.log"

# ── Parse args ────────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --interval)  INTERVAL="$2";   shift 2 ;;
        --workdir)   WORKDIR="$2";    shift 2 ;;
        --labels)    LABELS="$2";     shift 2 ;;
        --max-stale) MAX_STALE="$2";  shift 2 ;;
        --voice)     VOICE=true;      shift   ;;
        --help|-h)
            echo "Usage: overseer.sh [--interval SEC] [--workdir DIR] [--labels l1,l2] [--max-stale N] [--voice]"
            exit 0 ;;
        *) echo "Unknown arg: $1" >&2; exit 1 ;;
    esac
done

mkdir -p "$STATUS_DIR"

# ── Locking (one overseer per machine) ────────────────────────────────────────
LOCKFILE="$STATUS_DIR/overseer.lock"
exec 200>"$LOCKFILE"
if ! flock -n 200; then
    echo "Another overseer is already running. Exiting." >&2
    exit 0
fi

log() { echo "$(date -Iseconds) $*" >> "$LOGFILE"; }
log "Started: interval=${INTERVAL}s workdir=$WORKDIR labels=$LABELS max-stale=$MAX_STALE"

# ── Gateway PID detection ─────────────────────────────────────────────────────
find_gateway_pid() {
    pgrep -f "openclaw-gateway" | head -1 || echo ""
}

# ── Process-level health (no AI, no API — pure /proc) ────────────────────────
proc_health() {
    local pid="$1"
    if [[ -z "$pid" || ! -d "/proc/$pid" ]]; then
        echo '{"alive":false}'
        return
    fi
    local cpu mem threads state uptime_sec
    # CPU + MEM from ps
    read -r cpu mem < <(ps -p "$pid" -o %cpu,%mem --no-headers 2>/dev/null || echo "0 0")
    # Thread count from /proc
    threads=$(ls /proc/"$pid"/task 2>/dev/null | wc -l || echo 0)
    # Process state
    state=$(awk '/^State:/ {print $2}' /proc/"$pid"/status 2>/dev/null || echo "?")
    # Uptime
    uptime_sec=$(ps -p "$pid" -o etimes --no-headers 2>/dev/null | tr -d ' ' || echo 0)
    # FD count (proxy for activity)
    local fd_count
    fd_count=$(ls /proc/"$pid"/fd 2>/dev/null | wc -l || echo 0)

    cat <<-EOF
{"alive":true,"cpu":${cpu// /},"mem":${mem// /},"threads":$threads,"state":"$state","uptime_sec":$uptime_sec,"fd_count":$fd_count}
EOF
}

# ── Session-level sub-agent enumeration (one CLI call per cycle) ──────────────
list_subagents() {
    # Returns lines: label|age|model|tokens
    # Filter to recent sessions only (just now, seconds, or minutes — not hours/days)
    openclaw sessions list 2>/dev/null | grep "subag" | \
        grep -E "(just now|[0-9]+s ago|[0-9]+m ago)" | \
        while read -r kind key age model tokens flags; do
            local label="${key##*:}"
            label="${label:0:20}"
            echo "${label}|${age}|${model}|${tokens}"
        done
}

# ── Filesystem diff (cheap: find + stat) ──────────────────────────────────────
MARKER="$STATUS_DIR/fs-marker"
touch "$MARKER"

fs_changes() {
    find "$WORKDIR" -type f \
        -not -path '*/node_modules/*' \
        -not -path '*/.git/objects/*' \
        -not -path '*/dist/*' \
        -newer "$MARKER" \
        2>/dev/null | wc -l
}

fs_recent_files() {
    find "$WORKDIR" -type f \
        -not -path '*/node_modules/*' \
        -not -path '*/.git/objects/*' \
        -not -path '*/dist/*' \
        -newer "$MARKER" \
        2>/dev/null | xargs -I{} basename {} | sort -u | head -5 | tr '\n' ',' | sed 's/,$//'
}

# ── Per-label stale tracking ─────────────────────────────────────────────────
declare -A STALE_COUNTS

get_stale() { echo "${STALE_COUNTS[$1]:-0}"; }
set_stale() { STALE_COUNTS[$1]="$2"; }

# ── Main loop ─────────────────────────────────────────────────────────────────
CYCLE=0
while true; do
    CYCLE=$((CYCLE + 1))
    NOW=$(date -Iseconds)

    # 1. Gateway health
    GW_PID=$(find_gateway_pid)
    GW_HEALTH=$(proc_health "$GW_PID")

    # 2. Active sub-agents
    SUBAGENTS=$(list_subagents)
    SUBAGENT_COUNT=$(echo "$SUBAGENTS" | grep -c . || echo 0)

    # 3. Filesystem activity
    CHANGED=$(fs_changes)
    RECENT=$(fs_recent_files)

    # 4. Per-label staleness
    LABEL_STATUS=""
    if [[ -n "$SUBAGENTS" ]]; then
        while IFS='|' read -r label age model tokens; do
            [[ -z "$label" ]] && continue
            prev_stale=$(get_stale "$label")
            if [[ "$CHANGED" -gt 0 ]]; then
                set_stale "$label" 0
                LABEL_STATUS="${LABEL_STATUS}{\"label\":\"$label\",\"age\":\"$age\",\"stale\":0,\"status\":\"active\"},"
            else
                new_stale=$((prev_stale + 1))
                set_stale "$label" "$new_stale"
                local_status="idle"
                if [[ "$new_stale" -ge "$MAX_STALE" ]]; then
                    local_status="stuck"
                elif [[ "$new_stale" -ge 2 ]]; then
                    local_status="warning"
                fi
                LABEL_STATUS="${LABEL_STATUS}{\"label\":\"$label\",\"age\":\"$age\",\"stale\":$new_stale,\"status\":\"$local_status\"},"
            fi
        done <<< "$SUBAGENTS"
    fi
    # Trim trailing comma
    LABEL_STATUS="${LABEL_STATUS%,}"

    # 5. Write status file (atomic via temp + mv)
    STATUS_FILE="$STATUS_DIR/status.json"
    TMP_STATUS=$(mktemp "$STATUS_DIR/status.XXXXXX")
    cat > "$TMP_STATUS" <<-STATUSEOF
{
  "timestamp": "$NOW",
  "cycle": $CYCLE,
  "interval_sec": $INTERVAL,
  "gateway": { "pid": ${GW_PID:-null}, "health": $GW_HEALTH },
  "subagents": { "count": $SUBAGENT_COUNT, "details": [$LABEL_STATUS] },
  "filesystem": { "changes_since_last": $CHANGED, "recent_files": "$RECENT" },
  "max_stale_threshold": $MAX_STALE
}
STATUSEOF
    mv "$TMP_STATUS" "$STATUS_FILE"

    # 6. Append to rolling log (last 100 entries kept)
    echo "$NOW cycle=$CYCLE agents=$SUBAGENT_COUNT fs_changes=$CHANGED gw_pid=${GW_PID:-none}" >> "$LOGFILE"
    tail -100 "$LOGFILE" > "$LOGFILE.tmp" && mv "$LOGFILE.tmp" "$LOGFILE"

    # 7. Voice summary (optional, local only)
    if [[ "$VOICE" == "true" ]] && command -v jarvis &>/dev/null; then
        if [[ "$SUBAGENT_COUNT" -eq 0 ]]; then
            # No agents — stay silent after first announcement
            if [[ "$CYCLE" -eq 1 ]]; then
                setsid jarvis "No active sub-agents. Overseer watching." &>/dev/null &
            fi
        elif [[ "$CHANGED" -gt 0 ]]; then
            setsid jarvis "$SUBAGENT_COUNT agents active. $CHANGED files changed: $RECENT." &>/dev/null &
        else
            # Check if any stuck
            STUCK_COUNT=$(echo "$LABEL_STATUS" | grep -o '"stuck"' | wc -l || echo 0)
            if [[ "$STUCK_COUNT" -gt 0 ]]; then
                setsid jarvis "Warning: $STUCK_COUNT agents appear stuck. No file changes." &>/dev/null &
            fi
        fi
    fi

    # 8. Reset marker
    touch "$MARKER"

    # 9. Exit if no sub-agents for 2 consecutive cycles
    if [[ "$SUBAGENT_COUNT" -eq 0 ]]; then
        if [[ "${PREV_EMPTY:-0}" -eq 1 ]]; then
            log "No sub-agents for 2 cycles. Exiting."
            break
        fi
        PREV_EMPTY=1
    else
        PREV_EMPTY=0
    fi

    sleep "$INTERVAL"
done

# Cleanup
rm -f "$LOCKFILE" "$MARKER"
log "Overseer stopped after $CYCLE cycles."
