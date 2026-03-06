#!/bin/bash
# Human-readable Claude Code usage report

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run check (it writes to cache automatically)
"$SCRIPT_DIR/check-usage.sh" > /dev/null || {
  echo "❌ Failed to check usage" >&2
  exit 1
}

# Parse results from cache
SESSION=$(grep "^SESSION=" /tmp/claude-usage.cache | cut -d= -f2)
WEEKLY=$(grep "^WEEKLY=" /tmp/claude-usage.cache | cut -d= -f2)
BURN_RATE=$(grep "^BURN_RATE=" /tmp/claude-usage.cache | cut -d= -f2)

SESSION_INT=$(printf "%.0f" "$SESSION")
WEEKLY_INT=$(printf "%.0f" "$WEEKLY")

# Burn rate interpretation
case "$BURN_RATE" in
  UNDER)
    BURN_MSG="🟢 Under-using — you can use more to maximize your subscription value!"
    ;;
  OVER)
    BURN_MSG="🔴 Over-using — burn rate exceeds daily budget (~14%/day)"
    ;;
  OK)
    BURN_MSG="⚪ On pace — optimal usage"
    ;;
  *)
    BURN_MSG=""
    ;;
esac

# Session alert
if grep -q "ALERT_SESSION=1" /tmp/claude-usage.cache 2>/dev/null; then
  echo "🟡 WARNING: Session usage > 50% ($SESSION_INT%)"
  echo ""
fi

# Report
echo "📊 Claude Code Daily Check:"
echo ""
echo "⏱️  SESSION (5h): $SESSION_INT%"
echo "📅 WEEKLY (7d): $WEEKLY_INT%"
echo ""
if [ -n "$BURN_MSG" ]; then
  echo "$BURN_MSG"
fi
