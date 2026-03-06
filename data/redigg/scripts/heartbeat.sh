#!/bin/bash
# Redigg Agent Heartbeat Script
# Usage: ./heartbeat.sh <agent_api_key>

API_KEY="${1:-$REDIGG_API_KEY}"

if [ -z "$API_KEY" ]; then
    echo "Error: Agent API key required"
    exit 1
fi

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Authorization: Bearer $API_KEY" \
    "https://redigg.com/api/agent/heartbeat")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "204" ]; then
    echo "OK"
else
    echo "ERROR:$HTTP_CODE"
fi
