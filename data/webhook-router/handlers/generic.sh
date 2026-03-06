#!/bin/bash
#
# Generic Webhook Handler
# Fallback handler for unknown webhook sources
# Logs payload and attempts to extract meaningful information
#

set -euo pipefail

# Arguments
PAYLOAD="$1"
SOURCE="${2:-unknown}"
EVENT_TYPE="${3:-unknown}"

# Configuration
ALERT_CHANNEL="${WEBHOOK_ALERT_CHANNEL:-telegram}"
VAULT_SECTION="webhooks/generic"
LOG_LIMIT="${WEBHOOK_LOG_LIMIT:-10000}"

# Ensure jq is available
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required" >&2
    exit 1
fi

# Helper: Send alert
send_alert() {
    local title="$1"
    local body="$2"
    
    echo "ALERT: $title"
    echo "$body"
    
    # Try to use message tool if available
    if command -v message &> /dev/null; then
        message send "$ALERT_CHANNEL" "$title" <<< "$body" 2>/dev/null || true
    fi
}

# Helper: Write to vault
write_to_vault() {
    local path="$1"
    local content="$2"
    local tags="$3"
    
    if command -v vault &> /dev/null; then
        vault write "$path" --data "$content" --tags "$tags" 2>/dev/null || true
    fi
}

# Generate timestamp
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
VAULT_PATH="${VAULT_SECTION}/${SOURCE}/${EVENT_TYPE}"

# Truncate payload if too large
PAYLOAD_SIZE=$(echo "$PAYLOAD" | wc -c)
if [[ $PAYLOAD_SIZE -gt $LOG_LIMIT ]]; then
    TRUNCATED_PAYLOAD=$(echo "$PAYLOAD" | head -c $LOG_LIMIT)
    TRUNCATED_PAYLOAD="${TRUNCATED_PAYLOAD}... [truncated, total size: $PAYLOAD_SIZE bytes]"
else
    TRUNCATED_PAYLOAD="$PAYLOAD"
fi

# Attempt to extract common fields from payload
extract_field() {
    local field="$1"
    echo "$PAYLOAD" | jq -r "$field // empty" 2>/dev/null | head -c 1000
}

# Try to find meaningful identifiers
IDENTIFIER=$(extract_field '.id // .event_id // .uuid // .reference // .webhook_id')
SERVICE_NAME=$(extract_field '.service // .source // .app // .integration')
EVENT_NAME=$(extract_field '.event // .event_type // .type // .action // .kind')
STATUS=$(extract_field '.status // .state // .result // .outcome')
USER=$(extract_field '.user // .username // .email // .user_id // .account')

# Build a summary
SUMMARY=""
[[ -n "$SERVICE_NAME" ]] && SUMMARY+="Service: $SERVICE_NAME\n"
[[ -n "$EVENT_NAME" ]] && SUMMARY+="Event: $EVENT_NAME\n"
[[ -n "$IDENTIFIER" ]] && SUMMARY+="ID: $IDENTIFIER\n"
[[ -n "$STATUS" ]] && SUMMARY+="Status: $STATUS\n"
[[ -n "$USER" ]] && SUMMARY+="User: $USER\n"

# Detect potential importance
IS_IMPORTANT=false
IMPORTANCE_REASONS=()

# Check for error/failure status
if [[ "$STATUS" =~ (error|failed|failure|critical|alert|warning) ]]; then
    IS_IMPORTANT=true
    IMPORTANCE_REASONS+=("status indicates issue: $STATUS")
fi

# Check for event type that might need attention
if [[ "$EVENT_NAME" =~ (error|failed|critical|security|breach|incident|alert|deploy) ]]; then
    IS_IMPORTANT=true
    IMPORTANCE_REASONS+=("event type: $EVENT_NAME")
fi

# Check payload structure for error indicators
if echo "$PAYLOAD" | jq -e '.error // .errors // .failed // .exception' >/dev/null 2>&1; then
    IS_IMPORTANT=true
    IMPORTANCE_REASONS+=("payload contains error field")
fi

# Prepare vault content
VAULT_CONTENT=$(jq -n \
    --arg ts "$TIMESTAMP" \
    --arg source "$SOURCE" \
    --arg event "$EVENT_TYPE" \
    --arg identifier "$IDENTIFIER" \
    --arg service "$SERVICE_NAME" \
    --arg event_name "$EVENT_NAME" \
    --arg status "$STATUS" \
    --arg user "$USER" \
    --arg payload "$TRUNCATED_PAYLOAD" \
    --argjson important "$IS_IMPORTANT" \
    '{
        timestamp: $ts,
        source: $source,
        event_type: $event,
        identifier: $identifier,
        service: $service,
        event_name: $event_name,
        status: $status,
        user: $user,
        payload: $payload,
        flagged_important: $important
    }')

# Write to vault
write_to_vault "$VAULT_PATH/$TIMESTAMP" "$VAULT_CONTENT" "webhook,generic,${SOURCE}"

# Build response
RESPONSE=$(jq -n \
    --arg source "$SOURCE" \
    --arg event "$EVENT_TYPE" \
    --arg service "$SERVICE_NAME" \
    --arg event_name "$EVENT_NAME" \
    --arg status "$STATUS" \
    --argjson important "$IS_IMPORTANT" \
    --argjson size "$PAYLOAD_SIZE" \
    '{
        handled_by: "generic",
        source: $source,
        event_type: $event,
        detected_service: $service,
        detected_event: $event_name,
        detected_status: $status,
        flagged_important: $important,
        payload_size_bytes: $size
    }')

echo "$RESPONSE"

# Send alert if flagged as important
if [[ "$IS_IMPORTANT" == "true" ]]; then
    REASONS_STR=$(printf -- "- %s\n" "${IMPORTANCE_REASONS[@]+"${IMPORTANCE_REASONS[@]}"}")
    
    ALERT_BODY="**Source:** $SOURCE\n"
    ALERT_BODY+="**Event Type:** $EVENT_TYPE\n"
    [[ -n "$SUMMARY" ]] && ALERT_BODY+="\n**Detected Info:**\n$SUMMARY"
    ALERT_BODY+="\n**Flags:**\n$REASONS_STR"
    ALERT_BODY+="\n**Payload Size:** $PAYLOAD_SIZE bytes"
    
    send_alert "⚠️ Important webhook from $SOURCE" "$ALERT_BODY"
fi

# Output summary
if [[ "$IS_IMPORTANT" == "true" ]]; then
    echo "Processed important webhook from $SOURCE (flags: ${IMPORTANCE_REASONS[*]})"
else
    echo "Processed generic webhook from $SOURCE (size: $PAYLOAD_SIZE bytes)"
fi

exit 0
