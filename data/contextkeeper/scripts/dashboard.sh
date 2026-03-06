#!/bin/bash
# ContextKeeper Dashboard v0.1.3
# Shows active projects, recent checkpoints, and status

set -e

CKPT_DIR="$HOME/.memory/contextkeeper"
CHECKPOINTS_DIR="$CKPT_DIR/checkpoints"
PROJECTS_DIR="$CKPT_DIR/projects"

# Initialize variables to ensure they're always defined
PROJECT_ID=""

# Colors (if terminal supports them)
if [ -t 1 ]; then
    BOLD='\033[1m'
    DIM='\033[2m'
    RESET='\033[0m'
    CYAN='\033[36m'
    GREEN='\033[32m'
    YELLOW='\033[33m'
    RED='\033[31m'
else
    BOLD='' DIM='' RESET='' CYAN='' GREEN='' YELLOW='' RED=''
fi

# Header
echo ""
echo "${BOLD}${CYAN}🔮 ContextKeeper Dashboard${RESET}"
echo "${DIM}$(date '+%Y-%m-%d %H:%M UTC')${RESET}"
echo ""

# Check if initialized
if [ ! -d "$CKPT_DIR" ]; then
    echo "${YELLOW}⚠️ ContextKeeper not initialized.${RESET}"
    echo " Run: ckpt.sh to create first checkpoint"
    echo ""
    exit 1
fi

# Current state
CURRENT="$CKPT_DIR/current-state.json"
if [ -L "$CURRENT" ] && [ -f "$CURRENT" ]; then
    echo "${BOLD}Current Session${RESET}"
    echo "─────────────────────────────────────────"
    # Parse current checkpoint (using basic shell tools)
    if [ -f "$CURRENT" ]; then
        PROJECT_ID=$(grep '"project_id"' "$CURRENT" 2>/dev/null | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
        PROJECT_NAME=$(grep '"project_name"' "$CURRENT" 2>/dev/null | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
        SUMMARY=$(grep '"summary"' "$CURRENT" 2>/dev/null | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/' | cut -c1-60)
        TIMESTAMP=$(grep '"timestamp"' "$CURRENT" 2>/dev/null | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
        
        # Convert timestamp to relative time (with improved error handling)
        REL_TIME=""
        if [ -n "$TIMESTAMP" ] && command -v python3 > /dev/null 2>&1; then
            REL_TIME=$(python3 -c "
from datetime import datetime
try:
    ts = '${TIMESTAMP}'.replace('Z', '+00:00')
    td = datetime.utcnow() - datetime.fromisoformat(ts)
    mins = int(td.total_seconds() // 60)
    if mins < 1:
        print('just now')
    elif mins < 60:
        print(f'{mins}m ago')
    elif mins < 1440:
        print(f'{mins//60}h {mins%60}m ago')
    else:
        print(f'{mins//1440}d ago')
except Exception:
    pass
" 2>/dev/null)
        fi
        [ -z "$REL_TIME" ] && REL_TIME="${TIMESTAMP:-unknown}"
        
        echo " ${BOLD}Project:${RESET} $PROJECT_NAME ($PROJECT_ID)"
        echo " ${BOLD}Last checkpoint:${RESET} $REL_TIME"
        echo " ${BOLD}Summary:${RESET} $SUMMARY"
        echo ""
    fi
elif [ -L "$CURRENT" ] && [ ! -f "$CURRENT" ]; then
    # Broken symlink - clean it up
    rm -f "$CURRENT"
    echo "${YELLOW}⚠️ Current checkpoint was deleted. Run ckpt.sh to create a new one.${RESET}"
    echo ""
fi

# Active Projects
echo "${BOLD}Active Projects${RESET}"
echo "─────────────────────────────────────────"
if [ -d "$PROJECTS_DIR" ]; then
    PROJECT_COUNT=0
    for proj in "$PROJECTS_DIR"/*/latest.json; do
        [ -f "$proj" ] || continue
        PROJECT_COUNT=$((PROJECT_COUNT + 1))
        PROJ_ID=$(basename "$(dirname "$proj")")
        PROJ_NAME=$(grep '"project_name"' "$proj" 2>/dev/null | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
        LAST_CHECKPOINT=$(grep '"last_checkpoint"' "$proj" 2>/dev/null | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
        STATUS=$(grep '"status"' "$proj" 2>/dev/null | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
        case "$STATUS" in
            active) ICON="${GREEN}●${RESET}" ;;
            blocked) ICON="${RED}●${RESET}" ;;
            paused) ICON="${YELLOW}○${RESET}" ;;
            *) ICON="${DIM}○${RESET}" ;;
        esac
        if [ "$PROJ_ID" = "$PROJECT_ID" ]; then
            echo " ${ICON} ${BOLD}${PROJ_NAME}${RESET} ${DIM}($PROJ_ID) — active${RESET}"
        else
            echo " ${ICON} ${PROJ_NAME} ${DIM}($PROJ_ID) — $STATUS${RESET}"
        fi
    done
    if [ "$PROJECT_COUNT" -eq 0 ]; then
        echo " ${DIM}No projects tracked yet.${RESET}"
        echo " Run: ckpt.sh from within a git repository"
    fi
else
    echo " ${DIM}No projects found.${RESET}"
fi
echo ""

# Recent Checkpoints
echo "${BOLD}Recent Checkpoints${RESET}"
echo "─────────────────────────────────────────"
if [ -d "$CHECKPOINTS_DIR" ]; then
    # Get latest 5 checkpoints
    ls -t "$CHECKPOINTS_DIR"/*.json 2>/dev/null | head -5 | while read -r ckpt; do
        [ -f "$ckpt" ] || continue
        CKPT_NAME=$(basename "$ckpt" .json)
        CKPT_PROJ=$(grep '"project_name"' "$ckpt" 2>/dev/null | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
        CKPT_TIME=$(grep '"timestamp"' "$ckpt" 2>/dev/null | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
        echo " ${DIM}${CKPT_TIME:11:5}${RESET} ${CYAN}$CKPT_PROJ${RESET}"
    done || echo " ${DIM}No checkpoints yet${RESET}"
else
    echo " ${DIM}No checkpoints directory${RESET}"
fi
echo ""

# Quick Actions
echo "${BOLD}Quick Actions${RESET}"
echo "─────────────────────────────────────────"
echo " ckpt.sh                 # Create checkpoint"
echo " ckpt.sh \"message\"      # Checkpoint with summary"
echo " dashboard.sh            # View project state"
echo " ls ~/.memory/contextkeeper/  # Browse checkpoints"
echo ""
