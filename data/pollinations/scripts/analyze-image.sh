#!/bin/bash
# Pollinations Image Analysis (Vision)
# Usage: ./analyze-image.sh "image_url" [--prompt "describe this"] [--model gemini]

set -e

IMAGE_INPUT="$1"
shift || true

# Defaults
PROMPT="${PROMPT:-Describe this image in detail}"
MODEL="${MODEL:-gemini}"

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --prompt)
      PROMPT="$2"
      shift 2
      ;;
    --model)
      MODEL="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

if [[ -z "$IMAGE_INPUT" ]]; then
  echo "Usage: analyze-image.sh <image_url_or_file> [--prompt \"...\"] [--model gemini]"
  echo "Models: gemini, gemini-large, claude, openai (any vision-capable model)"
  exit 1
fi

# Build image_url content - support both URL and local file
if [[ -f "$IMAGE_INPUT" ]]; then
  # Local file: convert to base64 data URL
  MIME_TYPE="image/jpeg"
  case "$IMAGE_INPUT" in
    *.png) MIME_TYPE="image/png" ;;
    *.gif) MIME_TYPE="image/gif" ;;
    *.webp) MIME_TYPE="image/webp" ;;
  esac
  BASE64_DATA=$(base64 -w0 "$IMAGE_INPUT")
  IMAGE_URL="data:$MIME_TYPE;base64,$BASE64_DATA"
else
  IMAGE_URL="$IMAGE_INPUT"
fi

# Build request body
BODY=$(jq -n -c \
  --arg model "$MODEL" \
  --arg prompt "$PROMPT" \
  --arg image_url "$IMAGE_URL" \
  '{
    model: $model,
    messages: [{
      role: "user",
      content: [
        {type: "text", text: $prompt},
        {type: "image_url", image_url: {url: $image_url}}
      ]
    }]
  }')

# Make request
echo "Analyzing image with $MODEL..."

AUTH_HEADER=""
if [[ -n "$POLLINATIONS_API_KEY" ]]; then
  AUTH_HEADER="-H \"Authorization: Bearer $POLLINATIONS_API_KEY\""
fi

RESPONSE=$(curl -s -H "Content-Type: application/json" \
  ${POLLINATIONS_API_KEY:+-H "Authorization: Bearer $POLLINATIONS_API_KEY"} \
  -X POST "https://gen.pollinations.ai/v1/chat/completions" \
  -d "$BODY")

# Extract result
RESULT=$(echo "$RESPONSE" | jq -r '.choices[0].message.content // empty')

if [[ -n "$RESULT" ]]; then
  echo "$RESULT"
else
  echo "Error: Failed to analyze image"
  echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE"
  exit 1
fi
