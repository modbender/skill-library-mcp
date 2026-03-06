#!/bin/bash
# Zhipu Embeddings Script

set -euo pipefail

if [ -z "${ZHIPU_API_KEY:-}" ]; then
    echo "Error: Required environment variable not set" >&2
    exit 1
fi

if [ $# -lt 1 ] || [ -z "$1" ]; then
    echo "Error: Missing required argument" >&2
    exit 1
fi

KEY="$ZHIPU_API_KEY"
TEXT="$1"

if [ ${#TEXT} -gt 5000 ]; then
    echo "Error: Text exceeds maximum length" >&2
    exit 1
fi

TEXT_JSON=$(jq -n --arg t "$TEXT" '$t')

PAYLOAD=$(jq -n \
    --argjson text "$TEXT_JSON" \
    '{
        model: "embedding-3",
        input: $text
    }')

RESULT=$(curl -s --proto =https --tlsv1.2 -m 30 -X POST "https://open.bigmodel.cn/api/paas/v4/embeddings" \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

ERROR=$(echo "$RESULT" | jq -r '.error.message // empty' 2>/dev/null)
if [ -n "$ERROR" ]; then
    echo "API Error: $ERROR" >&2
    exit 1
fi

EMBEDDING=$(echo "$RESULT" | jq -r '.data[0].embedding' 2>/dev/null)
if [ -n "$EMBEDDING" ] && [ "$EMBEDDING" != "null" ]; then
    echo "$EMBEDDING"
else
    echo "Error: Failed to get embedding" >&2
    exit 1
fi
