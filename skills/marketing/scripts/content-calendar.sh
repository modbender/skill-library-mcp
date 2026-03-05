#!/bin/bash
# content-calendar.sh - Manage your content calendar
# Usage: ./content-calendar.sh [command] [args]

CALENDAR_DIR="${HOME}/.openclaw/workspace/content"
CALENDAR_FILE="${CALENDAR_DIR}/calendar.md"

mkdir -p "$CALENDAR_DIR"

case "$1" in
    init)
        if [ ! -f "$CALENDAR_FILE" ]; then
            cat > "$CALENDAR_FILE" << 'EOF'
# Content Calendar

## This Week

| Date | Platform | Type | Topic | Status |
|------|----------|------|-------|--------|

## Upcoming

| Date | Platform | Type | Topic | Status |
|------|----------|------|-------|--------|

## Content Bank (Ready to Use)

### Twitter
- 

### LinkedIn
- 

### Instagram
- 

## Ideas Backlog
- 

EOF
            echo "✅ Content calendar initialized at $CALENDAR_FILE"
        else
            echo "Calendar already exists at $CALENDAR_FILE"
        fi
        ;;
    
    add)
        if [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ]; then
            echo "Usage: $0 add <date> <platform> <topic>"
            echo "Example: $0 add 2024-01-15 twitter 'Thread on productivity'"
            exit 1
        fi
        echo "| $2 | $3 | post | $4 | draft |" >> "$CALENDAR_FILE"
        echo "✅ Added: $4 for $3 on $2"
        ;;
    
    week)
        echo "📅 This Week's Content"
        echo "====================="
        if [ -f "$CALENDAR_FILE" ]; then
            grep -A 20 "## This Week" "$CALENDAR_FILE" | head -25
        else
            echo "No calendar found. Run: $0 init"
        fi
        ;;
    
    month)
        echo "📅 Content Calendar"
        echo "==================="
        if [ -f "$CALENDAR_FILE" ]; then
            cat "$CALENDAR_FILE"
        else
            echo "No calendar found. Run: $0 init"
        fi
        ;;
    
    *)
        echo "Content Calendar Manager"
        echo "========================"
        echo "Commands:"
        echo "  init           - Initialize calendar"
        echo "  add <date> <platform> <topic> - Add content item"
        echo "  week           - View this week's content"
        echo "  month          - View full calendar"
        ;;
esac
