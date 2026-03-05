#!/bin/bash

# 检查定时任务状态

echo "=== Cron 任务状态 ==="
echo ""

# 检查每日热点
if openclaw cron list | grep -q "每日热点总结"; then
    echo "✓ 每日热点总结: 已启用"
else
    echo "✗ 每日热点总结: 未启用"
fi

# 检查记忆清理
if crontab -l | grep -q "cleanup-memory"; then
    echo "✓ 记忆清理: 已启用"
else
    echo "✗ 记忆清理: 未启用"
fi

echo ""
echo "=== 最近运行记录 ==="
openclaw cron runs --name "每日热点总结" --limit 5 2>/dev/null || echo "无运行记录"
