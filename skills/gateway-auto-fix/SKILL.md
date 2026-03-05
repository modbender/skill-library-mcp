---
name: gateway-auto-fix
description: Automatically monitor OpenClaw gateway status and fix when RPC probe fails. Uses OpenClaw cron system - just install and it works!
---

# Gateway Auto-Fix Skill

## Overview

This skill automatically monitors the OpenClaw gateway and fixes it when the RPC probe fails. It uses OpenClaw's built-in cron system for scheduling.

## What It Does

1. Checks `openclaw gateway status` every minute
2. Detects "RPC probe: failed" in the output
3. Automatically runs:
   - `openclaw doctor --fix` to fix config issues
   - `openclaw gateway restart` to restart the gateway
4. Logs all actions to `/tmp/openclaw-auto-fix.log`

## Quick Install (Automatic)

```bash
npx clawhub install gateway-auto-fix
```

That's it! The skill will:
- ✅ Add OpenClaw cron job (every 1 minute)
- ✅ Create the script
- ✅ Start monitoring

## Manual Install (If ClawHub Not Available)

```bash
# 1. Copy the script to workspace
mkdir -p ~/.openclaw-it/workspace
cp /path/to/gateway-auto-fix/openclaw-auto-fix.sh ~/.openclaw-it/workspace/

# 2. Make executable
chmod +x ~/.openclaw-it/workspace/openclaw-auto-fix.sh

# 3. Add OpenClaw cron job
openclaw cron add \
  --name "gateway-auto-fix" \
  --every "1m" \
  --message "Run: ~/.openclaw-it/workspace/openclaw-auto-fix.sh" \
  --no-deliver
```

## Manual Uninstall

```bash
# Remove cron job
openclaw cron rm gateway-auto-fix

# Remove script
rm ~/.openclaw-it/workspace/openclaw-auto-fix.sh
```

## Usage

### Check Cron Status
```bash
openclaw cron list
openclaw cron status
```

### Check Logs
```bash
tail -f /tmp/openclaw-auto-fix.log
```

### Run Manually
```bash
~/.openclaw-it/workspace/openclaw-auto-fix.sh

# Or via OpenClaw cron
openclaw cron run gateway-auto-fix
```

## Troubleshooting

### Check if cron is running:
```bash
openclaw cron status
```

### Check gateway:
```bash
openclaw gateway status
```

### Run manually:
```bash
openclaw cron run gateway-auto-fix
```

## Files Created

- Script: `~/.openclaw-it/workspace/openclaw-auto-fix.sh`
- Log: `/tmp/openclaw-auto-fix.log`
- Cron: OpenClaw built-in (every 1 minute)

## Configuration

### Change Interval

```bash
# Remove old job
openclaw cron rm gateway-auto-fix

# Add new job with different interval (e.g., 5 minutes)
openclaw cron add \
  --name "gateway-auto-fix" \
  --every "5m" \
  --message "Run: ~/.openclaw-it/workspace/openclaw-auto-fix.sh" \
  --no-deliver
```

## Complete Manual Setup Commands

```bash
# Step 1: Create workspace
mkdir -p ~/.openclaw-it/workspace

# Step 2: Create the script
cat > ~/.openclaw-it/workspace/openclaw-auto-fix.sh << 'EOF'
#!/bin/bash
LOG_FILE="/tmp/openclaw-auto-fix.log"
echo "=== $(date) ===" >> $LOG_FILE
STATUS_OUTPUT=$(openclaw gateway status 2>&1)
echo "$STATUS_OUTPUT" >> $LOG_FILE
if echo "$STATUS_OUTPUT" | grep -q "RPC probe: failed"; then
    echo "RPC probe FAILED! Running auto-fix..." >> $LOG_FILE
    openclaw doctor --fix 2>&1 >> $LOG_FILE
    openclaw gateway restart 2>&1 >> $LOG_FILE
    echo "Auto-fix completed at $(date)" >> $LOG_FILE
else
    echo "Gateway is healthy" >> $LOG_FILE
fi
echo "---" >> $LOG_FILE
EOF

# Step 3: Make executable
chmod +x ~/.openclaw-it/workspace/openclaw-auto-fix.sh

# Step 4: Add OpenClaw cron job
openclaw cron add \
  --name "gateway-auto-fix" \
  --every "1m" \
  --message "Run: ~/.openclaw-it/workspace/openclaw-auto-fix.sh" \
  --no-deliver

# Step 5: Verify
openclaw cron list
```
