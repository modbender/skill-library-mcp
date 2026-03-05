#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_PREFIX="[xhs-image]"

log_info() { echo "${LOG_PREFIX} $1" >&2; }
log_error() { echo "${LOG_PREFIX} ERROR: $1" >&2; }

usage() {
  cat <<'USAGE'
Usage: xhs-image.sh --mode generate|edit --prompt PROMPT [options]
       xhs-image.sh --mode edit --base-image PATH --prompt PROMPT [options]

Options:
  --mode MODE            generate (text-to-image) or edit (image-to-image)
  --prompt TEXT          prompt text for generation / editing
  --base-image PATH      base image path (required for edit mode)
  --provider NAME        google (nano-banana) | seed (bytedance seed), default: google
  --seed NUMBER          random seed (optional)
  --ratio RATIO          aspect ratio, e.g. 1:1 (default), 3:4, 4:3, 9:16, 16:9
  --output PATH          output file path (default: /tmp/xhs-image-<timestamp>.png)

Environment variables:
  Google nano banana (openai-compatible gateway expected)
    GOOGLE_API_KEY       required
    GOOGLE_API_BASE      optional, default: https://generativelanguage.googleapis.com/openai
    GOOGLE_IMAGE_MODEL   optional, default: gemini-3.1-flash-image-preview

  ByteDance Seed (openai-compatible gateway expected)
    SEED_API_KEY         required
    SEED_API_BASE        optional, default: https://seed.bytedanceapi.com
    SEED_IMAGE_MODEL     optional, default: bytedance/seed-v1

Dependencies: curl, jq, base64

The script expects the provider gateways to expose OpenAI-compatible endpoints:
  POST $BASE/v1/images/generations  (text-to-image, JSON)
  POST $BASE/v1/images/edits        (image editing, multipart form)
USAGE
}

MODE=""
PROMPT=""
BASE_IMAGE=""
PROVIDER="google"
SEED_VALUE=""
RATIO="1:1"
OUTPUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode) MODE="$2"; shift 2;;
    --prompt|-p) PROMPT="$2"; shift 2;;
    --base-image|-b) BASE_IMAGE="$2"; shift 2;;
    --provider) PROVIDER="$2"; shift 2;;
    --seed) SEED_VALUE="$2"; shift 2;;
    --ratio) RATIO="$2"; shift 2;;
    --output|-o) OUTPUT="$2"; shift 2;;
    --help|-h) usage; exit 0;;
    *) log_error "Unknown argument: $1"; usage; exit 1;;
  esac
done

if [[ -z "$MODE" ]]; then
  log_error "--mode is required"
  usage
  exit 1
fi
if [[ -z "$PROMPT" ]]; then
  log_error "--prompt is required"
  usage
  exit 1
fi
if [[ "$MODE" == "edit" && -z "$BASE_IMAGE" ]]; then
  log_error "--base-image is required for edit mode"
  usage
  exit 1
fi
if [[ "$MODE" != "generate" && "$MODE" != "edit" ]]; then
  log_error "Invalid mode: $MODE"
  usage
  exit 1
fi

case "$RATIO" in
  1:1) SIZE="1024x1024" ;;
  3:4) SIZE="1024x1365" ;;
  4:3) SIZE="1365x1024" ;;
  9:16) SIZE="1024x1820" ;;
  16:9) SIZE="1820x1024" ;;
  *) log_error "Unsupported ratio: $RATIO"; exit 1;;
esac

case "$PROVIDER" in
  google)
    API_KEY="${GOOGLE_API_KEY:-${GEMINI_API_KEY:-}}"
    API_BASE="${GOOGLE_API_BASE:-${GEMINI_API_BASE:-https://generativelanguage.googleapis.com/openai}}"
    MODEL="${GOOGLE_IMAGE_MODEL:-${GEMINI_IMAGE_MODEL:-gemini-3.1-flash-image-preview}}"
    ;;
  seed)
    API_KEY="${SEED_API_KEY:-}"
    API_BASE="${SEED_API_BASE:-https://seed.bytedanceapi.com}"
    MODEL="${SEED_IMAGE_MODEL:-bytedance/seed-v1}"
    ;;
  *)
    log_error "Unknown provider: $PROVIDER"
    exit 1
    ;;
esac

if [[ -z "$API_KEY" ]]; then
  log_error "API key not set for provider $PROVIDER"
  exit 1
fi

OUTPUT_PATH="${OUTPUT:-$(mktemp /tmp/xhs-image-XXXX.png)}"
ENDPOINT_BASE="${API_BASE%/}"

OUTPUT_DIR="$(dirname "$OUTPUT_PATH")"
if [[ ! -d "$OUTPUT_DIR" ]]; then
  mkdir -p "$OUTPUT_DIR" || {
    log_error "Failed to create output directory: $OUTPUT_DIR"
    exit 1
  }
fi

if ! command -v jq >/dev/null; then
  log_error "jq is required"
  exit 1
fi
if ! command -v curl >/dev/null; then
  log_error "curl is required"
  exit 1
fi

perform_generate() {
  local payload
  payload=$(jq -n \
    --arg model "$MODEL" \
    --arg prompt "$PROMPT" \
    --arg size "$SIZE" \
    --arg mode "$MODE" \
    --arg seed "$SEED_VALUE" \
    '{model: $model, prompt: $prompt, size: $size, n: 1} | if $seed != "" then .seed = ($seed|tonumber) else . end')

  local response
  response=$(curl -sS -X POST "${ENDPOINT_BASE}/v1/images/generations" \
    -H "Authorization: Bearer ${API_KEY}" \
    -H "Content-Type: application/json" \
    -d "$payload") || {
      log_error "Request failed"; exit 1; }

  local b64
  b64=$(echo "$response" | jq -r '.data[0].b64_json // empty')
  if [[ -z "$b64" ]]; then
    log_error "Failed to parse image data. Raw response:\n$response"
    exit 1
  fi
  echo "$b64" | base64 --decode >"$OUTPUT_PATH"
}

perform_edit() {
  local args=(
    -sS -X POST "${ENDPOINT_BASE}/v1/images/edits"
    -H "Authorization: Bearer ${API_KEY}"
    -F "model=${MODEL}"
    -F "prompt=${PROMPT}"
    -F "size=${SIZE}"
    -F "image=@${BASE_IMAGE}"
  )
  if [[ -n "$SEED_VALUE" ]]; then
    args+=( -F "seed=${SEED_VALUE}" )
  fi
  local response
  response=$(curl "${args[@]}") || {
      log_error "Request failed"; exit 1; }
  local b64
  b64=$(echo "$response" | jq -r '.data[0].b64_json // empty')
  if [[ -z "$b64" ]]; then
    log_error "Failed to parse image data. Raw response:\n$response"
    exit 1
  fi
  echo "$b64" | base64 --decode >"$OUTPUT_PATH"
}

case "$MODE" in
  generate)
    log_info "Generating image via ${PROVIDER} (${MODEL}) size ${SIZE}"
    perform_generate
    ;;
  edit)
    log_info "Editing image via ${PROVIDER} (${MODEL}) size ${SIZE}"
    perform_edit
    ;;
  *)
    log_error "Unsupported mode: ${MODE}"
    exit 1
    ;;
esac

log_info "Image saved to ${OUTPUT_PATH}"

jq -n \
  --arg success "true" \
  --arg mode "$MODE" \
  --arg provider "$PROVIDER" \
  --arg prompt "$PROMPT" \
  --arg base_image "$BASE_IMAGE" \
  --arg ratio "$RATIO" \
  --arg output "$OUTPUT_PATH" \
  '{success: ($success == "true"), mode: $mode, provider: $provider, prompt: $prompt, base_image: ($base_image // null), ratio: $ratio, output_path: $output}'
