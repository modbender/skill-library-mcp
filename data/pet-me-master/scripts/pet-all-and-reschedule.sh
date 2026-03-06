#!/bin/bash
# Pet all gotchis AND schedule the next reminder cycle
set -e

SKILL_DIR="$HOME/.openclaw/workspace/skills/pet-me-master"

echo "🦞 Petting all gotchis..."
bash "$SKILL_DIR/scripts/pet-all-bankr.sh"

echo ""
echo "📅 Scheduling next reminder cycle..."

# Get the timestamps
TIMESTAMPS=$(bash "$SKILL_DIR/scripts/schedule-next-reminder.sh" | grep "NEXT_.*_ISO=" | tail -2)
REMINDER_ISO=$(echo "$TIMESTAMPS" | grep REMINDER | cut -d= -f2)
FALLBACK_ISO=$(echo "$TIMESTAMPS" | grep FALLBACK | cut -d= -f2)

# Signal to the agent to create the cron jobs
echo "SCHEDULE_REMINDER:$REMINDER_ISO"
echo "SCHEDULE_FALLBACK:$FALLBACK_ISO"

echo ""
echo "✅ Petting complete! Next cycle scheduled."
