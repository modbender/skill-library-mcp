#!/bin/bash
# 小红书封面图生成脚本
# 功能：AI生成主题图片（上半部分3:2）+ 标题文字纯色底（下半部分3:2）→ 拼接为3:4封面图
# 支持多种生图 API：Google Gemini（默认）、OpenAI / OpenAI 兼容 API、腾讯云混元生图（AIART）
#
# 用法:
#   bash cover.sh "标题文字" "AI图片生成prompt" [输出路径] [底色] [字色]
#   bash cover.sh "标题文字" "__USER_IMAGE__:/path/to/img" [输出路径] [底色] [字色]
#
# 参数:
#   $1 - 标题文字（必填）
#   $2 - AI图片prompt 或 __USER_IMAGE__:/path/to/image（必填）
#        以 __USER_IMAGE__: 开头时跳过AI生成，直接使用用户提供的图片
#   $3 - 输出路径（可选，默认 /tmp/xhs_cover.png）
#   $4 - 标题区底色（可选，默认 #FFFFFF）
#   $5 - 标题字色（可选，默认 #1A1A1A）
#
# 环境变量（生图 API 配置）:
#   IMG_API_TYPE    - API 类型: "gemini"（默认）| "openai" | "hunyuan"
#
#   Gemini 模式:
#     GEMINI_API_KEY  - Google Gemini API Key（必须设置）
#     XHS_IMG_MODEL   - 模型名称（默认 gemini-2.5-flash-image）
#
#   OpenAI 兼容模式:
#     IMG_API_KEY     - API Key（必须设置）
#     IMG_API_BASE    - API Base URL（默认 https://api.openai.com/v1）
#     IMG_MODEL       - 模型名称（默认 dall-e-3）
#
#   腾讯云混元生图（AIART）模式:
#     HUNYUAN_SECRET_ID   - 腾讯云 SecretId（必须设置）
#     HUNYUAN_SECRET_KEY  - 腾讯云 SecretKey（必须设置）
#     HUNYUAN_REGION      - 地域（默认 ap-guangzhou）
#     HUNYUAN_ENDPOINT    - 请求域名（默认 aiart.tencentcloudapi.com）
#     HUNYUAN_RSP_TYPE    - 返回类型 url|base64（默认 url）
#
# 最终封面尺寸: 1080x1440 (3:4)
#   上半部分: 1080x720 (3:2) AI生成图片
#   下半部分: 1080x720 (3:2) 纯色底+标题文字

set -e

TITLE="${1:-}"
PROMPT="${2:-}"
OUTPUT="${3:-/tmp/xhs_cover.png}"
BG_COLOR="${4:-#FFFFFF}"
TEXT_COLOR="${5:-#1A1A1A}"

# 生图 API 配置（支持 gemini / openai / hunyuan 三种模式）
IMG_API_TYPE="${IMG_API_TYPE:-gemini}"

# Gemini 配置
GEMINI_API_KEY="${GEMINI_API_KEY:-}"
GEMINI_MODEL="${XHS_IMG_MODEL:-gemini-2.5-flash-image}"
GEMINI_API_URL="https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent"

# OpenAI 兼容配置
IMG_API_KEY="${IMG_API_KEY:-}"
IMG_API_BASE="${IMG_API_BASE:-https://api.openai.com/v1}"
IMG_MODEL="${IMG_MODEL:-dall-e-3}"

# 腾讯云混元生图（AIART）配置
HUNYUAN_SECRET_ID="${HUNYUAN_SECRET_ID:-}"
HUNYUAN_SECRET_KEY="${HUNYUAN_SECRET_KEY:-}"
HUNYUAN_REGION="${HUNYUAN_REGION:-ap-guangzhou}"
HUNYUAN_ENDPOINT="${HUNYUAN_ENDPOINT:-aiart.tencentcloudapi.com}"
HUNYUAN_RSP_TYPE="${HUNYUAN_RSP_TYPE:-url}"  # url | base64

# 尺寸定义
COVER_W=1080
COVER_H=1440
TOP_W=1080
TOP_H=720
BOT_W=1080
BOT_H=720

# 临时文件
TMP_DIR=$(mktemp -d)
AI_IMG="${TMP_DIR}/ai_raw.png"
AI_RESIZED="${TMP_DIR}/ai_top.png"
TITLE_IMG="${TMP_DIR}/title_bot.png"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

# ==================== 参数检查 ====================

if [ -z "$TITLE" ]; then
  echo "❌ 错误: 请提供标题文字"
  echo "用法: bash $0 \"标题文字\" \"AI图片prompt\" [输出路径] [底色] [字色]"
  exit 1
fi

if [ -z "$PROMPT" ]; then
  echo "❌ 错误: 请提供AI图片prompt或用户图片路径（__USER_IMAGE__:/path/to/img）"
  echo "用法: bash $0 \"标题文字\" \"AI图片prompt\" [输出路径] [底色] [字色]"
  echo "   或: bash $0 \"标题文字\" \"__USER_IMAGE__:/path/to/img\" [输出路径] [底色] [字色]"
  exit 1
fi

# 判断是用户上传图片还是AI生成
USER_IMAGE_MODE=false
USER_IMAGE_PATH=""
if [[ "$PROMPT" == __USER_IMAGE__:* ]]; then
  USER_IMAGE_MODE=true
  USER_IMAGE_PATH="${PROMPT#__USER_IMAGE__:}"
  if [ ! -f "$USER_IMAGE_PATH" ]; then
    echo "❌ 错误: 用户图片不存在: $USER_IMAGE_PATH"
    exit 1
  fi
fi

if [ "$USER_IMAGE_MODE" = false ]; then
  if [ "$IMG_API_TYPE" = "gemini" ] && [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ 错误: Gemini 模式下未设置 GEMINI_API_KEY 环境变量"
    echo "请先设置: export GEMINI_API_KEY=\"your-api-key\""
    echo "获取地址: https://aistudio.google.com/apikey"
    echo "或切换为 OpenAI 模式: export IMG_API_TYPE=openai IMG_API_KEY=xxx"
    echo "或切换为 混元 模式: export IMG_API_TYPE=hunyuan HUNYUAN_SECRET_ID=xxx HUNYUAN_SECRET_KEY=xxx"
    exit 1
  elif [ "$IMG_API_TYPE" = "openai" ] && [ -z "$IMG_API_KEY" ]; then
    echo "❌ 错误: OpenAI 模式下未设置 IMG_API_KEY 环境变量"
    echo "请先设置: export IMG_API_KEY=\"your-api-key\" IMG_API_BASE=\"https://api.openai.com/v1\""
    exit 1
  elif [ "$IMG_API_TYPE" = "hunyuan" ] && { [ -z "$HUNYUAN_SECRET_ID" ] || [ -z "$HUNYUAN_SECRET_KEY" ]; }; then
    echo "❌ 错误: 混元模式下未设置 HUNYUAN_SECRET_ID / HUNYUAN_SECRET_KEY 环境变量"
    echo "请先设置: export IMG_API_TYPE=hunyuan HUNYUAN_SECRET_ID=\"AKID...\" HUNYUAN_SECRET_KEY=\"...\""
    exit 1
  fi
fi

# 检查 ImageMagick
if ! command -v magick &> /dev/null && ! command -v convert &> /dev/null; then
  echo "❌ 错误: 未安装 ImageMagick，请先执行: apt install -y imagemagick"
  exit 1
fi

# 确定 ImageMagick 命令
if command -v magick &> /dev/null; then
  MAGICK="magick"
else
  MAGICK="convert"
fi

echo "🎨 开始生成小红书封面图..."
echo "   标题: ${TITLE}"
if [ "$USER_IMAGE_MODE" = true ]; then
  echo "   模式: 用户上传图片"
  echo "   图片: ${USER_IMAGE_PATH}"
else
  echo "   模式: AI生成图片 (${IMG_API_TYPE})"
  echo "   Prompt: ${PROMPT:0:80}..."
fi
echo "   输出: ${OUTPUT}"
echo "   底色: ${BG_COLOR} | 字色: ${TEXT_COLOR}"
echo ""

# ==================== 第1步：获取主题图片 ====================

if [ "$USER_IMAGE_MODE" = true ]; then
  echo "🔄 [1/3] 使用用户上传的图片..."
  cp "$USER_IMAGE_PATH" "$AI_IMG"
  if [ ! -s "$AI_IMG" ]; then
    echo "❌ 复制用户图片失败"
    exit 1
  fi
  echo "   ✅ 用户图片加载成功"
else
  echo "🔄 [1/3] 调用 ${IMG_API_TYPE} API 生成主题图片..."

  if [ "$IMG_API_TYPE" = "openai" ]; then
    echo "   模型: ${IMG_MODEL} (OpenAI兼容)"
    echo "   Base: ${IMG_API_BASE}"

    # OpenAI / OpenAI兼容 API 生图
    PROMPT_ESCAPED=$(echo "$PROMPT" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))")

    RESPONSE_FILE="${TMP_DIR}/openai_response.json"

    curl -s -X POST "${IMG_API_BASE}/images/generations" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer ${IMG_API_KEY}" \
      -d "{\"model\": \"${IMG_MODEL}\", \"prompt\": ${PROMPT_ESCAPED}, \"n\": 1, \"size\": \"1536x1024\", \"response_format\": \"b64_json\"}" \
      -o "$RESPONSE_FILE"

    # 提取 base64 图片
    EXTRACT_PY="${TMP_DIR}/extract_openai.py"
    cat > "$EXTRACT_PY" << 'PYEOF'
import sys, json, base64

response_file = sys.argv[1]
output_file = sys.argv[2]

with open(response_file, "r") as f:
    data = json.load(f)

# OpenAI 格式: {"data": [{"b64_json": "..."}]}
img_data = data.get("data", [])
if img_data and "b64_json" in img_data[0]:
    img_bytes = base64.b64decode(img_data[0]["b64_json"])
    with open(output_file, "wb") as f:
        f.write(img_bytes)
elif img_data and "url" in img_data[0]:
    # URL 模式，需要下载
    import urllib.request
    urllib.request.urlretrieve(img_data[0]["url"], output_file)
else:
    error = data.get("error", {}).get("message", "")
    if not error:
        error = json.dumps(data, ensure_ascii=False)[:300]
    print(f"ERROR:{error}", file=sys.stderr)
    sys.exit(1)
PYEOF
    python3 "$EXTRACT_PY" "$RESPONSE_FILE" "$AI_IMG" 2>/tmp/xhs_cover_err.log

  elif [ "$IMG_API_TYPE" = "hunyuan" ]; then
    echo "   服务: aiart (腾讯云混元生图)"
    echo "   Endpoint: ${HUNYUAN_ENDPOINT} | Region: ${HUNYUAN_REGION} | RspImgType: ${HUNYUAN_RSP_TYPE}"

    # 通过腾讯云 SDK 调用 TextToImageRapid
    GEN_PY="${TMP_DIR}/gen_hunyuan.py"
    cat > "$GEN_PY" << 'PYEOF'
import os, sys, json, base64, urllib.request
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.aiart.v20221229 import aiart_client, models

prompt = sys.argv[1]
out_path = sys.argv[2]

sid = os.environ.get('HUNYUAN_SECRET_ID')
skey = os.environ.get('HUNYUAN_SECRET_KEY')
region = os.environ.get('HUNYUAN_REGION', 'ap-guangzhou')
endpoint = os.environ.get('HUNYUAN_ENDPOINT', 'aiart.tencentcloudapi.com')
rsp_type = os.environ.get('HUNYUAN_RSP_TYPE', 'url')

if not sid or not skey:
    raise SystemExit('missing HUNYUAN_SECRET_ID/HUNYUAN_SECRET_KEY')

cred = credential.Credential(sid, skey)
httpProfile = HttpProfile()
httpProfile.endpoint = endpoint
clientProfile = ClientProfile()
clientProfile.httpProfile = httpProfile
client = aiart_client.AiartClient(cred, region, clientProfile)

req = models.TextToImageRapidRequest()
req.Prompt = prompt
req.RspImgType = rsp_type

resp = client.TextToImageRapid(req)

# resp.ResultImage: url 或 base64
if rsp_type == 'base64':
    img_bytes = base64.b64decode(resp.ResultImage)
    with open(out_path, 'wb') as f:
        f.write(img_bytes)
else:
    # url
    urllib.request.urlretrieve(resp.ResultImage, out_path)

print(json.dumps({
    'RequestId': resp.RequestId,
    'Seed': resp.Seed,
    'RspImgType': rsp_type,
}, ensure_ascii=False))
PYEOF

    # 用 python3 的 argv 传 prompt，避免 bash 引号地狱
    python3 "$GEN_PY" "$PROMPT" "$AI_IMG" 2>/tmp/xhs_cover_err.log | tee "${TMP_DIR}/hunyuan_meta.json" >/dev/null

  else
    # Gemini 模式（默认）
    echo "   模型: ${GEMINI_MODEL} (Gemini)"

# 转义 prompt 中的特殊字符用于 JSON
PROMPT_ESCAPED=$(echo "$PROMPT" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))")

# 构建 Gemini API 请求（3:2 比例）
PAYLOAD=$(cat <<EOFPAYLOAD
{
  "contents": [{
    "parts": [
      {"text": ${PROMPT_ESCAPED}}
    ]
  }],
  "generationConfig": {
    "responseModalities": ["IMAGE"],
    "imageConfig": {
      "aspectRatio": "3:2"
    }
  }
}
EOFPAYLOAD
)

RESPONSE_FILE="${TMP_DIR}/gemini_response.json"

curl -s -X POST "${GEMINI_API_URL}?key=${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  -o "$RESPONSE_FILE"

# 从响应中提取 base64 图片数据并保存
EXTRACT_PY="${TMP_DIR}/extract_img.py"
cat > "$EXTRACT_PY" << 'PYEOF'
import sys, json, base64

response_file = sys.argv[1]
output_file = sys.argv[2]

with open(response_file, "r") as f:
    data = json.load(f)

found = False
candidates = data.get("candidates", [])
if candidates:
    parts = candidates[0].get("content", {}).get("parts", [])
    for part in parts:
        inline = part.get("inlineData") or part.get("inline_data")
        if inline and "data" in inline:
            img_bytes = base64.b64decode(inline["data"])
            with open(output_file, "wb") as f:
                f.write(img_bytes)
            found = True
            break

if not found:
    error = data.get("error", {}).get("message", "")
    if not error:
        error = json.dumps(data, ensure_ascii=False)[:300]
    print(f"ERROR:{error}", file=sys.stderr)
    sys.exit(1)
PYEOF
    python3 "$EXTRACT_PY" "$RESPONSE_FILE" "$AI_IMG" 2>/tmp/xhs_cover_err.log

  fi  # 结束 API 类型判断

if [ ! -s "$AI_IMG" ]; then
  ERR=$(cat /tmp/xhs_cover_err.log 2>/dev/null)
  echo "❌ 图片生成失败: ${ERR:-未知错误}"
  echo ""
  echo "⚠️ 将使用渐变色占位图代替..."
  $MAGICK -size ${TOP_W}x${TOP_H} \
    gradient:"#667eea"-"#764ba2" \
    "$AI_IMG"
else
  echo "   ✅ AI 图片生成成功"
fi

fi  # 结束 USER_IMAGE_MODE 判断

# 裁剪/缩放为 1080x720 (3:2)
echo "   调整图片尺寸为 ${TOP_W}x${TOP_H}..."
$MAGICK "$AI_IMG" -resize "${TOP_W}x${TOP_H}^" -gravity center -extent "${TOP_W}x${TOP_H}" "$AI_RESIZED"

echo "   ✅ 上半部分就绪"

# ==================== 第2步：生成标题区域 ====================

echo "🔄 [2/3] 生成标题文字区域..."

# 标题区域布局（参考小红书爆款封面风格）
# 文字左对齐、大字号、粗体、撑满下半区域
# 左右边距 60px，上下边距 60px
PAD_LEFT=60
PAD_RIGHT=60
PAD_TOP=60
PAD_BOTTOM=60
TEXT_AREA_W=$((BOT_W - PAD_LEFT - PAD_RIGHT))  # 960px
TEXT_AREA_H=$((BOT_H - PAD_TOP - PAD_BOTTOM))   # 600px

# 查找可用的中文字体（优先粗体）
FONT=""
for f in \
  "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc" \
  "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc" \
  "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc" \
  "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Bold.ttc" \
  "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc" \
  "/usr/share/fonts/wqy-zenhei/wqy-zenhei.ttc" \
  "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf" \
  "/usr/share/fonts/noto/NotoSansSC-Bold.ttf" \
  "/usr/share/fonts/truetype/noto/NotoSansSC-Bold.ttf"; do
  if [ -f "$f" ]; then
    FONT="$f"
    break
  fi
done

# 如果没有找到中文字体，尝试用 fc-list 搜索
if [ -z "$FONT" ]; then
  FONT=$(fc-list :lang=zh -f "%{file}\n" 2>/dev/null | head -1)
fi

FONT_ARG=""
if [ -n "$FONT" ]; then
  FONT_ARG="-font $FONT"
  echo "   使用字体: $(basename "$FONT")"
else
  echo "   ⚠️ 未找到中文字体，使用系统默认字体（中文可能显示为方块）"
  echo "   建议安装: apt install -y fonts-noto-cjk"
fi

# 智能断句：调用 AI 按中文语义断行，避免拆散词语
# 目标：控制在 2-3 行，每行字符数要足够宽松以避免过碎断句
TITLE_LEN=${#TITLE}
if [ "$TITLE_LEN" -le 4 ]; then
  MAX_CHARS_PER_LINE=4
  TARGET_LINES=1
  FONT_SIZE=180
elif [ "$TITLE_LEN" -le 8 ]; then
  MAX_CHARS_PER_LINE=8
  TARGET_LINES=1
  FONT_SIZE=160
elif [ "$TITLE_LEN" -le 12 ]; then
  MAX_CHARS_PER_LINE=$((TITLE_LEN / 2 + 1))
  TARGET_LINES=2
  FONT_SIZE=140
elif [ "$TITLE_LEN" -le 20 ]; then
  MAX_CHARS_PER_LINE=$((TITLE_LEN / 2 + 1))
  TARGET_LINES=2
  FONT_SIZE=120
elif [ "$TITLE_LEN" -le 30 ]; then
  MAX_CHARS_PER_LINE=$((TITLE_LEN / 3 + 1))
  TARGET_LINES=3
  FONT_SIZE=100
else
  MAX_CHARS_PER_LINE=$((TITLE_LEN / 3 + 1))
  TARGET_LINES=3
  FONT_SIZE=80
fi

# 调用 Gemini 文本模型进行语义断句
LINEBREAK_PY="${TMP_DIR}/linebreak.py"
cat > "$LINEBREAK_PY" << 'PYEOF'
import sys, json, urllib.request, os

title = sys.argv[1]
max_chars = int(sys.argv[2])
api_key = os.environ.get("GEMINI_API_KEY", "")

# 如果标题不需要换行，直接输出
if len(title) <= max_chars:
    print(title)
    sys.exit(0)

# 如果没有 API key，用简单的标点断句兜底
if not api_key:
    # 简单兜底：按标点拆，或等分
    import re
    parts = re.split(r'([，,。！？、；：])', title)
    result = []
    line = ""
    for p in parts:
        if len(line) + len(p) <= max_chars:
            line += p
        else:
            if line:
                result.append(line)
            line = p
    if line:
        result.append(line)
    print('\n'.join(result))
    sys.exit(0)

# 调用 Gemini 文本模型断句
target_lines = os.environ.get("TARGET_LINES", "2")
prompt = f"""你是排版助手。将以下标题断成{target_lines}行，每行不超过{max_chars}个字符。
要求：
1. 绝对不能拆散词语（如"普通人"必须在同一行）
2. 在语义自然的位置换行（主谓之间、逗号处等）
3. 尽量少的行数（优先{target_lines}行，最多不超过{int(target_lines)+1}行）
4. 只输出断行结果，每行一段，不要任何解释

标题：{title}"""

payload = json.dumps({
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {"temperature": 0, "maxOutputTokens": 256, "thinkingConfig": {"thinkingBudget": 0}}
}).encode()

# 使用 gemini-2.5-flash（纯文本，非图片模型）
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

try:
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
    
    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    # 清理：去掉可能的空行和多余空格
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if lines:
        print('\n'.join(lines))
        sys.exit(0)
except Exception as e:
    print(f"AI断句失败: {e}", file=sys.stderr)

# 兜底：简单按字符数等分
import re
parts = re.split(r'([，,。！？、；：])', title)
result = []
line = ""
for p in parts:
    if len(line) + len(p) <= max_chars:
        line += p
    else:
        if line:
            result.append(line)
        line = p
if line:
    result.append(line)
print('\n'.join(result))
PYEOF

WRAPPED_TITLE=$(TARGET_LINES="$TARGET_LINES" python3 "$LINEBREAK_PY" "$TITLE" "$MAX_CHARS_PER_LINE")
echo "   断句结果:"
echo "$WRAPPED_TITLE" | while IFS= read -r line; do echo "     「$line」"; done
echo "   字号: ${FONT_SIZE}px"

# 计算行数，动态微调字号确保不超出区域
LINE_COUNT=$(echo "$WRAPPED_TITLE" | wc -l)

# 用 label + -size 约束渲染，循环缩小字号直到实际高度适配
TEXT_BLOCK="${TMP_DIR}/text_block.png"

render_text_block() {
  $MAGICK -background "$BG_COLOR" \
    -fill "$TEXT_COLOR" \
    $FONT_ARG \
    -pointsize "$FONT_SIZE" \
    -interline-spacing "$((FONT_SIZE / 4))" \
    -gravity SouthWest \
    label:"$WRAPPED_TITLE" \
    "$TEXT_BLOCK"
}

render_text_block

# 检查实际渲染高度，超出则缩小字号重试
TB_H=$($MAGICK identify -format "%h" "$TEXT_BLOCK" 2>/dev/null)
while [ "$TB_H" -gt "$TEXT_AREA_H" ] && [ "$FONT_SIZE" -gt 40 ]; do
  FONT_SIZE=$((FONT_SIZE - 10))
  echo "   文字块高 ${TB_H}px > ${TEXT_AREA_H}px，缩小字号至 ${FONT_SIZE}px..."
  render_text_block
  TB_H=$($MAGICK identify -format "%h" "$TEXT_BLOCK" 2>/dev/null)
done

# 同样检查宽度，超出则缩小
TB_W=$($MAGICK identify -format "%w" "$TEXT_BLOCK" 2>/dev/null)
while [ "$TB_W" -gt "$TEXT_AREA_W" ] && [ "$FONT_SIZE" -gt 40 ]; do
  FONT_SIZE=$((FONT_SIZE - 10))
  echo "   文字块宽 ${TB_W}px > ${TEXT_AREA_W}px，缩小字号至 ${FONT_SIZE}px..."
  render_text_block
  TB_W=$($MAGICK identify -format "%w" "$TEXT_BLOCK" 2>/dev/null)
done

TB_SIZE="${TB_W}x${TB_H}"
echo "   最终字号: ${FONT_SIZE}px, 行数: ${LINE_COUNT}, 文字块: ${TB_SIZE}"

# 创建纯色底板，将文字块左对齐放置（左下角定位）
$MAGICK -size "${BOT_W}x${BOT_H}" "xc:${BG_COLOR}" \
  "$TEXT_BLOCK" -gravity SouthWest -geometry "+${PAD_LEFT}+${PAD_BOTTOM}" \
  -composite \
  "$TITLE_IMG"

echo "   ✅ 下半部分就绪（左对齐大字·智能断句）"

# ==================== 第3步：上下拼接 ====================

echo "🔄 [3/3] 拼接封面图..."

$MAGICK "$AI_RESIZED" "$TITLE_IMG" -append "$OUTPUT"

# 验证最终尺寸
FINAL_SIZE=$($MAGICK identify -format "%wx%h" "$OUTPUT" 2>/dev/null)
echo ""
echo "✅ 封面图生成完成！"
echo "   路径: ${OUTPUT}"
echo "   尺寸: ${FINAL_SIZE} (目标: ${COVER_W}x${COVER_H})"
echo "   比例: 3:4"
echo ""
echo "📐 结构:"
echo "   ┌──────────────┐"
echo "   │  AI生成图片   │ ${TOP_W}x${TOP_H} (3:2)"
echo "   │              │"
echo "   ├──────────────┤"
echo "   │  ${BG_COLOR} 底色    │ ${BOT_W}x${BOT_H} (3:2)"
echo "   │  「${TITLE:0:8}...」│"
echo "   └──────────────┘"
echo "   总计: ${COVER_W}x${COVER_H} (3:4)"
