#!/bin/bash
# Check Z.AI API usage and quota

# Load API key from secrets
if [ -f ~/.openclaw/secrets/zai.env ]; then
    source ~/.openclaw/secrets/zai.env
fi

if [ -z "$ZAI_API_KEY" ]; then
    echo "Error: ZAI_API_KEY not set"
    echo "Add your API key to ~/.openclaw/secrets/zai.env"
    echo "Get your key from: https://z.ai/dashboard"
    exit 1
fi

# Make API request
curl -s -H "Authorization: Bearer $ZAI_API_KEY" \
  -H "Accept: application/json" \
  "https://api.z.ai/api/monitor/usage/quota/limit" | jq '.'
