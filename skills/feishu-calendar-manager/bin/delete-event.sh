#!/bin/bash
# 飞书日历管理器 - 删除事件
# 用法：./delete-event.sh "事件ID"

set -e

CONFIG_FILE="${HOME}/.feishu-config.json"

# 自动配置：如果配置不存在，先自动配置
if [ ! -f "$CONFIG_FILE" ]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  "$SCRIPT_DIR/auto-setup.sh"
fi

# 读取配置
APP_ID=$(jq -r '.app_id' "$CONFIG_FILE")
APP_SECRET=$(jq -r '.app_secret' "$CONFIG_FILE")
CALENDAR_ID=$(jq -r '.calendar_id' "$CONFIG_FILE")

EVENT_ID="$1"

# 获取 access token
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{
    \"app_id\": \"$APP_ID\",
    \"app_secret\": \"$APP_SECRET\"
  }" | jq -r '.tenant_access_token')

# 删除事件
RESPONSE=$(curl -s -X DELETE \
  "https://open.feishu.cn/open-apis/calendar/v4/calendars/${CALENDAR_ID}/events/${EVENT_ID}?need_notification=false" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

CODE=$(echo "$RESPONSE" | jq -r '.code')

if [ "$CODE" = "0" ]; then
  echo "✅ 日程删除成功"
  echo "事件ID: $EVENT_ID"
else
  echo "❌ 删除失败: $(echo "$RESPONSE" | jq -r '.msg')" >&2
  exit 1
fi
