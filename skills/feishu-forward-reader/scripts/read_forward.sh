#!/bin/bash
# 读取飞书合并转发消息的详细内容
#
# 凭证获取优先级：
# 1. 命令行参数
# 2. 环境变量 FEISHU_APP_ID / FEISHU_APP_SECRET
# 3. OpenClaw 配置 ~/.openclaw/openclaw.json
#
# Usage: ./read_forward.sh <message_id> [app_id] [app_secret]

MESSAGE_ID="$1"
APP_ID="${2:-$FEISHU_APP_ID}"
APP_SECRET="${3:-$FEISHU_APP_SECRET}"

# 如果没有从参数或环境变量获取，尝试从 OpenClaw 配置读取
if [ -z "$APP_ID" ] || [ -z "$APP_SECRET" ]; then
  OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"
  if [ -f "$OPENCLAW_CONFIG" ]; then
    APP_ID="${APP_ID:-$(jq -r '.channels.feishu.appId // empty' "$OPENCLAW_CONFIG")}"
    APP_SECRET="${APP_SECRET:-$(jq -r '.channels.feishu.appSecret // empty' "$OPENCLAW_CONFIG")}"
  fi
fi

if [ -z "$MESSAGE_ID" ]; then
  echo "Usage: $0 <message_id> [app_id] [app_secret]"
  echo ""
  echo "凭证获取优先级："
  echo "  1. 命令行参数"
  echo "  2. 环境变量 FEISHU_APP_ID / FEISHU_APP_SECRET"
  echo "  3. OpenClaw 配置 ~/.openclaw/openclaw.json"
  exit 1
fi

if [ -z "$APP_ID" ] || [ -z "$APP_SECRET" ]; then
  echo "Error: 无法获取飞书凭证"
  echo "请通过命令行参数、环境变量或 OpenClaw 配置提供"
  exit 1
fi

# 获取 tenant_access_token
TOKEN=$(curl -s -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}" | jq -r '.tenant_access_token')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
  echo "Error: Failed to get access token"
  exit 1
fi

# 获取消息详情（包含转发的子消息）
curl -s "https://open.feishu.cn/open-apis/im/v1/messages/$MESSAGE_ID" \
  -H "Authorization: Bearer $TOKEN"
