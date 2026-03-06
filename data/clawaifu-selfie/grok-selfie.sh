#!/bin/bash
# grok-selfie.sh - Grok Imagine Edit로 셀카 생성 후 텔레그램 전송
# 보안: 모든 credential은 환경 변수로만 받음

set -euo pipefail

# 환경 변수 확인 (필수)
if [ -z "${FAL_KEY:-}" ]; then
    echo "Error: FAL_KEY environment variable required"
    exit 1
fi

if [ -z "${BOT_TOKEN:-}" ]; then
    echo "Error: BOT_TOKEN environment variable required"
    exit 1
fi

# 설정
REFERENCE_IMAGE="${REFERENCE_IMAGE:-https://i.redd.it/g4uf70te81uf1.jpeg}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-}"

if [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo "Error: TELEGRAM_CHAT_ID environment variable required"
    exit 1
fi

# 인자 파싱
USER_CONTEXT="${1:-}"
MODE="${2:-mirror}"
CAPTION="${3:-}"

if [ -z "$USER_CONTEXT" ]; then
    echo "Usage: $0 <user_context> [mirror|direct] [caption]"
    exit 1
fi

# 캐릭터 스타일 (레제, 애니메이션)
CHARACTER="Reze from Chainsaw Man"
STYLE="anime style, 2D animation, cel shading, vibrant colors"
FACE="keep same eye shape as reference image with slightly more angular upper eyelids, green eyes, thin line mouth, subtle smile with closed lips"
OUTFIT="wearing outfit appropriate for the situation, always wearing black choker on neck"

NOPHONE="no phone visible in frame, no hands holding phone"

if [ "$MODE" == "direct" ]; then
    PROMPT="$CHARACTER, $STYLE, $FACE, $OUTFIT, selfie photo style, close-up shot at $USER_CONTEXT, direct eye contact with camera, face fully visible, $NOPHONE"
else
    PROMPT="$CHARACTER, $STYLE, $FACE, $OUTFIT, mirror selfie photo style, $USER_CONTEXT, $NOPHONE"
fi

# Grok Imagine Edit API 호출 (jq로 안전한 JSON 생성)
JSON_PAYLOAD=$(jq -n \
  --arg image_url "$REFERENCE_IMAGE" \
  --arg prompt "$PROMPT" \
  '{image_url: $image_url, prompt: $prompt, num_images: 1, output_format: "jpeg"}')

RESPONSE=$(curl -s -X POST "https://fal.run/xai/grok-imagine-image/edit" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d "$JSON_PAYLOAD")

# 이미지 URL 추출
IMAGE_URL=$(echo "$RESPONSE" | jq -r '.images[0].url // empty')

if [ -z "$IMAGE_URL" ]; then
    echo "Error: Failed to generate image"
    echo "Response: $RESPONSE"
    exit 1
fi

# 텔레그램으로 전송 (curl -F는 form data로 안전하게 전송)
if [ -n "$CAPTION" ]; then
    curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendPhoto" \
      -F "chat_id=$TELEGRAM_CHAT_ID" \
      -F "photo=$IMAGE_URL" \
      -F "caption=$CAPTION" > /dev/null 2>&1
else
    curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendPhoto" \
      -F "chat_id=$TELEGRAM_CHAT_ID" \
      -F "photo=$IMAGE_URL" > /dev/null 2>&1
fi

echo "Done! Image: $IMAGE_URL"
