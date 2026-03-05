#!/bin/bash
# Manus Task Monitor
# 每分钟检查保存的任务状态，状态变化时通知用户

DATA_DIR="$(dirname "$0")/../data"
TASK_LIST="$DATA_DIR/task_list.txt"
STATUS_FILE="$DATA_DIR/task_status.json"

# 确保数据目录存在
mkdir -p "$DATA_DIR"

# 初始化状态文件
init_status_file() {
  if [ ! -f "$STATUS_FILE" ]; then
    echo "{}" > "$STATUS_FILE"
  fi
}

# 获取任务状态
get_task_status() {
  local task_id="$1"
  curl -s "https://api.manus.ai/v1/tasks/$task_id" \
    -H "API_KEY: $MANUS_API_KEY" | jq -r '.status // "unknown"'
}

# 发送通知到 Telegram
send_notification() {
  local task_id="$1"
  local old_status="$2"
  local new_status="$3"
  local title="$4"

  # 构建消息
  local message="Manus 任务状态更新 🎉

任务：${title:-未知}
状态：${old_status} → **${new_status}**
链接：https://manus.im/app/${task_id}"

  # 发送到 Telegram（通过 OpenClaw 消息工具）
  # 这里使用 curl 直接调用 Telegram Bot API
  local bot_token="${TELEGRAM_BOT_TOKEN:-}"
  local chat_id="${TELEGRAM_CHAT_ID:-}"

  if [ -n "$bot_token" ] && [ -n "$chat_id" ]; then
    curl -s -X POST "https://api.telegram.org/bot${bot_token}/sendMessage" \
      -d "chat_id=${chat_id}" \
      -d "text=${message}" \
      -d "parse_mode=Markdown" > /dev/null
  fi

  # 也输出到 stdout，让 cron 记录日志
  echo "通知已发送: $task_id $old_status -> $new_status"
}

# 主监控逻辑
monitor_tasks() {
  if [ ! -f "$TASK_LIST" ] || [ ! -s "$TASK_LIST" ]; then
    echo "没有保存的任务，退出"
    return 0
  fi

  init_status_file

  # 读取旧状态
  old_status_json=$(cat "$STATUS_FILE")

  running_count=0
  temp_file=$(mktemp)

  echo "=== 开始检查任务状态 ===" >> /tmp/manus-monitor.log
  date >> /tmp/manus-monitor.log

  while IFS='|' read -r task_id timestamp description status title; do
    if [ -z "$task_id" ]; then
      continue
    fi

    # 获取最新状态
    current_status=$(get_task_status "$task_id")

    # 检查状态是否变化
    old_status=$(echo "$old_status_json" | jq -r ".\"$task_id\" // \"unknown\"")

    if [ "$current_status" != "$old_status" ]; then
      # 状态变化，发送通知
      echo "状态变化: $task_id $old_status -> $current_status" >> /tmp/manus-monitor.log
      send_notification "$task_id" "$old_status" "$current_status" "${description:-$title}"

      # 更新状态
      old_status_json=$(echo "$old_status_json" | jq ".\"$task_id\" = \"$current_status\"")
    fi

    # 统计进行中任务
    if [ "$current_status" != "completed" ] && [ "$current_status" != "failed" ]; then
      running_count=$((running_count + 1))
    fi

  done < "$TASK_LIST"

  # 保存新状态
  echo "$old_status_json" > "$STATUS_FILE"

  echo "进行中任务数量: $running_count" >> /tmp/manus-monitor.log

  # 返回进行中任务数量
  echo "$running_count"
}

# 运行监控
monitor_tasks
