#!/bin/bash
# send_agent_task.sh - Force agent to respond and deliver to chat
#
# Usage: send_agent_task.sh AGENT_ID GROUP_ID "message" [timeout]
#
# Example:
#   send_agent_task.sh stock-trading -5283045656 "Analyze positions" 180

set -e

AGENT_ID="${1:?Usage: send_agent_task.sh AGENT_ID GROUP_ID message [timeout]}"
GROUP_ID="${2:?Usage: send_agent_task.sh AGENT_ID GROUP_ID message [timeout]}"
MESSAGE="${3:?Usage: send_agent_task.sh AGENT_ID GROUP_ID message [timeout]}"
TIMEOUT="${4:-180}"

OPENCLAW="${OPENCLAW_PATH:-/home/eliran/.nvm/current/bin/openclaw}"
SESSION_KEY="agent:${AGENT_ID}:telegram:group:${GROUP_ID}"

echo "[$(date)] Sending task to agent: $AGENT_ID" >> ~/agent_task.log

# Send task via openclaw agent (forces response)
RESPONSE=$("$OPENCLAW" agent \
    --agent "$AGENT_ID" \
    --session-id "$SESSION_KEY" \
    --channel telegram \
    --message "$MESSAGE" \
    --timeout "$TIMEOUT" 2>&1)

# Log response
echo "[$(date)] Response (${#RESPONSE} chars): ${RESPONSE:0:100}..." >> ~/agent_task.log

# Send response to group
if [ -n "$RESPONSE" ]; then
    "$OPENCLAW" message send \
        --channel telegram \
        --target "$GROUP_ID" \
        --message "📊 **Agent Response:**

$RESPONSE"
    echo "[$(date)] Delivered response to $GROUP_ID" >> ~/agent_task.log
else
    "$OPENCLAW" message send \
        --channel telegram \
        --target "$GROUP_ID" \
        --message "⚠️ Agent did not provide a response (timeout or error)"
    echo "[$(date)] No response received" >> ~/agent_task.log
fi
