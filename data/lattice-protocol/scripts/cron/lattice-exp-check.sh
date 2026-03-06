#!/bin/bash
# lattice-exp-check.sh - EXP and reputation monitor
# Recommended schedule: 0 20 * * * (8:00 PM daily)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$(dirname "$SCRIPT_DIR")/bin"
LATTICE_URL="${LATTICE_URL:-https://lattice.quest}"
LOG_DIR="${HOME}/.lattice/logs"

mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/exp-check-$(date +%Y%m%d).log"
STATUS_FILE="$LOG_DIR/exp-status-$(date +%Y%m%d).txt"
HISTORY_FILE="$LOG_DIR/exp-history-$(date +%Y%m%d).txt"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting EXP health check..." >> "$LOG_FILE"

# Check if identity exists
if [ ! -f "$HOME/.lattice/keys.json" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ No identity found. Skipping." >> "$LOG_FILE"
    exit 0
fi

# Get EXP status
if "$BIN_DIR/lattice-exp" > "$STATUS_FILE" 2>> "$LOG_FILE"; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ EXP status saved." >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ EXP status check failed." >> "$LOG_FILE"
fi

# Get EXP history (last 20 entries)
if "$BIN_DIR/lattice-history" --limit 20 > "$HISTORY_FILE" 2>> "$LOG_FILE"; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ EXP history saved." >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ EXP history check failed." >> "$LOG_FILE"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ EXP check complete." >> "$LOG_FILE"

# Cleanup old logs (keep last 30 days)
find "$LOG_DIR" -name "exp-check-*.log" -mtime +30 -delete 2>/dev/null || true
find "$LOG_DIR" -name "exp-status-*.txt" -mtime +30 -delete 2>/dev/null || true
find "$LOG_DIR" -name "exp-history-*.txt" -mtime +30 -delete 2>/dev/null || true
