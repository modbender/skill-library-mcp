#!/bin/bash
# Check for pending reminder and trigger immediate send
# Runs every 2 minutes via cron

IMMEDIATE_FILE="$HOME/.openclaw/workspace/.pet-reminder-immediate.txt"
HEARTBEAT_FILE="$HOME/.openclaw/workspace/.gotchi-reminder.txt"

if [ -f "$IMMEDIATE_FILE" ]; then
  # Copy to heartbeat file (will be picked up within 2 min)
  cp "$IMMEDIATE_FILE" "$HEARTBEAT_FILE"
  
  # Remove immediate file
  rm -f "$IMMEDIATE_FILE"
  
  echo "[$(date)] ✅ Reminder moved to heartbeat queue"
fi
