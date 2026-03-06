#!/bin/bash

# 设置定时任务

echo "=== 设置定时任务 ==="

# 1. 创建热点总结任务
echo "创建每日热点总结任务..."
openclaw cron add --name "每日热点总结" \
  --schedule "0 10 * * *" \
  --tz "Asia/Shanghai" \
  --session-target "isolated" \
  --delivery "announce"

# 2. 设置记忆清理
echo "设置记忆清理..."
chmod +x scripts/cleanup-memory.sh
(crontab -l 2>/dev/null; echo "0 3 * * 0 $(pwd)/scripts/cleanup-memory.sh >> ~/memory/cleanup.log 2>&1") | crontab -

# 3. 验证
echo ""
echo "=== 验证 ==="
./scripts/check-cron.sh

echo ""
echo "✓ 定时任务设置完成"
