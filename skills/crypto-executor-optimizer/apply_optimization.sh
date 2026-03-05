#!/bin/bash

#########################################################
# APPLY OPTIMIZATION — crypto-executor-optimizer
# Called by Wesley after he decides what to change.
# Wesley passes the new values as arguments.
# This script: backup → modify → validate → restart → notify
#
# Author: Georges Andronescu (Wesley Armando)
# Version: 2.0.1
# Fix: Strategy mix regex now accepts both single AND double quotes
#########################################################

EXECUTOR_PATH="/workspace/skills/crypto-executor/executor.py"
BACKUP_DIR="/workspace/skills/crypto-executor"
LOG_FILE="/workspace/logs/auto_optimize.log"
ANALYSIS_LOG="/workspace/logs/wesley_optimizations.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
TIMESTAMP_FILE=$(date '+%Y%m%d_%H%M%S')

mkdir -p /workspace/logs

log() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

# ── Parse arguments ───────────────────────────────────────────────────────────

OBI_SCALPING=""
OBI_MOMENTUM=""
PRICE_CHANGE=""
SPREAD_BPS=""
KELLY_FACTOR=""
MIX_SCALPING=""
MIX_MOMENTUM=""
MIX_STAT_ARB=""
REASON=""
NO_CHANGES=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --obi-scalping)   OBI_SCALPING="$2";  shift 2 ;;
        --obi-momentum)   OBI_MOMENTUM="$2";  shift 2 ;;
        --price-change)   PRICE_CHANGE="$2";  shift 2 ;;
        --spread-bps)     SPREAD_BPS="$2";    shift 2 ;;
        --kelly-factor)   KELLY_FACTOR="$2";  shift 2 ;;
        --mix-scalping)   MIX_SCALPING="$2";  shift 2 ;;
        --mix-momentum)   MIX_MOMENTUM="$2";  shift 2 ;;
        --mix-stat-arb)   MIX_STAT_ARB="$2";  shift 2 ;;
        --reason)         REASON="$2";        shift 2 ;;
        --no-changes)     NO_CHANGES=true;    shift ;;
        *) shift ;;
    esac
done

log "========================================"
log "APPLY OPTIMIZATION — $(date '+%Y-%m-%d %H:%M:%S')"
log "Reason: $REASON"
log "========================================"

# ── No changes case ───────────────────────────────────────────────────────────

if [ "$NO_CHANGES" = true ]; then
    log "✅ No changes needed. $REASON"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] NO CHANGES — $REASON" >> "$ANALYSIS_LOG"
    exit 0
fi

# ── Pre-flight ────────────────────────────────────────────────────────────────

if [ ! -f "$EXECUTOR_PATH" ]; then
    log "ERROR: executor.py not found at $EXECUTOR_PATH"
    exit 1
fi

# ── Backup ────────────────────────────────────────────────────────────────────

BACKUP_PATH="$BACKUP_DIR/executor_backup_$TIMESTAMP_FILE.py"
cp "$EXECUTOR_PATH" "$BACKUP_PATH"
log "Backup created: $BACKUP_PATH"

# ── Apply changes with Python ─────────────────────────────────────────────────

python3 << PYEOF
import re
import sys

path = "$EXECUTOR_PATH"
with open(path) as f:
    code = f.read()

original = code
changes = []

def replace_val(code, pattern, new_val, label):
    """Replace first capture group with new_val."""
    def repl(m):
        return m.group(0).replace(m.group(1), new_val)
    new_code, n = re.subn(pattern, repl, code, count=1)
    if n > 0:
        changes.append(f"{label}: → {new_val}")
    return new_code

# OBI scalping threshold:  obi > 0.10 and spread_bps
if "$OBI_SCALPING":
    code = replace_val(code,
        r'if obi > ([\d.]+) and spread_bps',
        "$OBI_SCALPING",
        "OBI scalping")

# OBI momentum threshold:  obi > 0.12 and price_change
if "$OBI_MOMENTUM":
    code = replace_val(code,
        r'if obi > ([\d.]+) and price_change',
        "$OBI_MOMENTUM",
        "OBI momentum")

# price_change threshold:  price_change > 0.8
if "$PRICE_CHANGE":
    code = replace_val(code,
        r'price_change > ([\d.]+)',
        "$PRICE_CHANGE",
        "price_change trigger")

# spread_bps threshold:  spread_bps < 8
if "$SPREAD_BPS":
    code = replace_val(code,
        r'spread_bps < ([\d.]+)',
        "$SPREAD_BPS",
        "spread_bps filter")

# Kelly factor:  kelly * 0.5
if "$KELLY_FACTOR":
    code = replace_val(code,
        r'kelly \* ([\d.]+)',
        "$KELLY_FACTOR",
        "Kelly factor")

# FIX v2.0.1: Strategy mix — accept BOTH single AND double quotes
# executor.py uses double quotes: "scalping": 0.70
if "$MIX_SCALPING":
    code = replace_val(code,
        r'["\']scalping["\']:\s*([\d.]+)',
        "$MIX_SCALPING",
        "mix scalping")

if "$MIX_MOMENTUM":
    code = replace_val(code,
        r'["\']momentum["\']:\s*([\d.]+)',
        "$MIX_MOMENTUM",
        "mix momentum")

if "$MIX_STAT_ARB":
    code = replace_val(code,
        r'["\']stat_arb["\']:\s*([\d.]+)',
        "$MIX_STAT_ARB",
        "mix stat_arb")

if code == original:
    print("WARNING: No patterns matched in executor.py")
    sys.exit(2)

with open(path, 'w') as f:
    f.write(code)

print("CHANGES_APPLIED:" + "|".join(changes))
PYEOF

PYTHON_EXIT=$?

if [ $PYTHON_EXIT -eq 2 ]; then
    log "WARNING: No patterns matched. Restoring backup."
    cp "$BACKUP_PATH" "$EXECUTOR_PATH"
    exit 1
elif [ $PYTHON_EXIT -ne 0 ]; then
    log "ERROR: Python modification failed. Restoring backup."
    cp "$BACKUP_PATH" "$EXECUTOR_PATH"
    exit 1
fi

log "executor.py modified"

# ── Validate syntax ───────────────────────────────────────────────────────────

VALIDATE_OUTPUT=$(python3 -m py_compile "$EXECUTOR_PATH" 2>&1)
if [ $? -ne 0 ]; then
    log "ERROR: Syntax validation failed: $VALIDATE_OUTPUT"
    log "Restoring backup..."
    cp "$BACKUP_PATH" "$EXECUTOR_PATH"
    log "Backup restored. Original executor.py preserved."

    # Telegram alert
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
        MSG="⚠️ Wesley Optimizer: syntax error in generated code. Original restored.%0AReason: $REASON"
        curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d "chat_id=$TELEGRAM_CHAT_ID&text=$MSG" > /dev/null
    fi
    exit 1
fi

log "✅ Syntax validation passed"

# ── Restart bot ───────────────────────────────────────────────────────────────

# Try systemd
sudo systemctl restart crypto-executor 2>/dev/null
if systemctl is-active --quiet crypto-executor 2>/dev/null; then
    log "✅ Bot restarted via systemd"
    RESTART_OK=true
else
    # Fallback: pkill + nohup
    log "systemd unavailable, using pkill fallback..."
    pkill -f "executor.py" 2>/dev/null
    sleep 3
    if [ -f "/workspace/data/bot_config.env" ]; then
        source /workspace/data/bot_config.env
    fi
    nohup python3 "$EXECUTOR_PATH" >> /workspace/logs/binance_bot.log 2>&1 &
    sleep 3
    if pgrep -f "executor.py" > /dev/null; then
        log "✅ Bot restarted via pkill fallback"
        RESTART_OK=true
    else
        log "❌ Bot failed to restart"
        RESTART_OK=false
    fi
fi

# ── Cleanup old backups (keep last 5) ────────────────────────────────────────

BACKUP_COUNT=$(ls "$BACKUP_DIR"/executor_backup_*.py 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt 5 ]; then
    ls -t "$BACKUP_DIR"/executor_backup_*.py | tail -n +6 | xargs rm -f
    log "Old backups cleaned (kept last 5)"
fi

# ── Log to analysis log ───────────────────────────────────────────────────────

{
    echo ""
    echo "========================================"
    echo "[$TIMESTAMP]"
    echo "Reason: $REASON"
    echo "Restart: $RESTART_OK"
    echo "========================================"
} >> "$ANALYSIS_LOG"

# ── Telegram success alert ────────────────────────────────────────────────────

if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
    RESTART_STATUS="✅ Bot restarted"
    [ "$RESTART_OK" = false ] && RESTART_STATUS="⚠️ Restart failed"
    MSG="🤖 Wesley Optimization Applied%0AReason: $REASON%0A$RESTART_STATUS"
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
        -d "chat_id=$TELEGRAM_CHAT_ID&text=$MSG" > /dev/null
fi

log "========================================"
log "OPTIMIZATION COMPLETE ✅"
log "========================================"
