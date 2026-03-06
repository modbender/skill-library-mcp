#!/bin/bash
# sales-init.sh - Initialize sales workspace
# Usage: ./sales-init.sh

SALES_DIR="${HOME}/.openclaw/workspace/sales"

echo "🚀 Initializing Sales Workspace"
echo "================================"

# Create directory structure
mkdir -p "$SALES_DIR"/{leads,pipeline,analytics,templates}

# Create leads directory with sample
if [ ! -f "$SALES_DIR/leads/README.md" ]; then
    cat > "$SALES_DIR/leads/README.md" << 'EOF'
# Leads Directory

Store lead profiles here as individual markdown files.

## Naming Convention
Use: `company-name.md`

## Template
Copy from `../templates/lead-template.md`
EOF
fi

# Create pipeline tracker
if [ ! -f "$SALES_DIR/pipeline/current.md" ]; then
    cat > "$SALES_DIR/pipeline/current.md" << 'EOF'
# Sales Pipeline

## Summary
- Total pipeline value: $0
- Weighted pipeline: $0
- Deals in pipeline: 0

## By Stage

### Lead
| Company | Value | Last Activity | Next Step |
|---------|-------|---------------|-----------|

### Qualified
| Company | Value | Last Activity | Next Step |
|---------|-------|---------------|-----------|

### Demo/Proposal
| Company | Value | Last Activity | Next Step |
|---------|-------|---------------|-----------|

### Negotiation
| Company | Value | Last Activity | Next Step |
|---------|-------|---------------|-----------|

## Closed This Month

### Won
| Company | Value | Days to Close |
|---------|-------|---------------|

### Lost
| Company | Value | Reason |
|---------|-------|--------|
EOF
fi

# Create lead template
if [ ! -f "$SALES_DIR/templates/lead-template.md" ]; then
    cat > "$SALES_DIR/templates/lead-template.md" << 'EOF'
# Lead: [Company Name]

## Contact Info
- **Name:** 
- **Title:** 
- **Email:** 
- **Phone:** 
- **LinkedIn:** 
- **Company:** 
- **Website:** 

## Qualification (BANT)
- **Budget:** [Yes/No/Unknown]
- **Authority:** [Decision-maker/Influencer/User]
- **Need:** [Strong/Moderate/Weak]
- **Timeline:** [Immediate/1-3mo/3-6mo/6mo+]
- **Lead Score:** /100

## Source
- **How they found us:** 
- **First touchpoint:** 
- **Initial interest:** 

## Notes


## Activity Log
| Date | Activity | Notes |
|------|----------|-------|

## Next Action
- [ ] — Due: 
EOF
fi

# Create follow-up tracker
if [ ! -f "$SALES_DIR/followups.md" ]; then
    cat > "$SALES_DIR/followups.md" << 'EOF'
# Daily Follow-up Queue

## Due Today
| Lead | Stage | Last Contact | Reason | Next Action |
|------|-------|--------------|--------|-------------|

## Overdue
| Lead | Stage | Days Overdue | Priority |
|------|-------|--------------|----------|

## Upcoming (Next 3 Days)
| Lead | Stage | Due Date | Action |
|------|-------|----------|--------|
EOF
fi

echo "✅ Created: $SALES_DIR/leads/"
echo "✅ Created: $SALES_DIR/pipeline/current.md"
echo "✅ Created: $SALES_DIR/analytics/"
echo "✅ Created: $SALES_DIR/templates/lead-template.md"
echo "✅ Created: $SALES_DIR/followups.md"
echo ""
echo "🎉 Sales workspace ready!"
echo "Next steps:"
echo "  1. Add leads to leads/ directory"
echo "  2. Track pipeline in pipeline/current.md"
echo "  3. Use followups.md for daily follow-up queue"
