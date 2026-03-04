#!/bin/bash
# Sales Rhythm Tracker — Log Sales Activity
# Usage: log-activity.sh "Customer" "Company" "activity_type" "summary" "next_step"
# Called by OpenClaw agent when user says "Log: ..."

SALES_DIR="${HOME}/.openclaw/workspace/sales"
ACTIVITY_LOG="$SALES_DIR/activity-log.md"
PIPELINE="$SALES_DIR/pipeline.md"
TODAY=$(date +"%Y-%m-%d")
TIME=$(date +"%H:%M")

CUSTOMER="${1:-Unknown}"
COMPANY="${2:-Unknown}"
ACTIVITY="${3:-call}"
SUMMARY="${4:-No summary provided}"
NEXT_STEP="${5:-Follow up within 3 days}"

if [ ! -f "$ACTIVITY_LOG" ]; then
  echo "❌ Activity log not found. Run: init-pipeline.sh first"
  exit 1
fi

# Append activity to log
cat >> "$ACTIVITY_LOG" << EOF

## ${TODAY} ${TIME} — ${CUSTOMER} @ ${COMPANY}
- **Activity**: ${ACTIVITY}
- **Summary**: ${SUMMARY}
- **Next step**: ${NEXT_STEP}
- **Logged**: $(date)

EOF

echo "✅ Activity logged: ${CUSTOMER} @ ${COMPANY}"
echo "📝 Activity type: ${ACTIVITY}"
echo "📅 Date: ${TODAY} ${TIME}"
echo ""
echo "💡 AGENT INSTRUCTIONS — After logging, please:"
echo "1. Find ${CUSTOMER} @ ${COMPANY} in pipeline.md"
echo "2. Update their Last Contact to ${TODAY}"
echo "3. Update their Next Action to: ${NEXT_STEP}"
echo "4. Reassess their temperature (hotter/same/cooler) based on: ${SUMMARY}"
echo "5. Update Score and Status (🟢/🟡/🔴) accordingly"
echo "6. If stage should advance, update it"
echo "7. If this was a close attempt — record outcome"
echo ""
echo "📞 PHONE CALL REMINDER (if this was a call):"
echo "   • Did the call stay under 6 minutes?"
echo "   • Did you achieve your ONE objective for the call?"
echo "   • Did you ask for a specific next commitment?"
