#!/usr/bin/env bash
# gen_visuals.sh — Generate images or video clips for music video
# Usage: gen_visuals.sh --mode slideshow|video|hybrid [options]
#
# Image providers: openai (default), seedream, google-together
# Video providers: sora (default), seedance, veo
#
# Options:
#   --mode slideshow|video|hybrid
#   --prompts-file /path/to/prompts.json   (array of scene prompts)
#   --image-provider openai|google-together
#   --image-model gpt-image-1|gpt-image-1-mini  (default: gpt-image-1-mini)
#   --video-provider sora|sora-pro|seedance-lite|seedance-pro|veo-fast|veo-audio
#   --image-quality low|medium|high  (default: medium)
#   --image-size 1024x1024|1536x1024|1024x1536  (default: 1536x1024)
#   --outdir /path
#   --dry-run   (cost estimate only)
#
# Env: OPENAI_API_KEY, TOGETHER_API_KEY (optional, for google/seedance/veo)

set -euo pipefail

MODE="slideshow"
IMAGE_PROVIDER="openai"
IMAGE_MODEL="gpt-image-1-mini"
VIDEO_PROVIDER="sora"
IMAGE_QUALITY="medium"
IMAGE_SIZE="1536x1024"
OUTDIR="./output"
DRY_RUN=false
PROMPTS_FILE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode) MODE="$2"; shift 2 ;;
    --prompts-file) PROMPTS_FILE="$2"; shift 2 ;;
    --image-provider) IMAGE_PROVIDER="$2"; shift 2 ;;
    --image-model) IMAGE_MODEL="$2"; shift 2 ;;
    --video-provider) VIDEO_PROVIDER="$2"; shift 2 ;;
    --image-quality) IMAGE_QUALITY="$2"; shift 2 ;;
    --image-size) IMAGE_SIZE="$2"; shift 2 ;;
    --outdir) OUTDIR="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    *) echo "Unknown: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$PROMPTS_FILE" || ! -f "$PROMPTS_FILE" ]]; then
  echo "ERROR: --prompts-file required (JSON array of scene prompts)" >&2; exit 1
fi

mkdir -p "$OUTDIR/images" "$OUTDIR/videos"

# Count prompts
NUM_SCENES=$(python3 -c "import json, sys; print(len(json.load(open(sys.argv[1]))))" "$PROMPTS_FILE")
NUM_IMAGES=0
NUM_VIDEOS=0

case "$MODE" in
  slideshow) NUM_IMAGES=$NUM_SCENES ;;
  video) NUM_VIDEOS=$NUM_SCENES ;;
  hybrid)
    NUM_IMAGES=$((NUM_SCENES / 2))
    NUM_VIDEOS=$((NUM_SCENES - NUM_IMAGES))
    ;;
esac

# Token-based pricing (per 1M tokens, from OpenAI pricing page Feb 2026)
# Image cost = (text_input_tokens × text_rate + image_output_tokens × image_rate) / 1M
# Output tokens are FIXED per quality: low=272, medium=1056, high=4160
# Text input tokens are ~60-100 for typical prompts (negligible cost impact)
get_image_cost() {
  local provider="$1" quality="$2" size="$3"
  case "$provider" in
    openai)
      # Token-based calculation for OpenAI models
      # Output tokens by quality: low=272, medium=1056, high=4160
      # Size multiplier: 1024x1024=1x, 1536x1024/1024x1536=1.5x
      python3 -c "
model = '$IMAGE_MODEL'
quality = '$quality'
size = '$size'

# Image output token rates (per 1M tokens)
rates = {
    'gpt-image-1':      {'text_in': 5.00, 'img_out': 40.00},
    'gpt-image-1-mini': {'text_in': 2.00, 'img_out':  8.00},
}
# Output tokens by quality (measured empirically for 1024x1024)
output_tokens = {'low': 272, 'medium': 1056, 'high': 4160}
# Size multiplier for output tokens
size_mult = 1.5 if size != '1024x1024' else 1.0

r = rates.get(model, rates['gpt-image-1-mini'])
text_tokens = 80  # typical prompt, negligible
img_tokens = int(output_tokens.get(quality, 1056) * size_mult)

cost = (text_tokens * r['text_in'] + img_tokens * r['img_out']) / 1_000_000
print(f'{cost:.6f}')
" ;;
    seedream) echo "0.045" ;;  # BytePlus Seedream 4.5 ($0.045/image)
    google-together) echo "0.040" ;;  # Imagen 4.0 Preview
    *) echo "0.034" ;;
  esac
}

get_video_cost() {
  local provider="$1"
  case "$provider" in
    sora) echo "0.80" ;;
    sora-pro) echo "2.40" ;;
    seedance-lite) echo "0.14" ;;
    seedance-pro) echo "0.57" ;;
    veo-fast) echo "0.80" ;;
    veo-audio) echo "3.20" ;;
    *) echo "0.80" ;;
  esac
}

IMG_COST=$(get_image_cost "$IMAGE_PROVIDER" "$IMAGE_QUALITY" "$IMAGE_SIZE")
VID_COST=$(get_video_cost "$VIDEO_PROVIDER")
TOTAL_IMG=$(python3 -c "print(f'{$NUM_IMAGES * $IMG_COST:.2f}')")
TOTAL_VID=$(python3 -c "print(f'{$NUM_VIDEOS * $VID_COST:.2f}')")
TOTAL=$(python3 -c "print(f'{$NUM_IMAGES * $IMG_COST + $NUM_VIDEOS * $VID_COST:.2f}')")

echo "📊 Visual Generation Cost Estimate"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Mode: $MODE ($NUM_SCENES scenes)"
if [[ $NUM_IMAGES -gt 0 ]]; then
  echo "  🎨 Images: ${NUM_IMAGES}× $IMAGE_PROVIDER/$IMAGE_MODEL ($IMAGE_QUALITY, $IMAGE_SIZE)"
  echo "     Cost: ${NUM_IMAGES} × \$${IMG_COST} = \$${TOTAL_IMG}"
fi
if [[ $NUM_VIDEOS -gt 0 ]]; then
  echo "  🎬 Videos: ${NUM_VIDEOS}× $VIDEO_PROVIDER"
  echo "     Cost: ${NUM_VIDEOS} × \$${VID_COST} = \$${TOTAL_VID}"
fi
echo "  💰 Total: \$${TOTAL}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ "$DRY_RUN" = true ]]; then
  # Write estimate to JSON
  python3 -c "
import json
est = {
    'mode': '$MODE',
    'num_images': $NUM_IMAGES, 'num_videos': $NUM_VIDEOS,
    'image_provider': '$IMAGE_PROVIDER', 'image_model': '$IMAGE_MODEL',
    'video_provider': '$VIDEO_PROVIDER',
    'image_quality': '$IMAGE_QUALITY', 'image_size': '$IMAGE_SIZE',
    'image_cost_each': $IMG_COST, 'video_cost_each': $VID_COST,
    'total_image_cost': $TOTAL_IMG, 'total_video_cost': $TOTAL_VID,
    'total_cost': $TOTAL,
    'pricing_method': 'token-based'
}
with open('$OUTDIR/cost_estimate.json', 'w') as f:
    json.dump(est, f, indent=2)
print('Estimate saved to $OUTDIR/cost_estimate.json')
"
  exit 0
fi

# ── Generate images ──
generate_openai_image() {
  local prompt="$1" outpath="$2"
  # Write prompt to temp file for safe handling
  local pfile=$(mktemp)
  echo -n "$prompt" > "$pfile"
  local resp_file=$(mktemp)

  python3 -c "
import json
with open('$pfile') as f: p = f.read()
print(json.dumps({
    'model': '$IMAGE_MODEL',
    'prompt': p,
    'n': 1,
    'size': '$IMAGE_SIZE',
    'quality': '$IMAGE_QUALITY'
}, ensure_ascii=False))
" > "${resp_file}.body"

  curl -s -X POST "https://api.openai.com/v1/images/generations" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-Type: application/json" \
    -d @"${resp_file}.body" \
    -o "$resp_file"

  python3 -c "
import json, base64, sys
with open('$resp_file') as f:
    d = json.load(f)
if 'data' in d and len(d['data']) > 0:
    item = d['data'][0]
    if item.get('b64_json'):
        img = base64.b64decode(item['b64_json'])
        with open('$outpath', 'wb') as f:
            f.write(img)
        # Extract usage for actual cost tracking
        usage = d.get('usage', {})
        details = usage.get('input_tokens_details', {})
        text_in = details.get('text_tokens', 0)
        img_in = details.get('image_tokens', 0)
        img_out = usage.get('output_tokens', 0)
        # Calculate actual token-based cost
        rates = {
            'gpt-image-1':      {'text_in': 5.00, 'img_in': 10.00, 'img_out': 40.00},
            'gpt-image-1-mini': {'text_in': 2.00, 'img_in':  2.50, 'img_out':  8.00},
        }
        r = rates.get('$IMAGE_MODEL', rates['gpt-image-1-mini'])
        actual_cost = (text_in * r['text_in'] + img_in * r['img_in'] + img_out * r['img_out']) / 1_000_000
        # Save usage info alongside image
        usage_path = '$outpath'.replace('.png', '_usage.json')
        with open(usage_path, 'w') as uf:
            json.dump({
                'model': '$IMAGE_MODEL', 'quality': '$IMAGE_QUALITY', 'size': '$IMAGE_SIZE',
                'text_input_tokens': text_in, 'image_input_tokens': img_in,
                'output_tokens': img_out, 'actual_cost': actual_cost,
            }, uf, indent=2)
        print(f'OK|{actual_cost:.6f}|{img_out}')
    elif item.get('url'):
        import urllib.request
        urllib.request.urlretrieve(item['url'], '$outpath')
        print('OK|0|0')
    else:
        print('ERROR: no image data', file=sys.stderr)
        sys.exit(1)
elif 'error' in d:
    print(f'ERROR: {d[\"error\"][\"message\"]}', file=sys.stderr)
    sys.exit(1)
" && echo "  ✅ $(basename "$outpath")" || echo "  ❌ Image gen failed" >&2

  rm -f "$pfile" "$resp_file" "${resp_file}.body"
}

generate_seedream_image() {
  local prompt="$1" outpath="$2"
  if [[ -z "${BYTEPLUS_API_KEY:-}" ]]; then
    echo "ERROR: BYTEPLUS_API_KEY required for seedream provider" >&2; return 1
  fi
  local pfile=$(mktemp)
  echo -n "$prompt" > "$pfile"
  local resp_file=$(mktemp)

  python3 -c "
import json
with open('$pfile') as f: p = f.read()
print(json.dumps({
    'model': 'seedream-4-5-251128',
    'prompt': p,
    'size': '2048x2048',
    'response_format': 'url',
    'watermark': False
}, ensure_ascii=False))
" > "${resp_file}.body"

  curl -s -X POST "https://ark.ap-southeast.bytepluses.com/api/v3/images/generations" \
    -H "Authorization: Bearer $BYTEPLUS_API_KEY" \
    -H "Content-Type: application/json" \
    -d @"${resp_file}.body" \
    -o "$resp_file"

  python3 -c "
import json, urllib.request, sys
with open('$resp_file') as f:
    d = json.load(f)
if 'data' in d and len(d['data']) > 0:
    item = d['data'][0]
    if item.get('url'):
        urllib.request.urlretrieve(item['url'], '$outpath')
        usage = d.get('usage', {})
        imgs = usage.get('generated_images', 1)
        out_tokens = usage.get('output_tokens', 0)
        # Save usage
        usage_path = '$outpath'.replace('.png', '_usage.json')
        with open(usage_path, 'w') as uf:
            json.dump({
                'model': 'seedream-4-5-251128', 'provider': 'byteplus',
                'size': '2048x2048', 'output_tokens': out_tokens,
                'actual_cost': 0.045,
            }, uf, indent=2)
        print(f'OK|0.045000|{out_tokens}')
    else:
        print('ERROR: no url in response', file=sys.stderr)
        sys.exit(1)
elif 'error' in d:
    print(f'ERROR: {d[\"error\"][\"message\"]}', file=sys.stderr)
    sys.exit(1)
" && echo "  ✅ $(basename "$outpath")" || echo "  ❌ Seedream gen failed" >&2

  rm -f "$pfile" "$resp_file" "${resp_file}.body"
}

generate_together_image() {
  local prompt="$1" outpath="$2"
  if [[ -z "${TOGETHER_API_KEY:-}" ]]; then
    echo "ERROR: TOGETHER_API_KEY required for google-together provider" >&2; return 1
  fi
  local resp
  local pfile=$(mktemp)
  echo -n "$prompt" > "$pfile"
  local body_file=$(mktemp)
  python3 -c "
import json
with open('$pfile') as f: p = f.read()
print(json.dumps({
    'model': 'google/imagen-4.0-generate-preview',
    'prompt': p,
    'n': 1,
    'width': 1536, 'height': 1024
}, ensure_ascii=False))
" > "$body_file"
  resp=$(curl -s -X POST "https://api.together.xyz/v1/images/generations" \
    -H "Authorization: Bearer $TOGETHER_API_KEY" \
    -H "Content-Type: application/json" \
    -d @"$body_file")
  rm -f "$pfile" "$body_file"
  local url
  url=$(echo "$resp" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if 'data' in d and len(d['data']) > 0:
    print(d['data'][0].get('url',''))
else:
    print('ERROR', file=sys.stderr); sys.exit(1)
" 2>&1)
  if [[ -z "$url" || "$url" == ERROR* ]]; then
    echo "  ❌ Image gen failed" >&2; return 1
  fi
  curl -s -o "$outpath" "$url"
  echo "  ✅ $(basename "$outpath")"
}

# ── Generate videos ──
generate_video_together() {
  local prompt="$1" outpath="$2" model="$3"
  if [[ -z "${TOGETHER_API_KEY:-}" ]]; then
    echo "ERROR: TOGETHER_API_KEY required for $VIDEO_PROVIDER" >&2; return 1
  fi
  local resp
  local pfile=$(mktemp)
  echo -n "$prompt" > "$pfile"
  local body_file=$(mktemp)
  python3 -c "
import json
with open('$pfile') as f: p = f.read()
print(json.dumps({
    'model': '$model',
    'prompt': p,
}, ensure_ascii=False))
" > "$body_file"
  resp=$(curl -s -X POST "https://api.together.xyz/v2/videos" \
    -H "Authorization: Bearer $TOGETHER_API_KEY" \
    -H "Content-Type: application/json" \
    -d @"$body_file")
  rm -f "$pfile" "$body_file"
  local video_id
  video_id=$(echo "$resp" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)
  if [[ -z "$video_id" ]]; then
    echo "  ❌ Video gen failed: $resp" >&2; return 1
  fi
  # Poll
  echo "  ⏳ Video generating (id: $video_id)..."
  local status="processing"
  local attempts=0
  while [[ "$status" == "processing" || "$status" == "pending" ]]; do
    sleep 15
    attempts=$((attempts + 1))
    if [[ $attempts -ge 40 ]]; then
      echo "  ❌ Video timeout" >&2; return 1
    fi
    local poll
    poll=$(curl -s "https://api.together.xyz/v2/videos/${video_id}" \
      -H "Authorization: Bearer $TOGETHER_API_KEY")
    status=$(echo "$poll" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))" 2>/dev/null)
    echo "    [${attempts}] $status"
    if [[ "$status" == "completed" ]]; then
      local vid_url
      vid_url=$(echo "$poll" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('output',{}).get('video_url', d.get('result',{}).get('url','')))" 2>/dev/null)
      if [[ -n "$vid_url" ]]; then
        curl -s -o "$outpath" "$vid_url"
        echo "  ✅ $(basename "$outpath")"
        return 0
      fi
    elif [[ "$status" == "failed" ]]; then
      echo "  ❌ Video generation failed" >&2; return 1
    fi
  done
}

generate_sora_video() {
  local prompt="$1" outpath="$2" model_suffix="$3"
  local model="sora-2"
  [[ "$model_suffix" == "pro" ]] && model="sora-2-pro"
  if [[ -n "${TOGETHER_API_KEY:-}" ]]; then
    # Use Together AI for Sora
    local together_model="openai/${model}"
    generate_video_together "$prompt" "$outpath" "$together_model"
  elif [[ -n "${OPENAI_API_KEY:-}" ]]; then
    # Direct OpenAI (if supported)
    local resp
    local pfile=$(mktemp)
    echo -n "$prompt" > "$pfile"
    local body_file=$(mktemp)
    python3 -c "
import json
with open('$pfile') as f: p = f.read()
print(json.dumps({
    'model': '$model',
    'prompt': p,
}, ensure_ascii=False))
" > "$body_file"
    resp=$(curl -s -X POST "https://api.openai.com/v1/videos/generations" \
      -H "Authorization: Bearer $OPENAI_API_KEY" \
      -H "Content-Type: application/json" \
      -d @"$body_file")
    rm -f "$pfile" "$body_file"
    echo "  OpenAI direct response: $(echo "$resp" | head -c 200)"
    # TODO: handle OpenAI direct video response format
  fi
}

# ── Main generation loop ──
echo ""
echo "🎨 Generating visuals ($MODE mode)..."

VISUAL_IDX=0
IMAGE_IDX=0
VIDEO_IDX=0

python3 -c "
import json, sys
prompts = json.load(open(sys.argv[1]))
for i, p in enumerate(prompts):
    prompt = p if isinstance(p, str) else p.get('prompt','')
    ptype = p.get('type','') if isinstance(p, dict) else ''
    print(f'{i}|{ptype}|{prompt}')
" "$PROMPTS_FILE" | while IFS='|' read -r idx ptype prompt; do
  if [[ "$MODE" == "slideshow" ]] || \
     { [[ "$MODE" == "hybrid" ]] && { [[ "$ptype" == "image" ]] || { [[ -z "$ptype" ]] && [[ $IMAGE_IDX -lt $NUM_IMAGES ]]; }; }; }; then
    # Image
    FNAME="scene_$(printf '%03d' "$idx").png"
    echo ""
    echo "  [$((idx+1))/$NUM_SCENES] 🎨 Image: ${prompt:0:60}..."
    case "$IMAGE_PROVIDER" in
      openai) generate_openai_image "$prompt" "$OUTDIR/images/$FNAME" ;;
      seedream) generate_seedream_image "$prompt" "$OUTDIR/images/$FNAME" ;;
      google-together) generate_together_image "$prompt" "$OUTDIR/images/$FNAME" ;;
    esac
    IMAGE_IDX=$((IMAGE_IDX + 1))
  else
    # Video
    FNAME="scene_$(printf '%03d' "$idx").mp4"
    echo ""
    echo "  [$((idx+1))/$NUM_SCENES] 🎬 Video: ${prompt:0:60}..."
    case "$VIDEO_PROVIDER" in
      sora) generate_sora_video "$prompt" "$OUTDIR/videos/$FNAME" "" ;;
      sora-pro) generate_sora_video "$prompt" "$OUTDIR/videos/$FNAME" "pro" ;;
      seedance-lite) generate_video_together "$prompt" "$OUTDIR/videos/$FNAME" "ByteDance/Seedance-1.0-lite" ;;
      seedance-pro) generate_video_together "$prompt" "$OUTDIR/videos/$FNAME" "ByteDance/Seedance-1.0-pro" ;;
      veo-fast) generate_video_together "$prompt" "$OUTDIR/videos/$FNAME" "google/veo-3.0-generate-preview" ;;
      veo-audio) generate_video_together "$prompt" "$OUTDIR/videos/$FNAME" "google/veo-3.0-generate-preview" ;;
    esac
    VIDEO_IDX=$((VIDEO_IDX + 1))
  fi
done

# Write cost tracking
python3 -c "
import json, os, glob

outdir = '$OUTDIR'
images = sorted(glob.glob(os.path.join(outdir, 'images', 'scene_*.png')))
videos = sorted(glob.glob(os.path.join(outdir, 'videos', 'scene_*.mp4')))

# Load actual costs from usage files
actual_image_costs = []
for img_path in images:
    usage_path = img_path.replace('.png', '_usage.json')
    if os.path.exists(usage_path):
        with open(usage_path) as uf:
            u = json.load(uf)
            actual_image_costs.append({
                'file': img_path,
                'estimated_cost': $IMG_COST,
                'actual_cost': u.get('actual_cost', $IMG_COST),
                'output_tokens': u.get('output_tokens', 0),
                'model': u.get('model', '$IMAGE_MODEL'),
            })
    else:
        actual_image_costs.append({
            'file': img_path,
            'estimated_cost': $IMG_COST,
            'actual_cost': $IMG_COST,
            'output_tokens': 0,
            'model': '$IMAGE_MODEL',
        })

total_actual_img = sum(c['actual_cost'] for c in actual_image_costs)
total_est_img = len(images) * $IMG_COST

meta = {
    'mode': '$MODE',
    'image_provider': '$IMAGE_PROVIDER',
    'image_model': '$IMAGE_MODEL',
    'video_provider': '$VIDEO_PROVIDER',
    'pricing_method': 'token-based',
    'images': actual_image_costs,
    'videos': [{'file': f, 'cost': $VID_COST} for f in videos],
    'total_image_cost_estimated': total_est_img,
    'total_image_cost_actual': total_actual_img,
    'total_video_cost': len(videos) * $VID_COST,
    'total_cost_estimated': total_est_img + len(videos) * $VID_COST,
    'total_cost_actual': total_actual_img + len(videos) * $VID_COST,
}
with open(os.path.join(outdir, 'visuals_meta.json'), 'w') as f:
    json.dump(meta, f, indent=2, ensure_ascii=False)

print()
print('📊 Visual Generation Complete')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
print(f'  Model: {meta[\"image_model\"]}')
tic_est = meta['total_image_cost_estimated']
tic_act = meta['total_image_cost_actual']
tvc = meta['total_video_cost']
tc_est = meta['total_cost_estimated']
tc_act = meta['total_cost_actual']
print(f'  🎨 Images: {len(images)} (estimated \${tic_est:.4f} / actual \${tic_act:.4f})')
print(f'  🎬 Videos: {len(videos)} (\${tvc:.2f})')
print(f'  💰 Total estimated: \${tc_est:.4f}')
print(f'  💰 Total actual:    \${tc_act:.4f}')
if tic_est > 0:
    savings_pct = (1 - tic_act / tic_est) * 100
    print(f'  📐 Estimation accuracy: {savings_pct:+.1f}% vs estimate')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
"
