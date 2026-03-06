#!/bin/bash
# Quick Z.AI usage check - returns one-line status

source ~/.openclaw/secrets/zai.env 2>/dev/null

if [ -z "$ZAI_JWT_TOKEN" ]; then
    echo "ZAI: Not configured"
    exit 0
fi

RESPONSE=$(curl -s -H "Authorization: Bearer $ZAI_JWT_TOKEN" \
  "https://api.z.ai/api/monitor/usage/quota/limit" 2>/dev/null)

if ! echo "$RESPONSE" | jq -e '.success == true' > /dev/null 2>&1; then
    echo "ZAI: Auth error"
    exit 0
fi

# Get 5-hour quota percentage
PERCENT=$(echo "$RESPONSE" | jq -r '.data.limits[] | select(.type == "TOKENS_LIMIT" and .unit == 3) | .percentage' 2>/dev/null | head -1)
MONTHLY_PERCENT=$(echo "$RESPONSE" | jq -r '.data.limits[] | select(.type == "TOKENS_LIMIT" and .unit == 6) | .percentage' 2>/dev/null | head -1)

if [ -z "$PERCENT" ] || [ "$PERCENT" = "null" ]; then
    PERCENT=0
fi

# Format output
if [ "$PERCENT" -lt 50 ]; then
    ICON="✅"
elif [ "$PERCENT" -lt 80 ]; then
    ICON="⚠️"
else
    ICON="🔴"
fi

echo "ZAI: $ICON ${PERCENT}% 5h | ${MONTHLY_PERCENT}% monthly"
