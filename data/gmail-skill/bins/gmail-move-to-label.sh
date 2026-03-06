#!/usr/bin/env bash
set -euo pipefail

# Gmail Move to Label - Interactive message filing via keyword search
# Usage: gmail-move-to-label.sh [gmail-account]

ACCOUNT="${1:-${GMAIL_ACCOUNT:-}}"

if [[ -z "$ACCOUNT" ]]; then
    echo "Error: No Gmail account specified" >&2
    echo "Usage: $0 <gmail-account>" >&2
    echo "Or set GMAIL_ACCOUNT environment variable" >&2
    exit 1
fi

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to search for labels matching keywords
search_labels() {
    local keywords="$1"
    local all_labels
    
    echo -e "${BLUE}Searching for labels matching: ${keywords}${NC}" >&2
    
    # Get all labels
    all_labels=$(gog gmail labels list --account "$ACCOUNT" --plain 2>/dev/null | tail -n +2 | cut -f1)
    
    # Filter labels using case-insensitive grep with the keywords
    # Convert keywords to grep pattern (each word as optional match)
    local pattern
    pattern=$(echo "$keywords" | tr '[:upper:]' '[:lower:]' | sed 's/ /.*|.*/g')
    
    echo "$all_labels" | grep -i "$pattern" || true
}

# Function to list inbox messages
list_inbox_messages() {
    local max="${1:-50}"
    
    echo -e "${BLUE}Fetching inbox messages...${NC}" >&2
    
    # Search for messages in inbox
    gog gmail messages search "in:inbox" \
        --account "$ACCOUNT" \
        --max "$max" \
        --plain 2>/dev/null
}

# Function to move messages to a label
move_messages_to_label() {
    local label="$1"
    shift
    local message_ids=("$@")
    
    if [[ ${#message_ids[@]} -eq 0 ]]; then
        echo -e "${RED}No messages to move${NC}" >&2
        return 1
    fi
    
    echo -e "${BLUE}Moving ${#message_ids[@]} message(s) to label: ${label}${NC}" >&2
    
    # Add the target label and remove INBOX label
    gog gmail batch modify "${message_ids[@]}" \
        --add-labels "$label" \
        --remove-labels "INBOX" \
        --account "$ACCOUNT" 2>/dev/null
    
    echo -e "${GREEN}✓ Moved ${#message_ids[@]} message(s) to ${label}${NC}" >&2
}

# Function to undo move (restore to inbox, remove target label)
undo_move() {
    local label="$1"
    shift
    local message_ids=("$@")
    
    if [[ ${#message_ids[@]} -eq 0 ]]; then
        echo -e "${RED}No messages to undo${NC}" >&2
        return 1
    fi
    
    echo -e "${BLUE}Undoing move for ${#message_ids[@]} message(s)...${NC}" >&2
    
    # Remove target label and restore INBOX label
    gog gmail batch modify "${message_ids[@]}" \
        --remove-labels "$label" \
        --add-labels "INBOX" \
        --account "$ACCOUNT" 2>/dev/null
    
    echo -e "${GREEN}✓ Restored ${#message_ids[@]} message(s) to inbox${NC}" >&2
}

# Main workflow
echo -e "${BLUE}=== Gmail Move to Label ===${NC}"
echo -e "${BLUE}Account: ${ACCOUNT}${NC}"
echo ""

# Output format for agent consumption:
# STEP: <step-name>
# DATA: <json-or-tsv-data>
# PROMPT: <what-to-ask-user>

# Step 1: Ready to receive keywords
echo "STEP: READY"
echo "PROMPT: Enter keywords to search for target label (or 'quit' to exit)"
echo "STATUS: Awaiting user input for label search keywords"

# This script is designed to be called interactively by the agent
# The agent should:
# 1. Call with keywords: gmail-move-to-label.sh --search-labels "keywords"
# 2. Call to list inbox: gmail-move-to-label.sh --list-inbox
# 3. Call to move: gmail-move-to-label.sh --move "label" msg1 msg2 msg3
# 4. Call to undo: gmail-move-to-label.sh --undo "label" msg1 msg2 msg3

# Parse command-line action
ACTION="${2:-}"

case "$ACTION" in
    --search-labels)
        KEYWORDS="${3:-}"
        if [[ -z "$KEYWORDS" ]]; then
            echo "ERROR: No keywords provided" >&2
            exit 1
        fi
        
        MATCHES=$(search_labels "$KEYWORDS")
        
        if [[ -z "$MATCHES" ]]; then
            echo "STEP: NO_MATCHES"
            echo "PROMPT: No labels found matching '$KEYWORDS'. Enter new keywords or type 'abandon' to quit"
            exit 0
        fi
        
        echo "STEP: LABEL_MATCHES"
        echo "DATA:"
        echo "$MATCHES"
        echo "PROMPT: Select a label from the list above, or choose: [abandon] to quit, [new-search] to enter new keywords"
        ;;
        
    --list-inbox)
        MAX="${3:-50}"
        MESSAGES=$(list_inbox_messages "$MAX")
        
        if [[ -z "$MESSAGES" ]] || [[ $(echo "$MESSAGES" | wc -l) -le 1 ]]; then
            echo "STEP: NO_MESSAGES"
            echo "PROMPT: No messages in inbox"
            exit 0
        fi
        
        echo "STEP: INBOX_LIST"
        echo "DATA:"
        echo "$MESSAGES"
        echo "PROMPT: Select message IDs to move (space-separated), or type 'abandon' to quit"
        ;;
        
    --move)
        TARGET_LABEL="${3:-}"
        shift 3 || true
        MESSAGE_IDS=("$@")
        
        if [[ -z "$TARGET_LABEL" ]]; then
            echo "ERROR: No target label provided" >&2
            exit 1
        fi
        
        if [[ ${#MESSAGE_IDS[@]} -eq 0 ]]; then
            echo "ERROR: No message IDs provided" >&2
            exit 1
        fi
        
        move_messages_to_label "$TARGET_LABEL" "${MESSAGE_IDS[@]}"
        
        echo "STEP: MOVED"
        echo "DATA: {\"label\": \"$TARGET_LABEL\", \"count\": ${#MESSAGE_IDS[@]}, \"message_ids\": [\"${MESSAGE_IDS[*]}\"]}"
        echo "PROMPT: Messages moved to $TARGET_LABEL. Type 'undo' to reverse, or 'done' to finish"
        ;;
        
    --undo)
        TARGET_LABEL="${3:-}"
        shift 3 || true
        MESSAGE_IDS=("$@")
        
        if [[ -z "$TARGET_LABEL" ]]; then
            echo "ERROR: No target label provided" >&2
            exit 1
        fi
        
        if [[ ${#MESSAGE_IDS[@]} -eq 0 ]]; then
            echo "ERROR: No message IDs provided" >&2
            exit 1
        fi
        
        undo_move "$TARGET_LABEL" "${MESSAGE_IDS[@]}"
        
        echo "STEP: UNDONE"
        echo "DATA: {\"label\": \"$TARGET_LABEL\", \"count\": ${#MESSAGE_IDS[@]}}"
        echo "PROMPT: Move undone. Messages restored to inbox. Type 'done' to finish or start a new search"
        ;;
        
    *)
        echo "STEP: READY"
        echo "PROMPT: Enter keywords to search for target label, or type 'quit' to exit"
        ;;
esac
