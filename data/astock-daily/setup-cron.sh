#!/bin/bash
# A 股每日精选 - 定时任务设置脚本

echo "⏰ 设置 A 股每日精选定时任务"
echo ""

# 获取当前 crontab
CURRENT_CRON=$(crontab -l 2>/dev/null || echo "")

# 检查是否已存在
if echo "$CURRENT_CRON" | grep -q "astock-daily"; then
    echo "⚠️  已存在 astock-daily 定时任务"
    echo ""
    echo "当前任务:"
    echo "$CURRENT_CRON" | grep "astock-daily"
    echo ""
    read -p "是否删除并重新添加？(y/n): " confirm
    if [ "$confirm" != "y" ]; then
        echo "已取消"
        exit 0
    fi
    # 删除旧任务
    echo "$CURRENT_CRON" | grep -v "astock-daily" | crontab -
fi

# 添加新任务
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CRON_LINE="30 9 * * 1-5 cd $SCRIPT_DIR && source .env && /opt/homebrew/bin/node index.js >> /tmp/astock-daily.log 2>&1"

# 添加到 crontab
(echo "$CURRENT_CRON"; echo "$CRON_LINE") | crontab -

echo ""
echo "✅ 定时任务已添加！"
echo ""
echo "📋 当前 crontab:"
crontab -l
echo ""
echo "📊 任务说明:"
echo "   - 运行时间：每周一至周五 9:30"
echo "   - 日志文件：/tmp/astock-daily.log"
echo ""
echo "🔧 管理命令:"
echo "   查看日志：tail -f /tmp/astock-daily.log"
echo "   查看任务：crontab -l"
echo "   删除任务：crontab -e (手动删除对应行)"
