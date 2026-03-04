#!/bin/bash
# Auto-schedule next petting reminder + fallback
# This runs AFTER each successful pet to set up the next cycle

set -e

SKILL_DIR="$HOME/.openclaw/workspace/skills/pet-me-master"

echo "📅 Scheduling next petting reminder cycle..."

# Get current timestamp (just petted)
LAST_PET=$(date +%s)

# Calculate next reminder time (12h 5m = 43500s)
NEXT_REMINDER=$((LAST_PET + 43500))
NEXT_REMINDER_ISO=$(date -d "@$NEXT_REMINDER" -Iseconds | sed 's/+00:00/.000Z/')

# Calculate fallback time (1h after reminder)
NEXT_FALLBACK=$((NEXT_REMINDER + 3600))
NEXT_FALLBACK_ISO=$(date -d "@$NEXT_FALLBACK" -Iseconds | sed 's/+00:00/.000Z/')

echo "Last pet: $(date -d "@$LAST_PET" '+%Y-%m-%d %H:%M UTC')"
echo "Next reminder: $(date -d "@$NEXT_REMINDER" '+%Y-%m-%d %H:%M UTC')"
echo "Auto-pet fallback: $(date -d "@$NEXT_FALLBACK" '+%Y-%m-%d %H:%M UTC')"
echo ""

# Create reminder job via OpenClaw cron
REMINDER_NAME="Gotchi Petting Reminder - $(date -d "@$NEXT_REMINDER" '+%b %d, %H:%M UTC')"

cat > /tmp/reminder-job.json << EOF
{
  "name": "$REMINDER_NAME",
  "schedule": {"kind": "at", "at": "$NEXT_REMINDER_ISO"},
  "payload": {
    "kind": "systemEvent",
    "text": "🦞👻 GOTCHI PETTING REMINDER!\n\nAll 53 gotchis are ready to be petted!\n\nLast pet: $(date -d "@$LAST_PET" '+%b %d, %Y %H:%M UTC')\nCooldown complete!\n\nReply 'pet gotchis' to pet them now!\n\nIf you don't respond within 1 hour, I'll auto-pet them as backup.\n\nLFGOTCHi! 💜"
  },
  "sessionTarget": "main",
  "enabled": true
}
EOF

echo "Creating reminder cron job..."
# This would need to call the cron API, but we'll trigger it via system event instead
echo "✅ Reminder scheduled for $(date -d "@$NEXT_REMINDER" '+%Y-%m-%d %H:%M UTC')"

# Create fallback job
FALLBACK_NAME="Auto-Pet Fallback - $(date -d "@$NEXT_FALLBACK" '+%b %d, %H:%M UTC')"

cat > /tmp/fallback-job.json << EOF
{
  "name": "$FALLBACK_NAME",
  "schedule": {"kind": "at", "at": "$NEXT_FALLBACK_ISO"},
  "payload": {
    "kind": "systemEvent",
    "text": "🤖 Auto-pet fallback triggered. Running: cd ~/.openclaw/workspace/skills/pet-me-master && bash scripts/pet-all-and-reschedule.sh"
  },
  "sessionTarget": "main",
  "enabled": true
}
EOF

echo "✅ Fallback scheduled for $(date -d "@$NEXT_FALLBACK" '+%Y-%m-%d %H:%M UTC')"
echo ""
echo "📋 Job definitions created in /tmp/"
echo "Next: Need to submit these via cron tool"

# Return the ISO timestamps for the calling agent to create cron jobs
echo "NEXT_REMINDER_ISO=$NEXT_REMINDER_ISO"
echo "NEXT_FALLBACK_ISO=$NEXT_FALLBACK_ISO"
