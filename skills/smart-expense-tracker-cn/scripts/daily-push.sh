#!/bin/bash
# 每日汇总推送脚本（供 cron 调用）
# 用法: daily-push.sh [用户ID]

USER_ID="${1:-default}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$HOME/.expense-tracker"
RECORDS_FILE="$DATA_DIR/records.jsonl"
CONFIG_FILE="$DATA_DIR/config.json"

# 检查是否有今日记录
TODAY=$(date +%Y-%m-%d)

if [ ! -f "$RECORDS_FILE" ]; then
    echo '{"error": "暂无消费记录"}'
    exit 0
fi

# 检查今日是否有记录
if ! grep -q "$TODAY" "$RECORDS_FILE"; then
    echo '{"message": "今日暂无消费记录"}'
    exit 0
fi

# 生成汇总数据
SUMMARY=$("$SCRIPT_DIR/summary.sh" today "$USER_ID" 2>/dev/null)

if [ -z "$SUMMARY" ]; then
    echo '{"error": "生成汇总失败"}'
    exit 1
fi

# 输出汇总结果（JSON格式，供上层处理）
echo "$SUMMARY"
