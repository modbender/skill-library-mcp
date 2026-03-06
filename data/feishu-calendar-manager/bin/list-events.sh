#!/bin/bash
# 飞书日历管理器 - 查询事件
# 用法：./list-events.sh [日期]
# 示例：./list-events.sh "today" 或 ./list-events.sh "2026-02-10"

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

DATE_PARAM="${1:-today}"

# 获取 access token
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{
    \"app_id\": \"$APP_ID\",
    \"app_secret\": \"$APP_SECRET\"
  }" | jq -r '.tenant_access_token')

# 计算时间范围
if [ "$DATE_PARAM" = "today" ]; then
  START_TS=$(date -d "today 00:00:00" +%s)000
  END_TS=$(date -d "today 23:59:59" +%s)000
  DATE_LABEL=$(date +%Y-%m-%d)
elif [ "$DATE_PARAM" = "tomorrow" ]; then
  START_TS=$(date -d "tomorrow 00:00:00" +%s)000
  END_TS=$(date -d "tomorrow 23:59:59" +%s)000
  DATE_LABEL=$(date -d "tomorrow" +%Y-%m-%d)
else
  # 假设是 YYYY-MM-DD 格式
  START_TS=$(date -d "$DATE_PARAM 00:00:00" +%s)000
  END_TS=$(date -d "$DATE_PARAM 23:59:59" +%s)000
  DATE_LABEL="$DATE_PARAM"
fi

# 查询事件
RESPONSE=$(curl -s -X GET \
  "https://open.feishu.cn/open-apis/calendar/v4/calendars/${CALENDAR_ID}/events?start_time=${START_TS}&end_time=${END_TS}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

CODE=$(echo "$RESPONSE" | jq -r '.code')

if [ "$CODE" != "0" ]; then
  echo "❌ 查询失败: $(echo "$RESPONSE" | jq -r '.msg')" >&2
  exit 1
fi

COUNT=$(echo "$RESPONSE" | jq '.data.items | length')

if [ "$COUNT" -eq 0 ]; then
  echo "📅 $DATE_LABEL：无安排"
else
  echo "📅 $DATE_LABEL（共 $COUNT 个事件）："
  echo ""
  echo "$RESPONSE" | jq -r '.data.items[] | "
  \(.start_time.timestamp // "待定") - \(.end_time.timestamp // "待定")
  \(.summary // "(无标题)")
  [ID: \(.event_id)]
  "'
fi
