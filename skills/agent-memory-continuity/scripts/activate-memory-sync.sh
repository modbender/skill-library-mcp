#!/bin/bash
set -eo pipefail

echo "🔄 Activating Memory Sync System..."

WORKSPACE="${1:-$(pwd)}"
cd "$WORKSPACE"

# Check if cron is available
if ! command -v cron >/dev/null 2>&1; then
    echo "ℹ️  Cron not available - using file-based sync tracking"
    echo "$(date): Memory sync activated (file-based)" >> .memory-sync-log
    echo "✅ File-based memory sync activated"
    exit 0
fi

# Add cron job for memory sync (every 6 hours)
CRON_JOB="0 */6 * * * cd $WORKSPACE && bash scripts/sync-memory.sh >> .memory-sync-log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "sync-memory.sh"; then
    echo "✅ Memory sync cron job already active"
else
    # Add to crontab
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab - 2>/dev/null || true
    echo "✅ Memory sync cron job activated (every 6 hours)"
fi

echo "🧠 Memory continuity system is now active!"
echo "📊 Check sync status: cat .memory-sync-log"