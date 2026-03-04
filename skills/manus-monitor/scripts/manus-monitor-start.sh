#!/bin/bash
# 启动 Manus 任务监控
# 当有进行中任务时，自动创建 cron 每分钟轮询

SCRIPT_DIR="$(dirname "$0")"
MANUS_SCRIPT="$SCRIPT_DIR/manus-monitor.sh"

# 检查是否已有监控 cron
if openclaw cron list 2>/dev/null | grep -q "manus-task-monitor"; then
  echo "监控已存在，无需重复创建"
  exit 0
fi

# 创建 cron 任务
openclaw cron add << EOF
{
  "name": "manus-task-monitor",
  "schedule": {
    "kind": "every",
    "everyMs": 60000
  },
  "payload": {
    "kind": "agentTurn",
    "message": "执行 $MANUS_SCRIPT 脚本检查 Manus 任务状态。如果有进行中任务，记录日志；如果状态变化，发送通知到 Telegram。然后检查进行中任务数量，如果为 0，删除此 cron 监控任务。"
  },
  "sessionTarget": "isolated",
  "delivery": {
    "mode": "none"
  },
  "enabled": true
}
EOF

echo "Manus 任务监控已启动"
