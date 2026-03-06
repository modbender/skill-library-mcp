#!/bin/bash
# lead-tracker.sh - Quick lead management CLI
# Usage: ./lead-tracker.sh [command] [args]

SALES_DIR="${HOME}/.openclaw/workspace/sales"
LEADS_DIR="$SALES_DIR/leads"
PIPELINE_FILE="$SALES_DIR/pipeline/current.md"

mkdir -p "$LEADS_DIR"

case "$1" in
    add)
        if [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ]; then
            echo "Usage: $0 add <company> <contact_name> <email>"
            echo "Example: $0 add 'Acme Corp' 'John Smith' 'john@acme.com'"
            exit 1
        fi
        
        # Create filename from company name
        filename=$(echo "$2" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
        lead_file="$LEADS_DIR/${filename}.md"
        
        cat > "$lead_file" << EOF
# Lead: $2

## Contact Info
- **Name:** $3
- **Email:** $4
- **Company:** $2

## Qualification (BANT)
- **Budget:** Unknown
- **Authority:** Unknown
- **Need:** Unknown
- **Timeline:** Unknown
- **Lead Score:** /100

## Source
- **First touchpoint:** $(date +%Y-%m-%d)

## Notes


## Activity Log
| Date | Activity | Notes |
|------|----------|-------|
| $(date +%Y-%m-%d) | Created | Initial entry |

## Next Action
- [ ] Initial outreach — Due: $(date -v+3d +%Y-%m-%d 2>/dev/null || date -d "+3 days" +%Y-%m-%d 2>/dev/null || echo "$(date +%Y-%m-%d)")
EOF
        
        echo "✅ Lead created: $lead_file"
        ;;
    
    list)
        echo "📋 All Leads"
        echo "============"
        for file in "$LEADS_DIR"/*.md; do
            if [ -f "$file" ] && [ "$(basename "$file")" != "README.md" ]; then
                name=$(grep "^# Lead:" "$file" | sed 's/# Lead: //')
                stage=$(grep -A5 "Qualification" "$file" | head -1 || echo "Lead")
                echo "- $name"
            fi
        done 2>/dev/null || echo "No leads yet. Use: $0 add <company> <contact> <email>"
        ;;
    
    update)
        if [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ]; then
            echo "Usage: $0 update <company> --stage <stage>"
            echo "Stages: lead, qualified, demo, negotiation, won, lost"
            exit 1
        fi
        
        filename=$(echo "$2" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
        lead_file="$LEADS_DIR/${filename}.md"
        
        if [ -f "$lead_file" ]; then
            echo "| $(date +%Y-%m-%d) | Stage update | Moved to: $4 |" >> "$lead_file"
            echo "✅ Updated $2 to stage: $4"
        else
            echo "❌ Lead not found: $2"
        fi
        ;;
    
    followups)
        echo "📅 Today's Follow-ups"
        echo "===================="
        today=$(date +%Y-%m-%d)
        for file in "$LEADS_DIR"/*.md; do
            if [ -f "$file" ] && [ "$(basename "$file")" != "README.md" ]; then
                if grep -q "Due: $today" "$file" 2>/dev/null; then
                    name=$(grep "^# Lead:" "$file" | sed 's/# Lead: //')
                    action=$(grep -A1 "Next Action" "$file" | tail -1)
                    echo "- $name: $action"
                fi
            fi
        done 2>/dev/null || echo "No follow-ups due today"
        ;;
    
    search)
        if [ -z "$2" ]; then
            echo "Usage: $0 search <term>"
            exit 1
        fi
        echo "🔍 Searching for: $2"
        echo "===================="
        grep -l -r "$2" "$LEADS_DIR" 2>/dev/null | while read file; do
            name=$(grep "^# Lead:" "$file" | sed 's/# Lead: //')
            echo "- $name ($file)"
        done
        ;;
    
    *)
        echo "Lead Tracker CLI"
        echo "================"
        echo "Commands:"
        echo "  add <company> <contact> <email>  - Add new lead"
        echo "  list                             - List all leads"
        echo "  update <company> --stage <stage> - Update lead stage"
        echo "  followups                        - Show today's follow-ups"
        echo "  search <term>                    - Search leads"
        ;;
esac
