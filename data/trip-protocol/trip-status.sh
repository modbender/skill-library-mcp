#!/bin/bash
# trip-status.sh - Check current trip status
# Usage: ./trip-status.sh

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
SCHEDULED_DIR="$WORKSPACE/memory/scheduled"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[trip]${NC} $1"; }
warn() { echo -e "${YELLOW}[trip]${NC} $1"; }

# Check if SOUL.md has active trip marker
if [ -f "$WORKSPACE/SOUL.md" ]; then
    if grep -q "🍄 Active Trip" "$WORKSPACE/SOUL.md"; then
        echo ""
        echo -e "${CYAN}═══════════════════════════════════════${NC}"
        echo -e "${CYAN}  🍄 TRIP ACTIVE${NC}"
        echo -e "${CYAN}═══════════════════════════════════════${NC}"
        
        # Extract trip info from SOUL.md
        TRIP_SECTION=$(sed -n '/🍄 Active Trip/,/^---$/p' "$WORKSPACE/SOUL.md" | head -10)
        echo "$TRIP_SECTION" | grep -E "^\*\*|^##" | head -5
        
        # Check for scheduled restore
        if [ -d "$SCHEDULED_DIR" ]; then
            SCHEDULED=$(ls -t "$SCHEDULED_DIR"/trip-restore-*.json 2>/dev/null | head -1)
            if [ -n "$SCHEDULED" ] && [ -f "$SCHEDULED" ]; then
                RESTORE_TIME=$(jq -r '.triggerAt' "$SCHEDULED" 2>/dev/null)
                TOKEN_ID=$(jq -r '.tokenId' "$SCHEDULED" 2>/dev/null)
                STATUS=$(jq -r '.status' "$SCHEDULED" 2>/dev/null)
                
                echo ""
                echo -e "${YELLOW}Scheduled Restore:${NC}"
                echo "  Token:  #$TOKEN_ID"
                echo "  Time:   $RESTORE_TIME"
                echo "  Status: $STATUS"
                
                # Calculate time remaining
                if command -v python3 &>/dev/null; then
                    REMAINING=$(python3 -c "
from datetime import datetime, timezone
try:
    end = datetime.fromisoformat('$RESTORE_TIME'.replace('Z', '+00:00'))
    now = datetime.now(timezone.utc)
    delta = end - now
    if delta.total_seconds() > 0:
        hours = int(delta.total_seconds() // 3600)
        mins = int((delta.total_seconds() % 3600) // 60)
        print(f'{hours}h {mins}m remaining')
    else:
        print('should have ended')
except:
    pass
" 2>/dev/null)
                    if [ -n "$REMAINING" ]; then
                        echo "  Left:   $REMAINING"
                    fi
                fi
            fi
        fi
        
        echo -e "${CYAN}═══════════════════════════════════════${NC}"
        echo ""
        echo "To restore early: ./restore.sh"
        echo "To view journal:  cat \$WORKSPACE/memory/trips/*.md"
    else
        echo ""
        log "No active trip."
        echo ""
        
        # Check for recent journals
        JOURNAL_DIR="$WORKSPACE/memory/trips"
        if [ -d "$JOURNAL_DIR" ]; then
            LATEST=$(ls -t "$JOURNAL_DIR"/*.md 2>/dev/null | head -1)
            if [ -n "$LATEST" ]; then
                log "Most recent trip: $(basename "$LATEST")"
            fi
        fi
        
        # Check for pending scheduled restores (shouldn't exist if no active trip)
        if [ -d "$SCHEDULED_DIR" ]; then
            PENDING=$(ls "$SCHEDULED_DIR"/trip-restore-*.json 2>/dev/null | wc -l)
            if [ "$PENDING" -gt 0 ]; then
                warn "Found $PENDING pending restore(s) but no active trip marker."
                warn "Run: ls $SCHEDULED_DIR"
            fi
        fi
    fi
else
    log "No SOUL.md found at $WORKSPACE/SOUL.md"
fi
