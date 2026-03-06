#!/usr/bin/env bash
# Turnip Prophet cron handler
# Reads config from memory/turnip-config.json

set -eo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_FILE="$SKILL_DIR/memory/turnip-config.json"
MEMORY_FILE="$SKILL_DIR/memory/turnip-week.json"
EVENT="${1:-}"

# Load config
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "Error: Config not found at $CONFIG_FILE" >&2
    echo "Run the skill setup first to configure reminders." >&2
    exit 1
fi

CHANNEL=$(jq -r '.channel // ""' "$CONFIG_FILE")
TARGET=$(jq -r '.target // ""' "$CONFIG_FILE")
OPENCLAW_BIN=$(jq -r '.openclaw_bin // ""' "$CONFIG_FILE")

if [[ -z "$CHANNEL" ]] || [[ -z "$TARGET" ]] || [[ -z "$OPENCLAW_BIN" ]]; then
    echo "Error: Invalid config in $CONFIG_FILE" >&2
    exit 1
fi

send_message() {
    local message="$1"
    "$OPENCLAW_BIN" gateway call message.send \
        --params "{\"channel\":\"$CHANNEL\",\"target\":\"$TARGET\",\"message\":\"$message\"}" \
        2>&1 | logger -t turnip-prophet-cron
}

get_current_week_start() {
    # ACNH weeks start on Sunday
    date -d "$(date +%Y-%m-%d) - $(date +%w) days" +%Y-%m-%d
}

case "$EVENT" in
    sunday-daisy)
        WEEK_START=$(get_current_week_start)
        
        if [[ -f "$MEMORY_FILE" ]]; then
            STORED_WEEK=$(jq -r '.week_start // ""' "$MEMORY_FILE")
            BUY_PRICE=$(jq -r '.buy_price // null' "$MEMORY_FILE")
            
            # If it's a new week or no buy price set
            if [[ "$STORED_WEEK" != "$WEEK_START" ]] || [[ "$BUY_PRICE" == "null" ]]; then
                send_message "🔔 Sunday! Check Daisy Mae's turnip price (90-110 bells) and buy your turnips 🥬"
            fi
        else
            # No memory file exists yet
            send_message "🔔 Sunday! Check Daisy Mae's turnip price (90-110 bells) and buy your turnips 🥬"
        fi
        ;;
        
    daily-check)
        if [[ ! -f "$MEMORY_FILE" ]]; then
            # No data yet, skip
            exit 0
        fi
        
        WEEK_START=$(get_current_week_start)
        STORED_WEEK=$(jq -r '.week_start // ""' "$MEMORY_FILE")
        
        # Only remind if we're in the same week
        if [[ "$STORED_WEEK" != "$WEEK_START" ]]; then
            exit 0
        fi
        
        # Determine which slot we're in (Mon AM = 0, Mon PM = 1, ..., Sat PM = 11)
        DAY_OF_WEEK=$(date +%w)  # 0=Sun, 1=Mon, ..., 6=Sat
        HOUR=$(date +%H)
        
        # Skip if Sunday (0)
        if [[ "$DAY_OF_WEEK" -eq 0 ]]; then
            exit 0
        fi
        
        # Calculate slot index (Mon AM = 0)
        if [[ "$HOUR" -lt 12 ]]; then
            SLOT=$(( (DAY_OF_WEEK - 1) * 2 ))  # AM slot
            TIME_LABEL="morning"
        else
            SLOT=$(( (DAY_OF_WEEK - 1) * 2 + 1 ))  # PM slot
            TIME_LABEL="evening"
        fi
        
        # Check if this slot is already filled
        PRICE=$(jq -r ".prices[$SLOT] // null" "$MEMORY_FILE")
        
        if [[ "$PRICE" == "null" ]]; then
            # Get day name
            DAY_NAME=$(date +%A)
            send_message "🔔 ${DAY_NAME} ${TIME_LABEL}: Check Nook's Cranny turnip prices!"
        fi
        ;;
        
    saturday-final)
        if [[ ! -f "$MEMORY_FILE" ]]; then
            # No data, send generic warning
            send_message "⏰ FINAL CALL: Turnips expire at 10 PM tonight! Sell now or they'll rot 🗑️"
            exit 0
        fi
        
        WEEK_START=$(get_current_week_start)
        STORED_WEEK=$(jq -r '.week_start // ""' "$MEMORY_FILE")
        
        # Only warn if we're in the same week
        if [[ "$STORED_WEEK" == "$WEEK_START" ]]; then
            # Count how many prices are still null
            NULL_COUNT=$(jq '[.prices[] | select(. == null)] | length' "$MEMORY_FILE")
            
            if [[ "$NULL_COUNT" -gt 0 ]]; then
                send_message "⏰ FINAL CALL: Turnips expire at 10 PM! You're missing $NULL_COUNT price check(s). Sell now or they'll rot 🗑️"
            else
                # All prices known, just remind to sell
                send_message "⏰ Last chance to sell turnips tonight! Nook's Cranny closes at 10 PM 🗑️"
            fi
        fi
        ;;
        
    *)
        echo "Unknown event: $EVENT" >&2
        exit 1
        ;;
esac
