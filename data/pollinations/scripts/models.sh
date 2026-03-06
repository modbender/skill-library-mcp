#!/bin/bash
# Pollinations Model Listing
# Usage: ./models.sh [--type text|image|audio|vision|video]

set -e

TYPE="${1:-all}"

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --type)
      TYPE="$2"
      shift 2
      ;;
    text|image|audio|vision|video|all)
      TYPE="$1"
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

fetch_text_models() {
  local data
  data=$(curl -s "https://gen.pollinations.ai/v1/models")
  # Handle both array format and {data: [...]} format
  echo "$data" | jq -r 'if type == "array" then .[].id else .data[].id end' 2>/dev/null
}

fetch_image_models() {
  curl -s "https://gen.pollinations.ai/image/models" | jq -r '.[] | (.id // .name)' 2>/dev/null
}

fetch_vision_models() {
  local data
  data=$(curl -s "https://gen.pollinations.ai/text/models")
  echo "$data" | jq -r '.[] | select(.input_modalities? // [] | index("image")) | (.id // .name)' 2>/dev/null
  # Fallback if jq filter returns nothing
  if [[ -z "$(echo "$data" | jq -r '.[] | select(.input_modalities? // [] | index("image")) | (.id // .name)' 2>/dev/null)" ]]; then
    echo "gemini"
    echo "gemini-large"
    echo "claude"
    echo "openai"
  fi
}

case "$TYPE" in
  text)
    echo "=== Text/Chat Models ==="
    fetch_text_models
    ;;
  image)
    echo "=== Image Models ==="
    fetch_image_models
    ;;
  video)
    echo "=== Video Models ==="
    curl -s "https://gen.pollinations.ai/image/models" | jq -r '.[] | select(.output_modalities? // [] | index("video")) | (.id // .name)' 2>/dev/null
    # Fallback
    if [[ -z "$(curl -s "https://gen.pollinations.ai/image/models" | jq -r '.[] | select(.output_modalities? // [] | index("video")) | (.id // .name)' 2>/dev/null)" ]]; then
      echo "veo"
      echo "seedance"
    fi
    ;;
  audio)
    echo "=== Audio/TTS Models ==="
    echo "openai-audio"
    ;;
  vision)
    echo "=== Vision Models (image analysis) ==="
    fetch_vision_models
    ;;
  all)
    echo "=== Text/Chat Models ==="
    fetch_text_models
    echo ""
    echo "=== Image Models ==="
    fetch_image_models
    echo ""
    echo "=== Video Models ==="
    echo "veo"
    echo "seedance"
    echo ""
    echo "=== Audio/TTS ==="
    echo "openai-audio"
    echo ""
    echo "=== Vision Models ==="
    fetch_vision_models
    ;;
  *)
    echo "Usage: models.sh [--type text|image|audio|vision|video|all]"
    exit 1
    ;;
esac
