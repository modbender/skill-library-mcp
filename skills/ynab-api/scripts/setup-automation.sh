#!/bin/bash
# Setup YNAB automation - creates recommended cron jobs
# Usage: ./setup-automation.sh [--dry-run]

set -e

DRY_RUN=false
if [ "$1" = "--dry-run" ]; then
  DRY_RUN=true
  echo "DRY RUN MODE - No changes will be made"
  echo ""
fi

# Check if openclaw CLI is available
if ! command -v openclaw &> /dev/null; then
  echo "Error: openclaw CLI not found" >&2
  exit 1
fi

# Load config to verify setup
if [ -f ~/.config/ynab/config.json ]; then
  API_KEY=$(jq -r '.api_key' ~/.config/ynab/config.json)
  BUDGET_ID=$(jq -r '.budget_id // "last-used"' ~/.config/ynab/config.json)
elif [ -f /home/node/clawd/config/ynab.json ]; then
  API_KEY=$(jq -r '.api_key' /home/node/clawd/config/ynab.json)
  BUDGET_ID="${YNAB_BUDGET_ID:-last-used}"
else
  echo "Error: YNAB config not found at ~/.config/ynab/config.json or /home/node/clawd/config/ynab.json" >&2
  echo "Please configure your API key first." >&2
  exit 1
fi

if [ "$API_KEY" = "null" ] || [ -z "$API_KEY" ]; then
  echo "Error: YNAB API key not configured" >&2
  exit 1
fi

echo "✅ YNAB configuration found"
echo ""

# Get skill path
SKILL_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "📂 Skill path: $SKILL_PATH"
echo ""

# Get user's WhatsApp number
echo "📱 What's your WhatsApp number? (format: +393760105565)"
read -r WHATSAPP_NUMBER

if [ -z "$WHATSAPP_NUMBER" ]; then
  echo "Error: WhatsApp number required for delivery" >&2
  exit 1
fi

echo ""
echo "🤖 Setting up YNAB automation cron jobs..."
echo ""

# Function to create or skip cron job
create_cron() {
  local name="$1"
  local schedule="$2"
  local task="$3"
  
  if [ "$DRY_RUN" = true ]; then
    echo "  [DRY RUN] Would create: $name"
    echo "    Schedule: $schedule"
    echo "    Task: $task"
    echo ""
    return
  fi
  
  echo "  Creating: $name"
  openclaw cron add \
    --name "$name" \
    --schedule "$schedule" \
    --session isolated \
    --model gemini-flash \
    --delivery announce \
    --channel whatsapp \
    --to "$WHATSAPP_NUMBER" \
    --task "$task" 2>&1 | grep -E "(✓|Error)" || true
  echo ""
}

# 1. Daily Budget Check (7:15 AM)
create_cron \
  "[YNAB] Daily Budget Check" \
  "15 7 * * *" \
  "Run $SKILL_PATH/scripts/daily-budget-check.sh and format output for WhatsApp (single asterisks, no backticks). Add brief butler-style greeting at start."

# 2. Weekly Spending Review (Monday 8:00 AM)
create_cron \
  "[YNAB] Weekly Spending Review" \
  "0 8 * * 1" \
  "Run $SKILL_PATH/scripts/month-comparison.sh to compare current month with previous month. Format for WhatsApp and send with analysis."

# 3. Mid-Month Goal Check (15th at 9:00 AM)
create_cron \
  "[YNAB] Mid-Month Goal Check" \
  "0 9 15 * *" \
  "Run $SKILL_PATH/scripts/goals-progress.sh and send formatted WhatsApp report showing category goal progress."

# 4. Upcoming Bills Alert (Daily 10:00 AM)
create_cron \
  "[YNAB] Upcoming Bills Alert" \
  "0 10 * * *" \
  "Run $SKILL_PATH/scripts/scheduled-upcoming.sh 2 to show scheduled transactions for next 2 days. Only send if there are upcoming transactions."

if [ "$DRY_RUN" = true ]; then
  echo "✅ DRY RUN complete - no changes made"
  echo ""
  echo "Run without --dry-run to actually create cron jobs"
else
  echo "✅ YNAB automation setup complete!"
  echo ""
  echo "📅 Scheduled jobs:"
  echo "  • Daily Budget Check - 7:15 AM every day"
  echo "  • Weekly Spending Review - Monday 8:00 AM"
  echo "  • Mid-Month Goal Check - 15th at 9:00 AM"
  echo "  • Upcoming Bills Alert - 10:00 AM daily (if bills exist)"
  echo ""
  echo "To view your cron jobs: openclaw cron list"
  echo "To disable a job: openclaw cron update --id <job-id> --enabled false"
fi
