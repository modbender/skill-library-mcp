#!/usr/bin/env bash
# Smart Router — Call a specific model via OpenAI-compatible API
# Supports: chat (with optional vision), image generation, async tasks, TTS

set -euo pipefail

# ========== Config ==========
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
MODELS_JSON="$SKILL_DIR/models.json"

BASE_URL_ENV=$(jq -r '.provider.base_url_env // "SMART_ROUTER_BASE_URL"' "$MODELS_JSON")
API_KEY_ENV=$(jq -r '.provider.api_key_env // "SMART_ROUTER_API_KEY"' "$MODELS_JSON")

BASE_URL="${!BASE_URL_ENV:-}"
API_KEY="${!API_KEY_ENV:-}"

if [[ -z "$BASE_URL" ]]; then
  echo "Error: environment variable $BASE_URL_ENV is not set" >&2
  echo "Set it to your OpenAI-compatible API base URL (e.g. https://api.openai.com/v1)" >&2
  exit 1
fi

if [[ -z "$API_KEY" ]]; then
  echo "Error: environment variable $API_KEY_ENV is not set" >&2
  exit 1
fi

# ========== Args ==========
MODEL=""
PROMPT=""
TYPE="chat"
IMAGE_URL=""
SIZE="1024x1024"
VOICE="alloy"
MAX_TOKENS=4096
TEMPERATURE=0.7

usage() {
  cat <<EOF
Usage: call-model.sh --model <model_id> --prompt <prompt> [options]

Required:
  --model       Model ID
  --prompt      Prompt / task description

Optional:
  --type        Call type: chat (default) | image | async | tts
  --image       Image URL (for vision models)
  --size        Image size (default: 1024x1024)
  --voice       TTS voice (default: alloy)
  --max-tokens  Max output tokens (default: 4096)
  --temperature Temperature (default: 0.7)
EOF
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --model) MODEL="$2"; shift 2 ;;
    --prompt) PROMPT="$2"; shift 2 ;;
    --type) TYPE="$2"; shift 2 ;;
    --image) IMAGE_URL="$2"; shift 2 ;;
    --size) SIZE="$2"; shift 2 ;;
    --voice) VOICE="$2"; shift 2 ;;
    --max-tokens) MAX_TOKENS="$2"; shift 2 ;;
    --temperature) TEMPERATURE="$2"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; usage ;;
  esac
done

if [[ -z "$MODEL" || -z "$PROMPT" ]]; then
  echo "Error: --model and --prompt are required" >&2
  usage
fi

# ========== Functions ==========

call_chat() {
  local messages
  if [[ -n "$IMAGE_URL" ]]; then
    messages=$(jq -n --arg prompt "$PROMPT" --arg img "$IMAGE_URL" '[{
      "role": "user",
      "content": [
        {"type": "text", "text": $prompt},
        {"type": "image_url", "image_url": {"url": $img}}
      ]
    }]')
  else
    messages=$(jq -n --arg prompt "$PROMPT" '[{
      "role": "user",
      "content": $prompt
    }]')
  fi

  local body
  body=$(jq -n \
    --arg model "$MODEL" \
    --argjson messages "$messages" \
    --argjson max_tokens "$MAX_TOKENS" \
    --argjson temperature "$TEMPERATURE" \
    '{model: $model, messages: $messages, max_tokens: $max_tokens, temperature: $temperature}')

  local response
  response=$(curl -sS --max-time 120 "$BASE_URL/chat/completions" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "$body")

  local error
  error=$(echo "$response" | jq -r '.error.message // empty')
  if [[ -n "$error" ]]; then
    echo "API error: $error" >&2
    exit 1
  fi

  echo "$response" | jq -r '.choices[0].message.content // "(no response)"'
}

call_image() {
  local body
  body=$(jq -n \
    --arg model "$MODEL" \
    --arg prompt "$PROMPT" \
    --arg size "$SIZE" \
    '{model: $model, prompt: $prompt, size: $size, n: 1}')

  local response
  response=$(curl -sS --max-time 180 "$BASE_URL/images/generations" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "$body")

  local error
  error=$(echo "$response" | jq -r '.error.message // empty')
  if [[ -n "$error" ]]; then
    echo "API error: $error" >&2
    exit 1
  fi

  local url
  url=$(echo "$response" | jq -r '.data[0].url // empty')
  local b64
  b64=$(echo "$response" | jq -r '.data[0].b64_json // empty')

  if [[ -n "$url" ]]; then
    echo "$url"
  elif [[ -n "$b64" ]]; then
    local outfile="/tmp/smart-router-img-$(date +%s).png"
    echo "$b64" | base64 -d > "$outfile"
    echo "Image saved: $outfile"
  else
    echo "No image result returned" >&2
    echo "$response" | jq '.' >&2
    exit 1
  fi
}

call_async() {
  local body
  body=$(jq -n \
    --arg model "$MODEL" \
    --arg prompt "$PROMPT" \
    '{model: $model, messages: [{"role": "user", "content": $prompt}], stream: false}')

  local response
  response=$(curl -sS --max-time 300 "$BASE_URL/chat/completions" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "$body")

  local error
  error=$(echo "$response" | jq -r '.error.message // empty')
  if [[ -n "$error" ]]; then
    echo "API error: $error" >&2
    exit 1
  fi

  local content
  content=$(echo "$response" | jq -r '.choices[0].message.content // empty')
  if [[ -n "$content" ]]; then
    echo "$content"
  else
    echo "$response" | jq '.'
  fi
}

call_tts() {
  local body
  body=$(jq -n \
    --arg model "$MODEL" \
    --arg input "$PROMPT" \
    --arg voice "$VOICE" \
    '{model: $model, input: $input, voice: $voice}')

  local outfile="/tmp/smart-router-tts-$(date +%s).mp3"

  curl -sS --max-time 120 "$BASE_URL/audio/speech" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "$body" \
    -o "$outfile"

  if [[ -s "$outfile" ]]; then
    echo "Audio saved: $outfile"
  else
    echo "TTS generation failed" >&2
    rm -f "$outfile"
    exit 1
  fi
}

# ========== Execute ==========
case "$TYPE" in
  chat)  call_chat ;;
  image) call_image ;;
  async) call_async ;;
  tts)   call_tts ;;
  *)     echo "Unknown type: $TYPE (supported: chat, image, async, tts)" >&2; exit 1 ;;
esac
