#!/bin/bash
# Setup cron job for Pipedream token refresh
# Usage: ./setup-cron.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REFRESH_SCRIPT="$HOME/clawd/scripts/pipedream-token-refresh.py"
LOG_DIR="$HOME/clawd/logs"

echo "🔌 Pipedream Token Refresh - Cron Setup"
echo "========================================"

# Create directories
mkdir -p "$HOME/clawd/scripts"
mkdir -p "$LOG_DIR"

# Copy refresh script if not in place
if [[ ! -f "$REFRESH_SCRIPT" ]]; then
    cp "$SCRIPT_DIR/pipedream-token-refresh.py" "$REFRESH_SCRIPT"
    chmod +x "$REFRESH_SCRIPT"
    echo "✅ Copied refresh script to $REFRESH_SCRIPT"
else
    echo "ℹ️  Refresh script already exists at $REFRESH_SCRIPT"
fi

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "pipedream-token-refresh"; then
    echo "ℹ️  Cron job already exists"
    crontab -l | grep "pipedream-token-refresh"
else
    # Add cron job (runs every 45 minutes)
    CRON_LINE="*/45 * * * * /usr/bin/python3 $REFRESH_SCRIPT --quiet >> $LOG_DIR/pipedream-cron.log 2>&1"
    (crontab -l 2>/dev/null || echo "") | { cat; echo "$CRON_LINE"; } | crontab -
    echo "✅ Added cron job: runs every 45 minutes"
fi

echo ""
echo "📋 Verification:"
echo "   Script: $REFRESH_SCRIPT"
echo "   Logs:   $LOG_DIR/pipedream-token-refresh.log"
echo ""
echo "🧪 Test manually with:"
echo "   python3 $REFRESH_SCRIPT"
echo ""
echo "📝 View cron jobs with:"
echo "   crontab -l"
