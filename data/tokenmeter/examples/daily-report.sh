#!/bin/bash
# daily-report.sh - Daily tokenmeter usage report
# Add to cron: 0 23 * * * ~/clawd/skills/tokenmeter/examples/daily-report.sh

set -e

# tokenmeter is installed in the main repo, not the skill dir
TOKENMETER_DIR="$HOME/clawd/tokenmeter"
cd "$TOKENMETER_DIR"

# Activate virtual environment
source .venv/bin/activate

echo "🪙 tokenmeter Daily Report - $(date '+%Y-%m-%d')"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Import latest sessions
echo "Importing sessions..."
tokenmeter import --auto

# Show today's usage
echo "📊 Today's Usage:"
tokenmeter summary --period day
echo ""

# Show this week
echo "📈 This Week:"
tokenmeter summary --period week
echo ""

# Cost breakdown
echo "💰 Cost Breakdown (This Month):"
tokenmeter costs --period month
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Max plan: \$100/month | Compare to 'Total' above"
