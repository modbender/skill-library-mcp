#!/bin/bash
# 设置每日汇总定时任务
# 用法: setup-cron.sh [用户ID] [小时] [分钟]

USER_ID="${1:-default}"
HOUR="${2:-21}"
MINUTE="${3:-00}"

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "设置每日消费汇总定时任务..."
echo "时间: 每天 $HOUR:$MINUTE"
echo "用户: $USER_ID"

# 创建汇总推送脚本
SUMMARY_PUSH="$SCRIPT_DIR/daily-push.sh"
cat > "$SUMMARY_PUSH" << 'SCRIPT'
#!/bin/bash
USER_ID="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$HOME/.expense-tracker"
RECORDS_FILE="$DATA_DIR/records.jsonl"

# 检查是否有今日记录
TODAY=$(date +%Y-%m-%d)
if [ -f "$RECORDS_FILE" ] && grep -q "$TODAY" "$RECORDS_FILE"; then
    # 生成汇总
    SUMMARY=$("$SCRIPT_DIR/summary.sh" today "$USER_ID" 2>/dev/null)
    
    if [ -n "$SUMMARY" ]; then
        # 输出汇总结果（供外部调用）
        echo "$SUMMARY"
    fi
else
    echo '{"message": "今日暂无消费记录"}'
fi
SCRIPT
chmod +x "$SUMMARY_PUSH"

echo "✅ 定时任务配置完成"
echo ""
echo "请手动添加 cron 任务："
echo "crontab -e"
echo ""
echo "添加以下行："
echo "$MINUTE $HOUR * * * $SCRIPT_DIR/daily-push.sh $USER_ID"
echo ""
echo "或使用系统提供的定时任务功能"
SCRIPT
chmod +x "$SCRIPT_DIR/setup-cron.sh" 2>/dev/null || true

# 输出配置信息
cat << EOF
{"success":true,"message":"定时任务配置已准备","hour":$HOUR,"minute":$MINUTE,"userId":"$USER_ID"}
EOF
