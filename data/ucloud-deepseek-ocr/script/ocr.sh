#!/bin/bash
# OCR Script - 使用 DeepSeek-OCR 识别图片文字
# Usage: ocr.sh <image_path> [format]

set -e

# 加载环境变量
if [ -f ~/.openclaw-env ]; then
  source ~/.openclaw-env
fi

# 检查 API Key
if [ -z "$DEEPSEEK_OCR_API_KEY" ]; then
  echo "错误: 未设置 DEEPSEEK_OCR_API_KEY 环境变量" >&2
  echo "请运行: source ~/.openclaw-env" >&2
  exit 1
fi

# 检查参数
if [ -z "$1" ]; then
  echo "用法: ocr.sh <图片路径> [输出格式]" >&2
  echo "示例: ocr.sh /path/to/image.jpg markdown" >&2
  exit 1
fi

IMAGE_PATH="$1"
FORMAT="${2:-markdown}"

# 检查文件存在
if [ ! -f "$IMAGE_PATH" ]; then
  echo "错误: 文件不存在: $IMAGE_PATH" >&2
  exit 1
fi

# 获取 MIME 类型
get_mime_type() {
  local file="$1"
  local ext="${file##*.}"
  case "${ext,,}" in
    jpg|jpeg) echo "image/jpeg" ;;
    png) echo "image/png" ;;
    gif) echo "image/gif" ;;
    webp) echo "image/webp" ;;
    bmp) echo "image/bmp" ;;
    *) echo "image/jpeg" ;;  # 默认
  esac
}

MIME_TYPE=$(get_mime_type "$IMAGE_PATH")

# 转换图片为 base64
IMAGE_BASE64=$(base64 -w 0 "$IMAGE_PATH" 2>/dev/null || base64 "$IMAGE_PATH" | tr -d '\n')

# API 地址
API_URL="${DEEPSEEK_OCR_API_URL:-https://api.modelverse.cn/v1/chat/completions}"

# 构建提示词
PROMPT="convert to $FORMAT"

# 发送请求
RESPONSE=$(curl -s "$API_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $DEEPSEEK_OCR_API_KEY" \
  -d @- <<EOF
{
  "model": "deepseek-ai/DeepSeek-OCR",
  "max_tokens": 8192,
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "$PROMPT"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "data:$MIME_TYPE;base64,$IMAGE_BASE64"
          }
        }
      ]
    }
  ]
}
EOF
)

# 检查响应错误
if echo "$RESPONSE" | grep -q '"error"'; then
  echo "API 错误:" >&2
  echo "$RESPONSE" | jq -r '.error.message // .error // .' >&2
  exit 1
fi

# 提取结果
RESULT=$(echo "$RESPONSE" | jq -r '.choices[0].message.content // empty')

if [ -z "$RESULT" ]; then
  echo "错误: 无法解析 API 响应" >&2
  echo "$RESPONSE" >&2
  exit 1
fi

echo "$RESULT"