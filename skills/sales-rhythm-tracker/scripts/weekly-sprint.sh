#!/bin/bash
# Sales Rhythm Tracker — Weekly Sprint Planner
# Generates a full weekly plan using the Three-Step Sprint Cycle
# Best run every Monday morning

SALES_DIR="${HOME}/.openclaw/workspace/sales"
PIPELINE="$SALES_DIR/pipeline.md"
SPRINT_FILE="$SALES_DIR/weekly-sprint.md"
TODAY=$(date +"%Y-%m-%d")
WEEK_NUM=$(date +"%V")

# Determine sprint phase
DAY_OF_MONTH=$(date +"%d")
if [ "$DAY_OF_MONTH" -le 7 ]; then
  SPRINT_WEEK=1; PHASE="SEED (播种)"; PHASE_GOAL="Maximize volume. Build a full pipeline for the month."
elif [ "$DAY_OF_MONTH" -le 14 ]; then
  SPRINT_WEEK=2; PHASE="FLIP (翻牌)"; PHASE_GOAL="Qualify hard. Keep the top 30%. Release the rest."
elif [ "$DAY_OF_MONTH" -le 21 ]; then
  SPRINT_WEEK=3; PHASE="HARVEST (采果)"; PHASE_GOAL="Close sprint. Every lead needs a YES or NO by Friday."
else
  SPRINT_WEEK=4; PHASE="RESET (机动)"; PHASE_GOAL="Onboard wins, collect payment, plan next month."
fi

echo "============================================"
echo "🗓 WEEKLY SPRINT PLANNER"
echo "Week $WEEK_NUM | Sprint Week $SPRINT_WEEK | $TODAY"
echo "Phase: $PHASE"
echo "Goal: $PHASE_GOAL"
echo "============================================"
echo ""
echo "📋 CURRENT PIPELINE:"
cat "$PIPELINE"
echo ""
echo "---"
echo ""
echo "💡 AGENT INSTRUCTIONS — Generate this week's sprint plan:"
echo ""
echo "Based on the pipeline above and the current phase ($PHASE), create:"
echo ""
echo "1. WEEK OBJECTIVE"
echo "   One sentence capturing what winning this week looks like."
echo ""
echo "2. DAILY ACTION PLAN (Monday-Friday)"
echo "   For each day, list:"
echo "   - Primary focus (which leads to advance)"
echo "   - New outreach targets (how many, what sector/profile)"
echo "   - Specific commitments to get from key leads"
echo ""
echo "3. CLOSE TARGETS THIS WEEK"
echo "   List all leads in 'closing' or 'negotiation' stage."
echo "   For each: name, stage, customer type, and the exact closing approach to use."
echo "   (Match approach to Tiger/Peacock/Koala/Owl type)"
echo ""
echo "4. FLIP CANDIDATES"
echo "   Leads that need a YES or NO decision this week."
echo "   These are wasting space in the pipeline if not resolved."
echo ""
echo "5. SEED TARGETS"
echo "   Profile of the 4+ new contacts to reach each day."
echo "   What sector? What pain point? What opening line?"
echo ""
echo "6. FRIDAY SUCCESS CRITERIA"
echo "   Exactly 3-4 measurable outcomes that define a successful week."
echo "   (Examples: 2 deals advanced to next stage, 1 close, 20 new contacts seeded)"
echo ""
echo "7. WEEKLY MANTRA"
echo "   One motivating principle from the Iron Army for this week's phase."
echo ""
echo "Write the plan to: $SPRINT_FILE"
echo "Format clearly with day headers and bullet points."
