#!/usr/bin/env bash
set -euo pipefail

# 主题自动生图文（豆包API）-> 小红书CDP预填（不点发布）

TOPIC=""
TONE="A"
AUDIENCE=""
COUNT=3
REALISTIC="不要"
IMG_DESC=""
STYLE="A"
ACCOUNT=""
PORT="9222"
HOST="127.0.0.1"
AUTO_PREFILL="要"
OUT_BASE="$HOME/.openclaw/workspace/output/social-push-auto-api"
BASE_URL="https://ark.cn-beijing.volces.com/api/v3"
MODEL="doubao-seedream-5-0-260128"
API_KEY_ENV="DOUBAO_API_KEY"

usage(){
cat <<EOF
Usage:
  bash $0 --topic "主题" --audience "目标人群" [--tone A|B|C] [--count 3]
          [--image-desc "图片描述"] [--realistic 要|不要]
          [--style A|B|C] [--account xxx] [--host 127.0.0.1] [--port 9222]
          [--base-url URL] [--model MODEL] [--api-key-env DOUBAO_API_KEY]
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --topic) TOPIC="$2"; shift 2;;
    --tone) TONE="$2"; shift 2;;
    --audience) AUDIENCE="$2"; shift 2;;
    --count) COUNT="$2"; shift 2;;
    --realistic) REALISTIC="$2"; shift 2;;
    --image-desc) IMG_DESC="$2"; shift 2;;
    --style) STYLE="$2"; shift 2;;
    --account) ACCOUNT="$2"; shift 2;;
    --host) HOST="$2"; shift 2;;
    --port) PORT="$2"; shift 2;;
    --base-url) BASE_URL="$2"; shift 2;;
    --model) MODEL="$2"; shift 2;;
    --api-key-env) API_KEY_ENV="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 2;;
  esac
done

[[ -n "$TOPIC" && -n "$AUDIENCE" ]] || { usage; exit 2; }

TS=$(date +%Y%m%d-%H%M%S)
OUT="$OUT_BASE/$TS"
mkdir -p "$OUT"

case "$TONE" in
  A) TONE_TEXT="干货";;
  B) TONE_TEXT="种草";;
  C) TONE_TEXT="故事";;
  *) TONE_TEXT="干货";;
esac

case "$STYLE" in
  A) STYLE_TEXT="稳妥";;
  B) STYLE_TEXT="干货";;
  C) STYLE_TEXT="故事";;
  *) STYLE_TEXT="稳妥";;
esac

REAL_RULE="避免真人脸"
[[ "$REALISTIC" == "要" ]] && REAL_RULE="可出现真人但不要清晰可识别脸部"

PROMPT="为小红书图文生成科技感视觉海报，竖版，适合中文内容。主题：${TOPIC}。目标人群：${AUDIENCE}。调性：${TONE_TEXT}。要求：高质感、现代科技、简洁构图、可读性强、留出标题留白区域。${REAL_RULE}。禁止水印、禁止logo、禁止乱码文字。补充描述：${IMG_DESC}"

echo "[topic-auto-api] Step1 生成图片..."
PY_GEN="$HOME/.openclaw/workspace/skills/social-push-semi/scripts/generate_images_doubao.py"
IMAGES_JSON=$(python3 "$PY_GEN" --base-url "$BASE_URL" --model "$MODEL" --prompt "$PROMPT" --out-dir "$OUT" --count "$COUNT" --api-key-env "$API_KEY_ENV")
echo "$IMAGES_JSON" > "$OUT/images.json"

cat > "$OUT/content.txt" <<EOF
${AUDIENCE}向｜${TOPIC}（${TONE_TEXT}版）

这套流程把“选题-生图-文案-发布预填”串成一条线：
- 按主题自动生成配图
- 生成可直接发布的文案和标签
- 自动预填到待发布页，最后人工确认

建议：先从半自动跑通，稳定后再做批量。

#OpenClaw #自动发文 #AI效率 #${AUDIENCE}成长 #小红书运营
EOF

TITLE="${AUDIENCE}也能上手的 ${TOPIC}"

IMG_PATHS=()
while IFS= read -r line; do
  [[ -n "$line" ]] && IMG_PATHS+=("$line")
done < <(python3 - <<'PY' "$OUT/images.json"
import json,sys
obj=json.load(open(sys.argv[1],'r',encoding='utf-8'))
for p in obj.get('images',[]):
    print(p)
PY
)

XHS_PY="$HOME/.openclaw/workspace/skills/social-push-semi/vendor/xhs/.venv/bin/python"
[[ -x "$XHS_PY" ]] || { echo "Missing vendor xhs venv python, run: bash $HOME/.openclaw/workspace/skills/social-push-semi/scripts/setup_vendor_xhs.sh"; exit 3; }

echo "[topic-auto-api] Step2 预填到小红书待发布..."
if [[ -n "$ACCOUNT" ]]; then
  "$XHS_PY" "$HOME/.openclaw/workspace/skills/social-push-semi/vendor/xhs/scripts/publish_pipeline.py" \
    --host "$HOST" --port "$PORT" \
    --preview --reuse-existing-tab \
    --account "$ACCOUNT" \
    --title "$TITLE" \
    --content-file "$OUT/content.txt" \
    --images "${IMG_PATHS[@]}"
else
  "$XHS_PY" "$HOME/.openclaw/workspace/skills/social-push-semi/vendor/xhs/scripts/publish_pipeline.py" \
    --host "$HOST" --port "$PORT" \
    --preview --reuse-existing-tab \
    --title "$TITLE" \
    --content-file "$OUT/content.txt" \
    --images "${IMG_PATHS[@]}"
fi

cat > "$OUT/meta.json" <<EOF
{
  "topic": "$TOPIC",
  "tone": "$TONE_TEXT",
  "audience": "$AUDIENCE",
  "image_count": $COUNT,
  "image_desc": "${IMG_DESC}",
  "style": "$STYLE_TEXT",
  "provider": "doubao",
  "model": "$MODEL"
}
EOF

echo "[topic-auto-api] Done: $OUT"
