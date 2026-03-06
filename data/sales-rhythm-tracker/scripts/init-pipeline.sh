#!/bin/bash
# Sales Rhythm Tracker — Initialize Pipeline Workspace
# Run once to set up your local CRM files

SALES_DIR="${HOME}/.openclaw/workspace/sales"

echo "🚀 Initializing Sales Rhythm Tracker workspace..."

mkdir -p "$SALES_DIR"

# Create pipeline.md if it doesn't exist
if [ ! -f "$SALES_DIR/pipeline.md" ]; then
cat > "$SALES_DIR/pipeline.md" << 'EOF'
# Sales Pipeline
> Managed by Sales Rhythm Tracker | Alibaba Iron Army Methodology

---

## Active Leads

<!-- Each lead follows this format:

### [Lead Name] @ [Company]
- **Stage**: [prospect/connected/qualified/presented/proposal/negotiation/closing]
- **Type**: [Tiger/Peacock/Koala/Owl/Unknown]
- **Score**: [0-100]
- **Status**: [🟢 Green / 🟡 Yellow / 🔴 Red]
- **Deal Size**: [estimated value]
- **Last Contact**: [YYYY-MM-DD]
- **Next Action**: [what to do + by when]
- **Key Pain**: [their main problem you're solving]
- **Notes**: [context, objections, anything relevant]

-->

EOF
echo "✅ Created pipeline.md"
fi

# Create activity-log.md if it doesn't exist
if [ ! -f "$SALES_DIR/activity-log.md" ]; then
cat > "$SALES_DIR/activity-log.md" << 'EOF'
# Sales Activity Log
> Every interaction matters. Log it within 10 minutes.

---

<!-- Format:
## [YYYY-MM-DD] — [Customer Name] @ [Company]
- **Activity**: [call/email/meeting/demo/proposal/other]
- **Duration**: [X min]
- **What happened**: [brief summary]
- **Customer reaction**: [positive/neutral/negative/no response]
- **Objections raised**: [none / list them]
- **Next step**: [specific action + date]
- **Temperature**: [hotter/same/cooler]
-->

EOF
echo "✅ Created activity-log.md"
fi

# Create weekly-sprint.md
if [ ! -f "$SALES_DIR/weekly-sprint.md" ]; then
cat > "$SALES_DIR/weekly-sprint.md" << 'EOF'
# Weekly Sales Sprint
> Updated every Monday morning

---

EOF
echo "✅ Created weekly-sprint.md"
fi

# Create closed-deals.md
if [ ! -f "$SALES_DIR/closed-deals.md" ]; then
cat > "$SALES_DIR/closed-deals.md" << 'EOF'
# Closed Deals
> Won and lost deals — your most valuable data

---

## Won Deals

<!-- Format:
### [Customer] @ [Company] — WON [YYYY-MM-DD]
- **Value**: [amount]
- **Cycle length**: [X days from first contact to close]
- **Customer type**: [Tiger/Peacock/Koala/Owl]
- **What worked**: [key factor that closed the deal]
-->

---

## Lost Deals

<!-- Format:
### [Customer] @ [Company] — LOST [YYYY-MM-DD]
- **Stage when lost**: [stage name]
- **Customer type**: [Tiger/Peacock/Koala/Owl]
- **Lost reason**: [price/competition/no budget/timing/no decision]
- **What I'd do differently**: [honest reflection]
- **Reactivation date**: [when to try again, if ever]
-->

EOF
echo "✅ Created closed-deals.md"
fi

echo ""
echo "✅ Sales Rhythm Tracker workspace ready at: $SALES_DIR"
echo ""
echo "Next steps:"
echo "  1. Add your first lead via your OpenClaw agent:"
echo "     'New lead: [Name] at [Company] — [context]'"
echo "  2. Get your first morning brief:"
echo "     'Morning sales brief'"
echo "  3. Set up daily automation (optional):"
echo "     openclaw cron add --name morning-sales --schedule '0 8 * * 1-5' --message 'Morning sales brief'"
