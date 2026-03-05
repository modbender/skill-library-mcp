#!/bin/bash
# 飞书日历管理器 - 创建事件
# 用法：./create-event.sh "标题" "开始时间" "结束时间" [描述]

set -e

# 配置文件路径
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
DEFAULT_USER_ID=$(jq -r '.default_user_id' "$CONFIG_FILE")

# 验证配置
if [ -z "$APP_ID" ] || [ "$APP_ID" = "null" ]; then
  echo "❌ 配置文件中缺少 app_id" >&2
  exit 1
fi

# 参数
SUMMARY="$1"
START_TIME="$2"
END_TIME="$3"
DESCRIPTION="${4:-}"

# 获取 access token
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{
    \"app_id\": \"$APP_ID\",
    \"app_secret\": \"$APP_SECRET\"
  }" | jq -r '.tenant_access_token')

# 转换时间为秒级时间戳
START_TS=$(date -d "$START_TIME" +%s)
END_TS=$(date -d "$END_TIME" +%s)

# 生成幂等性键
IDEMPOTENCY_KEY=$(uuidgen | tr -d '-' | head -c 32)

# 创建事件
RESPONSE=$(curl -s -X POST \
  "https://open.feishu.cn/open-apis/calendar/v4/calendars/${CALENDAR_ID}/events?idempotency_key=${IDEMPOTENCY_KEY}&user_id_type=open_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "{
    \"summary\": \"$SUMMARY\",
    \"description\": \"$DESCRIPTION\",
    \"start_time\": {
      \"timestamp\": \"$START_TS\",
      \"timezone\": \"Asia/Shanghai\"
    },
    \"end_time\": {
      \"timestamp\": \"$END_TS\",
      \"timezone\": \"Asia/Shanghai\"
    },
    \"visibility\": \"default\",
    \"attendee_ability\": \"can_see_others\",
    \"free_busy_status\": \"busy\",
    \"reminders\": [
      { \"minutes\": 15 }
    ]
  }")

CODE=$(echo "$RESPONSE" | jq -r '.code')

if [ "$CODE" != "0" ]; then
  echo "❌ 创建失败: $(echo "$RESPONSE" | jq -r '.msg')" >&2
  exit 1
fi

EVENT_ID=$(echo "$RESPONSE" | jq -r '.data.event.event_id')
APP_LINK=$(echo "$RESPONSE" | jq -r '.data.event.app_link')

# 添加参与人
curl -s -X POST \
  "https://open.feishu.cn/open-apis/calendar/v4/calendars/${CALENDAR_ID}/events/${EVENT_ID}/attendees?user_id_type=open_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "{
    \"attendees\": [
      {
        \"user_id\": \"$DEFAULT_USER_ID\",
        \"type\": \"user\"
      }
    ],
    \"need_notification\": true
  }" > /dev/null

# 输出结果
echo "✅ 日程创建成功"
echo "标题: $SUMMARY"
echo "时间: $START_TIME - $END_TIME"
echo "链接: $APP_LINK"
