#!/bin/bash
# Signal Poll - Cron-based polling with conversation history and OpenClaw wake
# Run every minute via cron: * * * * * /path/to/signal-poll.sh
# Handles text messages, voice messages, and attachments
# Supports both phone number and UUID-based senders
# Role-based permissions via permissions.json

# ============ CONFIGURATION ============
# Set these for your setup:
SIGNAL_NUMBER="+YOUR_NUMBER_HERE"
SIGNAL_CLI="signal-cli"  # or full path like /usr/local/bin/signal-cli
STATE_DIR="$HOME/.signal-state"
WAKE_FILE="$STATE_DIR/pending_wakes"
HISTORY_DIR="$STATE_DIR/conversations"
PERMISSIONS_FILE="$STATE_DIR/permissions.json"

# OpenClaw wake API (set to empty to disable)
WAKE_URL="http://127.0.0.1:18789/hooks/wake"
WAKE_TOKEN="your-wake-token-here"
# =======================================

mkdir -p "$HISTORY_DIR"

# Initialize permissions file if it doesn't exist
if [[ ! -f "$PERMISSIONS_FILE" ]]; then
    echo '{}' > "$PERMISSIONS_FILE"
    echo "[$(date)] Created empty permissions file at $PERMISSIONS_FILE" >> "$STATE_DIR/monitor.log"
fi

# Get contact role from permissions.json (owner/trusted/pending/untrusted)
get_role() {
    local sender="$1"
    local role=$(python3 -c "import json; d=json.load(open('$PERMISSIONS_FILE')); print(d.get('$sender',{}).get('role','untrusted'))" 2>/dev/null)
    echo "${role:-untrusted}"
}

get_name() {
    local id="$1"
    local name=$(python3 -c "import json; d=json.load(open('$PERMISSIONS_FILE')); print(d.get('$id',{}).get('name',''))" 2>/dev/null)
    [[ -n "$name" ]] && echo "$name" || echo "$id"
}

# Receive messages with read receipts
output=$($SIGNAL_CLI -a "$SIGNAL_NUMBER" receive --send-read-receipts -t 5 2>&1)

current_sender=""
current_timestamp=""
current_timestamp_raw=""
current_attachment=""
content_type=""
has_message=false

while IFS= read -r line; do
    # Parse sender - phone number
    if [[ "$line" =~ ^Envelope\ from:.*(\+[0-9]+)\ \(device ]]; then
        current_sender="${BASH_REMATCH[1]}"
        echo "[$(date)] DEBUG: Matched Envelope, sender=$current_sender" >> "$STATE_DIR/debug-parse.log"
        has_message=false
        current_attachment=""
    elif [[ "$line" =~ ^Envelope\ from:\ (\+[0-9]+) ]]; then
        current_sender="${BASH_REMATCH[1]}"
        has_message=false
        current_attachment=""
    # Parse sender - UUID (contacts without phone numbers)
    elif [[ "$line" =~ ^Envelope\ from:.*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\ \(device ]]; then
        current_sender="${BASH_REMATCH[1]}"
        echo "[$(date)] DEBUG: Matched UUID Envelope, sender=$current_sender" >> "$STATE_DIR/debug-parse.log"
        has_message=false
        current_attachment=""
    fi

    # Parse timestamp
    if [[ "$line" =~ ^Timestamp:\ ([0-9]+) ]]; then
        ts="${BASH_REMATCH[1]}"
        current_timestamp_raw="$ts"
        current_timestamp=$(date -d "@$((ts/1000))" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "$ts")
    fi

    # Parse text body
    if [[ "$line" =~ ^Body:\ (.+)$ ]]; then
        body="${BASH_REMATCH[1]}"
        echo "[$(date)] DEBUG: Found body='$body' sender='$current_sender'" >> "$STATE_DIR/debug-parse.log"
        if [[ -n "$current_sender" && -n "$body" ]]; then
            has_message=true
            name=$(get_name "$current_sender")
            role=$(get_role "$current_sender")
            history_file="$HISTORY_DIR/${current_sender}.log"

            echo "[$current_timestamp] $name: $body" >> "$history_file"
            echo "[$(date)] Received TEXT from $name ($current_sender) [$role]: $body" >> "$STATE_DIR/monitor.log"
            echo "Signal from $name ($current_sender) [$role]: $body" >> "$WAKE_FILE"

            # Flag untrusted/pending contacts for triage
            if [[ "$role" == "untrusted" || "$role" == "pending" ]]; then
                echo "[$(date)] TRIAGE NEEDED: $role contact $name ($current_sender) messaged: $body" >> "$STATE_DIR/triage.log"
                echo "⚠️ NEW/PENDING CONTACT needs triage - $name ($current_sender) [$role]: $body" >> "$WAKE_FILE"
            fi
        fi
    fi

    # Parse attachment content type
    if [[ "$line" =~ Content-Type:\ ([^\ ]+) ]] || [[ "$line" =~ ^\ *Type:\ (.+)$ ]]; then
        content_type="${BASH_REMATCH[1]}"
    fi

    # Parse attachment file path
    if [[ "$line" =~ Stored\ plaintext\ in:\ (.+)$ ]]; then
        current_attachment="${BASH_REMATCH[1]}"
        echo "[$(date)] DEBUG: Found attachment='$current_attachment' type='$content_type' sender='$current_sender'" >> "$STATE_DIR/debug-parse.log"

        if [[ -n "$current_sender" && -n "$current_attachment" ]]; then
            has_message=true
            name=$(get_name "$current_sender")
            role=$(get_role "$current_sender")
            history_file="$HISTORY_DIR/${current_sender}.log"

            if [[ "$content_type" == *"audio"* ]] || [[ "$content_type" == *"ogg"* ]]; then
                attachment_type="VOICE MESSAGE"
            elif [[ "$content_type" == *"image"* ]]; then
                attachment_type="IMAGE"
            else
                attachment_type="ATTACHMENT ($content_type)"
            fi

            echo "[$current_timestamp] $name: [$attachment_type] $current_attachment" >> "$history_file"
            echo "[$(date)] Received $attachment_type from $name ($current_sender) [$role]: $current_attachment" >> "$STATE_DIR/monitor.log"
            echo "Signal $attachment_type from $name ($current_sender) [$role]: $current_attachment" >> "$WAKE_FILE"

            # Send "viewed" receipt for voice messages
            if [[ "$attachment_type" == "VOICE MESSAGE" && -n "$current_timestamp_raw" ]]; then
                $SIGNAL_CLI -a "$SIGNAL_NUMBER" sendReceipt --type viewed -t "$current_timestamp_raw" "$current_sender" 2>/dev/null
                echo "[$(date)] Sent VIEWED receipt to $name for timestamp $current_timestamp_raw" >> "$STATE_DIR/monitor.log"
            fi

            # Flag untrusted/pending contacts for triage
            if [[ "$role" == "untrusted" || "$role" == "pending" ]]; then
                echo "[$(date)] TRIAGE NEEDED: $role contact $name ($current_sender) sent $attachment_type" >> "$STATE_DIR/triage.log"
                echo "⚠️ NEW/PENDING CONTACT needs triage - $name ($current_sender) [$role] sent $attachment_type" >> "$WAKE_FILE"
            fi

            current_attachment=""
        fi
    fi

done <<< "$output"

# Trigger OpenClaw wake API if there are pending messages
if [[ -s "$WAKE_FILE" && -n "$WAKE_URL" && -n "$WAKE_TOKEN" ]]; then
    curl -s -X POST "$WAKE_URL" \
      -H "Authorization: Bearer $WAKE_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"text": "Signal message received", "mode": "now"}' > /dev/null 2>&1
    echo "[$(date)] Triggered OpenClaw wake for pending Signal messages" >> "$STATE_DIR/monitor.log"
fi
