#!/usr/bin/env bash
# install_cron.sh — Install/remove the supermemory-free auto-capture cron job.
#
# Usage:
#   bash install_cron.sh           # Install (daily at 2:00 AM UTC)
#   bash install_cron.sh --remove  # Remove the cron job

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(realpath "$SKILL_DIR/../..")"
PYTHON="${PYTHON:-python3}"
LOG_FILE="$WORKSPACE_DIR/logs/supermemory-auto-capture.log"
CRON_MARKER="supermemory-free-auto-capture"

# Cron schedule: 2:00 AM UTC daily
CRON_SCHEDULE="0 2 * * *"
CRON_CMD="$CRON_SCHEDULE cd $WORKSPACE_DIR && source .env && $PYTHON $SKILL_DIR/auto_capture.py --days 3 >> $LOG_FILE 2>&1 # $CRON_MARKER"

# ── Colors ──────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()    { echo -e "${GREEN}✅${NC} $*"; }
warn()    { echo -e "${YELLOW}⚠️ ${NC} $*"; }
error()   { echo -e "${RED}❌${NC} $*" >&2; }

# ── Check Python ─────────────────────────────────────────────────────────────
check_python() {
    if ! command -v "$PYTHON" &>/dev/null; then
        error "python3 not found. Install it or set PYTHON env var."
        exit 1
    fi
    info "Python: $($PYTHON --version)"
}

# ── Check API key ─────────────────────────────────────────────────────────────
check_api_key() {
    if grep -q "SUPERMEMORY_OPENCLAW_API_KEY" "$WORKSPACE_DIR/.env" 2>/dev/null; then
        info "API key found in .env"
    elif [[ -n "${SUPERMEMORY_OPENCLAW_API_KEY:-}" ]]; then
        info "API key found in environment"
    else
        warn "SUPERMEMORY_OPENCLAW_API_KEY not found — cron will fail without it."
        warn "Add it to $WORKSPACE_DIR/.env"
    fi
}

# ── Install ───────────────────────────────────────────────────────────────────
install_cron() {
    check_python
    check_api_key

    # Create log dir
    mkdir -p "$(dirname "$LOG_FILE")"

    # Remove existing entry (if any)
    crontab -l 2>/dev/null | grep -v "$CRON_MARKER" | crontab - || true

    # Add new entry
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -

    info "Cron job installed: $CRON_SCHEDULE (daily at 2:00 AM UTC)"
    echo ""
    echo "  Command: $PYTHON $SKILL_DIR/auto_capture.py --days 3"
    echo "  Log:     $LOG_FILE"
    echo ""
    echo "Verify with: crontab -l | grep $CRON_MARKER"
    echo ""
    echo "Test run (dry):  $PYTHON $SKILL_DIR/auto_capture.py --dry-run"
    echo "Test run (live): $PYTHON $SKILL_DIR/auto_capture.py"
}

# ── Remove ────────────────────────────────────────────────────────────────────
remove_cron() {
    if crontab -l 2>/dev/null | grep -q "$CRON_MARKER"; then
        crontab -l 2>/dev/null | grep -v "$CRON_MARKER" | crontab -
        info "Cron job removed."
    else
        warn "No cron job found with marker: $CRON_MARKER"
    fi
}

# ── Status ────────────────────────────────────────────────────────────────────
show_status() {
    echo "--- supermemory-free auto-capture status ---"
    echo ""
    if crontab -l 2>/dev/null | grep -q "$CRON_MARKER"; then
        info "Cron job is INSTALLED"
        echo ""
        crontab -l | grep "$CRON_MARKER"
    else
        warn "Cron job is NOT installed"
    fi
    echo ""
    if [[ -f "$LOG_FILE" ]]; then
        echo "Last 10 log lines ($LOG_FILE):"
        tail -10 "$LOG_FILE"
    else
        echo "No log file yet: $LOG_FILE"
    fi
}

# ── Entry point ───────────────────────────────────────────────────────────────
case "${1:-install}" in
    --remove|remove|uninstall)
        remove_cron
        ;;
    --status|status)
        show_status
        ;;
    --install|install|"")
        install_cron
        ;;
    *)
        echo "Usage: $0 [--install|--remove|--status]"
        exit 1
        ;;
esac
