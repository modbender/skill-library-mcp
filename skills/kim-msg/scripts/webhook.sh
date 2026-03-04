#!/usr/bin/env bash
# Kim Webhook 消息发送脚本
# 用法: webhook.sh <消息内容> [--text]
# 环境变量: KIM_WEBHOOK_TOKEN

set -euo pipefail

# 读取 API Token
API_TOKEN="${KIM_WEBHOOK_TOKEN:-}"

if [[ -z "$API_TOKEN" ]]; then
  echo "Error: KIM_WEBHOOK_TOKEN not set" >&2
  echo "请提供 Kim Webhook Token" >&2
  exit 1
fi

# 解析参数
MSG_TYPE="markdown"
CONTENT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --text)
      MSG_TYPE="text"
      shift
      ;;
    *)
      CONTENT="$1"
      shift
      ;;
  esac
done

if [[ -z "$CONTENT" ]]; then
  echo "Usage: $0 <消息内容> [--text]" >&2
  exit 1
fi

# 构造请求体
if [[ "$MSG_TYPE" == "markdown" ]]; then
  BODY=$(jq -n --arg content "$CONTENT" '{"msgtype": "markdown", "markdown": {"content": $content}}')
else
  BODY=$(jq -n --arg content "$CONTENT" '{"msgtype": "text", "text": {"content": $content}}')
fi

# 发送请求
URL="https://kim-robot.kwaitalk.com/api/robot/send?key=$API_TOKEN"
RESPONSE=$(curl -s -X POST "$URL" \
  -H "Content-Type: application/json" \
  -d "$BODY")

# 检查结果
if echo "$RESPONSE" | jq -e '.code == 200' > /dev/null 2>&1; then
  echo "✅ 消息发送成功！"
  echo "$RESPONSE" | jq -r '.msg // .'
else
  echo "❌ 发送失败：" >&2
  echo "$RESPONSE" >&2
  exit 1
fi