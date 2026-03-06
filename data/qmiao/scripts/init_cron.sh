#!/usr/bin/env bash
  
# 检查是否已经存在IM监控任务
EXISTING_JOB=$(openclaw cron list --json | grep -c "qmiao-im-monitor" || true)

if [ "$EXISTING_JOB" -eq 0 ]; then
    echo "创建千喵IM消息监控定时任务..."

    # 使用正确的cron add命令格式
    openclaw cron add \
        --name "qmiao-im-monitor" \
        --every 1m \
        --session isolated \
        --message "执行千喵IM消息检查：获取聊天历史并推送新消息" \
        --announce

    echo "✅  千喵IM消息监控定时任务已创建"
else
    echo "ℹ️ 千喵IM消息监控定时任务已存在"
fi