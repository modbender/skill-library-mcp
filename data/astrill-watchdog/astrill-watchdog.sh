#!/usr/bin/env bash
# =============================================================================
# astrill-watchdog.sh — Astrill VPN Watchdog for Ubuntu (deb GUI package)
#
# Monitors tun0 + ping every CHECK_INTERVAL seconds. On failure, attempts
# reconnect via three escalating methods (no sudo required at any point):
#   1. astrill /reconnect  — built-in command (same as post-sleep service)
#   2. pkill asovpnc/asproxy — parent Astrill respawns children automatically
#   3. pkill astrill + relaunch /autostart — full restart, auto-connects to
#      last used server. Root children die with parent; no sudo needed.
#
# Usage: astrill-watchdog.sh {start|stop|status|once}
# Setup: run setup.sh once to install as a systemd user service.
#
# Requirements:
#   - Ubuntu Linux x86_64, Astrill deb GUI package (/usr/local/Astrill/)
#   - Tools: ping, ip, pgrep, pkill (Ubuntu defaults). No sudo.
#   - Active desktop session (DISPLAY/DBUS) for Method 3 relaunch.
# =============================================================================

set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────────────

# Auto-detect Astrill process owner; fall back to current user
ASTRILL_USER="${ASTRILL_USER:-$(pgrep -a -f '/usr/local/Astrill/astrill' 2>/dev/null \
    | awk 'NR==1{print $1}' | xargs -I{} ps -p {} -o user= 2>/dev/null || true)}"
ASTRILL_USER="${ASTRILL_USER:-$(whoami)}"

CHECK_INTERVAL=30       # seconds between health checks
MAX_ATTEMPTS=3          # reconnect attempts per drop event
RECONNECT_WAIT_1=20     # wait after method 1 (/reconnect)
RECONNECT_WAIT_2=20     # wait after method 2 (kill children)
RECONNECT_WAIT_3=45     # wait after method 3 (full restart)
PING_HOST="8.8.8.8"
PING_COUNT=3
LOG_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/astrill-watchdog"
LOG_FILE="$LOG_DIR/watchdog.log"
PID_FILE="$LOG_DIR/watchdog.pid"
ASTRILL_BIN="/usr/local/Astrill/astrill"

# Private log directory and files — dir 700, files 600 (not world-readable)
mkdir -p "$LOG_DIR" && chmod 700 "$LOG_DIR"
touch "$LOG_FILE" "$PID_FILE" && chmod 600 "$LOG_FILE" "$PID_FILE"

DESKTOP_ENV=(
    DISPLAY="${DISPLAY:-:0}"
    DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-unix:path=/run/user/$(id -u)/bus}"
    XDG_SESSION_TYPE="${XDG_SESSION_TYPE:-wayland}"
)

# ── Helpers ───────────────────────────────────────────────────────────────────

log() { printf "[%s] [%s] %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$1" "${*:2}" >> "$LOG_FILE"; }

# Enforce same-user execution — no sudo fallback, no privilege escalation
run_as_astrill() {
    local me; me="$(whoami)"
    if [[ "$me" != "$ASTRILL_USER" ]]; then
        log "ERROR" "User mismatch: running as '$me', Astrill owned by '$ASTRILL_USER'. Aborting."
        return 1
    fi
    "$@"
}

# ── Health checks ─────────────────────────────────────────────────────────────

# ip link show tun0 called once, result reused — avoids duplicate subprocess
tun_up() {
    local state; state="$(ip link show tun0 2>/dev/null)" || return 1
    [[ "$state" =~ state\ (UP|UNKNOWN) ]]
}
internet_ok()     { ping -c "$PING_COUNT" -W 3 "$PING_HOST" &>/dev/null; }
vpn_healthy()     { tun_up && internet_ok; }
astrill_running() { pgrep -u "$ASTRILL_USER" -f '/usr/local/Astrill/astrill' &>/dev/null; }

# ── Reconnect methods ─────────────────────────────────────────────────────────

reconnect_builtin() {
    # Method 1: Astrill's own /reconnect command (undocumented but shipped —
    # same command used by /etc/systemd/system/astrill-reconnect.service)
    log "INFO" "  → Method 1: astrill /reconnect"
    env "${DESKTOP_ENV[@]}" run_as_astrill "$ASTRILL_BIN" /reconnect &>/dev/null &
}

reconnect_kill_child() {
    # Method 2: kill OpenVPN child processes; parent Astrill respawns them
    log "INFO" "  → Method 2: pkill asovpnc/asproxy (parent respawns)"
    pkill -f '/usr/local/Astrill/asovpnc' 2>/dev/null || true
    pkill -f '/usr/local/Astrill/asproxy'  2>/dev/null || true
}

reconnect_full_restart() {
    # Method 3: kill entire Astrill process; relaunch with /autostart argument.
    # /autostart is what the desktop autostart entry uses — Astrill connects
    # to the last used server automatically. Root children (asovpnc, asproxy)
    # die with the parent process, so no sudo is needed.
    log "INFO" "  → Method 3: pkill astrill + relaunch /autostart (wait ${RECONNECT_WAIT_3}s)"
    pkill -u "$ASTRILL_USER" -f '/usr/local/Astrill/astrill' 2>/dev/null || true
    sleep 4
    [[ -x "$ASTRILL_BIN" ]] || { log "ERROR" "Binary missing: $ASTRILL_BIN"; return 1; }
    env "${DESKTOP_ENV[@]}" run_as_astrill nohup "$ASTRILL_BIN" /autostart &>/dev/null &
    disown $! 2>/dev/null || true
    log "INFO" "  Astrill relaunched."
}

reconnect() {
    local attempt wait
    local -a methods=( reconnect_builtin reconnect_kill_child reconnect_full_restart )
    local -a waits=( "$RECONNECT_WAIT_1" "$RECONNECT_WAIT_2" "$RECONNECT_WAIT_3" )
    for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
        log "WARN" "Reconnect attempt $attempt/$MAX_ATTEMPTS"
        "${methods[$((attempt-1))]}"
        wait="${waits[$((attempt-1))]}"
        log "INFO" "Waiting ${wait}s…"; sleep "$wait"
        if vpn_healthy; then log "INFO" "VPN restored (attempt $attempt)."; return 0; fi
        log "WARN" "Still unhealthy after attempt $attempt."
    done
    log "ERROR" "All $MAX_ATTEMPTS attempts exhausted. Will retry next cycle."
    return 1
}

# ── Watch loop ────────────────────────────────────────────────────────────────

watch_loop() {
    echo $$ > "$PID_FILE" && chmod 600 "$PID_FILE"
    log "INFO" "Watchdog started (PID $$, user $ASTRILL_USER, interval ${CHECK_INTERVAL}s)."
    local was_healthy=true
    while true; do
        if vpn_healthy; then
            [[ "$was_healthy" == false ]] && { log "INFO" "VPN healthy again."; was_healthy=true; } \
                || log "DEBUG" "VPN healthy."
        else
            if [[ "$was_healthy" == true ]]; then
                log "WARN" "VPN FAILED. tun0=$(tun_up && echo UP || echo DOWN) ping=$(internet_ok && echo OK || echo FAIL) astrill=$(astrill_running && echo YES || echo NO)"
                was_healthy=false
            fi
            reconnect || true
        fi
        sleep "$CHECK_INTERVAL"
    done
}

# ── Commands ──────────────────────────────────────────────────────────────────

cmd_start() {
    if [[ -f "$PID_FILE" ]]; then
        local old; old="$(cat "$PID_FILE")"
        if kill -0 "$old" 2>/dev/null; then echo "Already running (PID $old)."; exit 0; fi
        rm -f "$PID_FILE"
    fi
    local orphans; orphans="$(pgrep -f 'astrill-watchdog.sh _loop' 2>/dev/null || true)"
    [[ -n "$orphans" ]] && { echo "Killing orphans: $orphans"; echo "$orphans" | xargs kill 2>/dev/null || true; sleep 1; }
    nohup bash "$0" _loop >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "Watchdog started (PID $(cat "$PID_FILE")). Log: $LOG_FILE"
}

cmd_stop() {
    local killed=0
    if [[ -f "$PID_FILE" ]]; then
        local pid; pid="$(cat "$PID_FILE")"
        kill "$pid" 2>/dev/null && { echo "Watchdog (PID $pid) stopped."; killed=1; }
        rm -f "$PID_FILE"
    fi
    local orphans; orphans="$(pgrep -f 'astrill-watchdog.sh _loop' 2>/dev/null || true)"
    if [[ -n "$orphans" ]]; then
        echo "$orphans" | xargs kill 2>/dev/null || true
        echo "Killed orphans: $orphans"; killed=1
    fi
    [[ $killed -eq 0 ]] && echo "No watchdog was running."
}

cmd_status() {
    local tun ping proc health watcher
    tun=$(tun_up      && echo "UP ($(ip addr show tun0 2>/dev/null | awk '/inet /{print $2}'))" || echo "DOWN")
    ping=$(internet_ok && echo "OK" || echo "FAILED")
    proc=$(astrill_running && pgrep -u "$ASTRILL_USER" -f '/usr/local/Astrill/astrill' \
           | xargs -I{} ps -p {} -o pid=,etime= 2>/dev/null | awk '{print "PID "$1" up "$2}' \
           || echo "NOT RUNNING")
    health=$(vpn_healthy && echo "HEALTHY ✓" || echo "DEGRADED ✗")
    local loops; loops="$(pgrep -f 'astrill-watchdog.sh _loop' 2>/dev/null || true)"
    if [[ -n "$loops" ]]; then
        watcher="running (PID $(echo "$loops" | tr '\n' ' '))"
        [[ -f "$PID_FILE" ]] && ! echo "$loops" | grep -q "^$(cat "$PID_FILE")$" \
            && watcher+=" ⚠ PID mismatch — run stop then start"
    else
        watcher="not running"
    fi
    printf "User:     %s\ntun0:     %s\nping:     %s\nastrill:  %s\nstatus:   %s\nwatchdog: %s\nlog:      %s\n" \
        "$ASTRILL_USER" "$tun" "$ping" "$proc" "$health" "$watcher" "$LOG_FILE"
    echo ""; echo "--- last 20 log lines ---"
    tail -n 20 "$LOG_FILE" 2>/dev/null || echo "(no log yet)"
}

cmd_once() {
    vpn_healthy && { log "INFO" "VPN healthy — nothing to do."; } \
               || { log "WARN" "VPN unhealthy — reconnecting."; reconnect || true; }
}

# ── Entrypoint ────────────────────────────────────────────────────────────────

case "${1:-}" in
    start)  cmd_start  ;;
    stop)   cmd_stop   ;;
    status) cmd_status ;;
    once)   cmd_once   ;;
    _loop)  watch_loop ;;
    *) echo "Usage: $0 {start|stop|status|once}"; exit 1 ;;
esac
