#!/bin/bash
# Zhipu Image Generation Script (CogView)
#
# SECURITY: Requires ZHIPU_API_KEY environment variable

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
PROMPT="$1"

# Validate prompt length
if [ ${#PROMPT} -gt 1000 ]; then
    echo "Error: Prompt exceeds maximum length" >&2
    exit 1
fi

# Build JSON payload using jq for safe escaping
PROMPT_JSON=$(jq -n --arg p "$PROMPT" '$p')

PAYLOAD=$(jq -n \
    --argjson prompt "$PROMPT_JSON" \
    '{
        model: "cogview-4",
        prompt: $prompt,
        size: "1024x1024",
        quality: "standard"
    }')

# Call Zhipu API
RESULT=$(curl -s --proto =https --tlsv1.2 -m 60 -X POST "https://open.bigmodel.cn/api/paas/v4/images/generations" \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

# Extract image URL or error
ERROR_MSG=$(echo "$RESULT" | jq -r '.error.message // empty' 2>/dev/null)
if [ -n "$ERROR_MSG" ]; then
    echo "API Error: $ERROR_MSG" >&2
    exit 1
fi

IMAGE_URL=$(echo "$RESULT" | jq -r '.data[0].url // empty' 2>/dev/null)
if [ -n "$IMAGE_URL" ] && [ "$IMAGE_URL" != "null" ]; then
    echo "$IMAGE_URL"
else
    echo "Error: Failed to generate image" >&2
    exit 1
fi
