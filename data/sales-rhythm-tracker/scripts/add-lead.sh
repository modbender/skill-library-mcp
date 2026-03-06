#!/bin/bash
# Sales Rhythm Tracker — Add New Lead
# Usage: add-lead.sh "Name" "Company" "stage" "deal_size" "notes"
# Called by OpenClaw agent when user says "New lead: ..."

SALES_DIR="${HOME}/.openclaw/workspace/sales"
PIPELINE="$SALES_DIR/pipeline.md"
TODAY=$(date +"%Y-%m-%d")

NAME="${1:-Unknown}"
COMPANY="${2:-Unknown Company}"
STAGE="${3:-connected}"
DEAL_SIZE="${4:-TBD}"
NOTES="${5:-First contact. Personality type unknown — determine on next call.}"

if [ ! -f "$PIPELINE" ]; then
  echo "❌ Pipeline not initialized. Run: init-pipeline.sh first"
  exit 1
fi

# Append new lead to pipeline
cat >> "$PIPELINE" << EOF

### ${NAME} @ ${COMPANY}
- **Stage**: ${STAGE}
- **Type**: Unknown — detect on next interaction (look for Tiger/Peacock/Koala/Owl signals)
- **Score**: 45
- **Status**: 🟢 Green
- **Deal Size**: ${DEAL_SIZE}
- **Last Contact**: ${TODAY}
- **Next Action**: Schedule discovery call within 48 hours — prepare 3 open questions about their pain
- **Key Pain**: To be discovered
- **Notes**: ${NOTES}

EOF

echo "✅ Lead added: ${NAME} @ ${COMPANY}"
echo "📌 Stage: ${STAGE}"
echo "📅 Last Contact: ${TODAY}"
echo ""
echo "💡 Next step: Prepare your discovery call using the Four-Step method:"
echo "   1. 挖需求: 'What's the biggest challenge you're dealing with in [their area] right now?'"
echo "   2. 抛产品: Match your solution to their specific answer — not your script"
echo "   3. 解问题: Address the real objection (not the stated one)"
echo "   4. 提成交: Ask for the next concrete commitment"
