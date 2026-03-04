#!/bin/bash
# 停止 Manus 任务监控

# 查找并删除监控 cron
jobs=$(openclaw cron list 2>/dev/null)

echo "$jobs" | jq -r '.[] | select(.name == "manus-task-monitor") | .id' | while read job_id; do
  if [ -n "$job_id" ]; then
    openclaw cron remove "$job_id"
    echo "已删除监控任务: $job_id"
  fi
done

if [ $(echo "$jobs" | jq -r '.[] | select(.name == "manus-task-monitor") | .id' | wc -l) -eq 0 ]; then
  echo "没有找到Manus监控任务"
fi
