#!/bin/bash
# Zhipu Web Search Script
#
# SECURITY: This script requires ZHIPU_API_KEY environment variable to be set.
# Do NOT source ~/.bashrc or other shell config files for security reasons.

set -euo pipefail

# Validate API key is set
if [ -z "${ZHIPU_API_KEY:-}" ]; then
    echo "Error: Required environment variable not set" >&2
    exit 1
fi

# Validate query is provided
if [ $# -lt 1 ] || [ -z "$1" ]; then
    echo "Error: Missing required argument" >&2
    exit 1
fi

KEY="$ZHIPU_API_KEY"
QUERY="$1"

# Validate query length (reasonable limit)
if [ ${#QUERY} -gt 500 ]; then
    echo "Error: Query exceeds maximum length" >&2
    exit 1
fi

# Safety: Use jq to create properly escaped JSON strings
MESSAGE_CONTENT=$(jq -n --arg q "搜索: $QUERY" '$q')
SEARCH_QUERY=$(jq -n --arg q "$QUERY" '$q')

# Build JSON payload
PAYLOAD=$(jq -n \
    --argjson msg "$MESSAGE_CONTENT" \
    --argjson sq "$SEARCH_QUERY" \
    '{
        model: "glm-4-flash",
        messages: [{"role": "user", "content": $msg}],
        tools: [{"type": "web_search", "web_search": {"search_query": $sq}}]
    }')

# Call Zhipu API with TLS verification
RESULT=$(curl -s --proto =https --tlsv1.2 -m 30 -X POST "https://open.bigmodel.cn/api/paas/v4/chat/completions" \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

# Extract content - check for errors first
ERROR_MSG=$(echo "$RESULT" | jq -r '.error.message // empty' 2>/dev/null)
if [ -n "$ERROR_MSG" ]; then
    echo "API Error: $ERROR_MSG" >&2
    exit 1
fi

# Output content
echo "$RESULT" | jq -r '.choices[0].message.content // "No results"' 2>/dev/null || echo "Failed to parse response" >&2
