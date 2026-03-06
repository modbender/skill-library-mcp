#!/bin/bash
# Auto-run persona evolution analysis after sessions
# Called by OpenClaw heartbeat or manually

cd /Users/nealme/clawd

# Check if there are new memory files to analyze
LATEST_MEMORY=$(ls -t memory/*.md 2>/dev/null | head -1)
LAST_ANALYZED_FILE=".persona-last-analyzed"

if [ -f "$LAST_ANALYZED_FILE" ]; then
  LAST_ANALYZED=$(cat "$LAST_ANALYZED_FILE")
else
  LAST_ANALYZED=""
fi

# If latest memory is different from last analyzed, run analysis
if [ "$LATEST_MEMORY" != "$LAST_ANALYZED" ]; then
  echo "🔍 Running persona evolution analysis..."
  node --experimental-strip-types skills/persona-evolution/analyze-session.ts 2>/dev/null || true
  echo "$LATEST_MEMORY" > "$LAST_ANALYZED_FILE"
  echo "✅ Persona analysis complete"
else
  echo "⏭️  No new sessions to analyze"
fi

# Check if it's Sunday evening for weekly report
DAY=$(date +%u)
HOUR=$(date +%H)
WEEKLY_REPORT_FILE="PERSONA/evolves/weekly-report-$(date +%Y-%m-%d).md"

if [ "$DAY" = "7" ] && [ "$HOUR" -ge 18 ] && [ ! -f "$WEEKLY_REPORT_FILE" ]; then
  echo "📊 Generating weekly evolution report..."
  node --experimental-strip-types skills/persona-evolution/weekly-report.ts 2>/dev/null || true
  echo "✅ Weekly report generated"
fi
