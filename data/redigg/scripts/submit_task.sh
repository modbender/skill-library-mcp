#!/bin/bash
# Redigg Claim and Submit Task Script
# Usage: ./submit_task.sh <agent_api_key> <task_id> <result_json>

API_KEY="$1"
TASK_ID="$2"
RESULT_JSON="$3"

if [ -z "$API_KEY" ] || [ -z "$TASK_ID" ] || [ -z "$RESULT_JSON" ]; then
    echo "Error: Missing required arguments"
    echo "Usage: $0 <agent_api_key> <task_id> '<result_json>'"
    exit 1
fi

# Claim task
CLAIM_RESPONSE=$(curl -s -X POST \
    -H "Authorization: Bearer $API_KEY" \
    "https://redigg.com/api/agent/tasks/$TASK_ID/claim")

if ! echo "$CLAIM_RESPONSE" | grep -q '"success":true'; then
    echo "CLAIM_FAILED:$CLAIM_RESPONSE"
    exit 1
fi

# Submit result
SUBMIT_RESPONSE=$(curl -s -X POST \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "$RESULT_JSON" \
    "https://redigg.com/api/agent/tasks/$TASK_ID/submit")

if echo "$SUBMIT_RESPONSE" | grep -q '"success":true'; then
    echo "SUBMIT_OK"
else
    echo "SUBMIT_FAILED:$SUBMIT_RESPONSE"
fi
