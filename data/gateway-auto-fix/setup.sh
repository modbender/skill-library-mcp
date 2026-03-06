#!/bin/bash
# OpenClaw Gateway Auto-Fix - Self-Installing Script
# Uses OpenClaw cron system instead of system cron

echo "🚀 Installing Gateway Auto-Fix (OpenClaw Cron)..."

SCRIPT_PATH="$HOME/.openclaw-it/workspace/openclaw-auto-fix.sh"
LOG_FILE="/tmp/openclaw-auto-fix.log"

# Create workspace directory
mkdir -p "$HOME/.openclaw-it/workspace"

# Write the main script
cat > "$SCRIPT_PATH" << 'SCRIPT_EOF'
#!/bin/bash
# OpenClaw Gateway Auto-Fix Script
# Monitors gateway status and auto-fixes if RPC probe fails

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
SCRIPT_EOF

# Make executable
chmod +x "$SCRIPT_PATH"

# Add OpenClaw cron job (only if not already added)
if ! openclaw cron list 2>/dev/null | grep -q "gateway-auto-fix"; then
    openclaw cron add \
      --name "gateway-auto-fix" \
      --every "1m" \
      --message "Run: $SCRIPT_PATH" \
      --no-deliver \
      --description "Auto-fix gateway if RPC probe fails"
    echo "✅ OpenClaw cron job added (every 1 minute)"
else
    echo "✅ Cron job already exists"
fi

echo ""
echo "=========================================="
echo "✅ Gateway Auto-Fix Installed!"
echo "=========================================="
echo "Script: $SCRIPT_PATH"
echo "Log: $LOG_FILE"
echo "Cron: OpenClaw cron (every 1 minute)"
echo ""
echo "To check status:"
echo "  openclaw cron list"
echo "  tail -f $LOG_FILE"
echo "=========================================="
