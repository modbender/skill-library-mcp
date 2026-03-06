#!/usr/bin/env bash
# Smart Router — List available models from your provider
# Helps discover models to add to models.json

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
MODELS_JSON="$SKILL_DIR/models.json"

BASE_URL_ENV=$(jq -r '.provider.base_url_env // "SMART_ROUTER_BASE_URL"' "$MODELS_JSON")
API_KEY_ENV=$(jq -r '.provider.api_key_env // "SMART_ROUTER_API_KEY"' "$MODELS_JSON")

BASE_URL="${!BASE_URL_ENV:-}"
API_KEY="${!API_KEY_ENV:-}"

if [[ -z "$BASE_URL" ]]; then
  echo "Error: environment variable $BASE_URL_ENV is not set" >&2
  exit 1
fi

if [[ -z "$API_KEY" ]]; then
  echo "Error: environment variable $API_KEY_ENV is not set" >&2
  exit 1
fi

echo "Fetching models from $BASE_URL ..."

response=$(curl -sS --max-time 30 "$BASE_URL/models" \
  -H "Authorization: Bearer $API_KEY")

error=$(echo "$response" | jq -r '.error.message // empty')
if [[ -n "$error" ]]; then
  echo "API error: $error" >&2
  exit 1
fi

total=$(echo "$response" | jq '.data | length')
echo "Found $total models"
echo ""

# Categorize by keywords
declare -A keywords
keywords[vision]="vision|vl-|visual"
keywords[image]="imagen|flux|dall-e|stable-diffusion|midjourney|gpt-image"
keywords[video]="sora|veo|vidu|kling-video|runway|gen-4"
keywords[audio]="suno|tts|audio|music|speech"
keywords[reasoning]="o1|o3|o4|r1|thinking|reason"
keywords[code]="codex|coder|code"

for category in vision image video audio reasoning code; do
  pattern="${keywords[$category]}"
  echo "=== $category ==="
  echo "$response" | jq -r --arg p "$pattern" \
    '[.data[].id | select(test($p; "i"))] | sort | .[]' 2>/dev/null || true
  echo ""
done

echo "=== All models (first 50) ==="
echo "$response" | jq -r '[.data[].id] | sort | .[:50] | .[]'

if [[ "$total" -gt 50 ]]; then
  echo "... and $((total - 50)) more"
fi

echo ""
echo "Full list saved to /tmp/smart-router-models.json"
echo "$response" | jq '.data | sort_by(.id)' > /tmp/smart-router-models.json
