#!/bin/bash
# Helper script to display cron setup commands based on schedule.json
# The agent reads this and uses the cron tool to set up jobs

SCHEDULE_FILE="$HOME/.openclaw/workspace/skills/x-monitor/config/schedule.json"

if [ ! -f "$SCHEDULE_FILE" ]; then
    echo "Error: Schedule file not found at $SCHEDULE_FILE"
    exit 1
fi

# Read schedule config
TIMEZONE=$(jq -r '.timezone // "America/Los_Angeles"' "$SCHEDULE_FILE")
ENABLED=$(jq -r '.enabled // true' "$SCHEDULE_FILE")

if [ "$ENABLED" != "true" ]; then
    echo "X Monitor schedule is disabled in config"
    exit 0
fi

echo "X Monitor Schedule Configuration:"
echo "  Timezone: $TIMEZONE"
echo "  Check times:"

# Read check times and output cron expressions
jq -r '.check_times[]' "$SCHEDULE_FILE" | while read TIME; do
    HOUR=$(echo "$TIME" | cut -d: -f1 | sed 's/^0//')
    MINUTE=$(echo "$TIME" | cut -d: -f2)
    echo "    - $TIME → cron: $MINUTE $HOUR * * * (tz: $TIMEZONE)"
done

echo ""
echo "Use the cron tool to create jobs with these schedules."
