#!/bin/bash
# 导出记录为 CSV/JSON
# 用法: export-records.sh [月份] [格式] [用户ID]
# 月份格式: 2024-01，默认当月
# 格式: csv 或 json，默认 json

MONTH="${1:-$(date +%Y-%m)}"
FORMAT="${2:-json}"
USER_ID="${3:-.*}"
DATA_DIR="$HOME/.expense-tracker"
RECORDS_FILE="$DATA_DIR/records.jsonl"

if [ ! -f "$RECORDS_FILE" ]; then
    echo '{"error": "暂无消费记录"}'
    exit 0
fi

# 筛选指定月份的记录
RECORDS=$(grep "$MONTH" "$RECORDS_FILE" | grep -E "\"userId\":\"$USER_ID\"" || true)

if [ -z "$RECORDS" ]; then
    echo "{\"error\": \"没有找到 $MONTH 的记录\"}"
    exit 0
fi

case "$FORMAT" in
    csv)
        echo "id,amount,category,note,time"
        echo "$RECORDS" | jq -r '[.id, .amount, .category, .note, .time] | @csv'
        ;;
    json)
        echo "$RECORDS" | jq -s 'sort_by(.time)'
        ;;
    *)
        echo '{"error": "格式支持: csv 或 json"}'
        exit 1
        ;;
esac
