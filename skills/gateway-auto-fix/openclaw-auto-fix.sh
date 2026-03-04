#!/bin/bash
# OpenClaw Gateway Auto-Fix - Main Script
# This runs every minute via cron

LOG_FILE="/tmp/openclaw-auto-fix.log"

echo "=== $(date) ===" >> $LOG_FILE

# Check gateway status
STATUS_OUTPUT=$(openclaw gateway status 2>&1)
echo "$STATUS_OUTPUT" >> $LOG_FILE

# Check if RPC probe failed
if echo "$STATUS_OUTPUT" | grep -q "RPC probe: failed"; then
    echo "RPC probe FAILED! Running auto-fix..." >> $LOG_FILE
    
    # Run openclaw doctor --fix
    echo "Running: openclaw doctor --fix" >> $LOG_FILE
    openclaw doctor --fix 2>&1 >> $LOG_FILE
    
    # Restart gateway
    echo "Running: openclaw gateway restart" >> $LOG_FILE
    openclaw gateway restart 2>&1 >> $LOG_FILE
    
    echo "Auto-fix completed at $(date)" >> $LOG_FILE
    echo "✅ Auto-fix completed!"
else
    echo "Gateway is healthy, no action needed." >> $LOG_FILE
    echo "✅ Gateway is healthy"
fi

echo "---" >> $LOG_FILE
