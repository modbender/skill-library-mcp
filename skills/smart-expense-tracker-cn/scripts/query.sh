#!/bin/bash
# 查询历史记录
# 用法: query.sh [分类] [天数] [用户ID]

CATEGORY="${1:-all}"
DAYS="${2:-7}"
USER_ID="${3:-.*}"
DATA_DIR="$HOME/.expense-tracker"
RECORDS_FILE="$DATA_DIR/records.jsonl"

if [ ! -f "$RECORDS_FILE" ]; then
    echo '{"error": "暂无消费记录"}'
    exit 0
fi

# 计算日期范围
START_DATE=$(date -d "$DAYS days ago" +%Y-%m-%d 2>/dev/null || date -v-${DAYS}d +%Y-%m-%d)

# 筛选记录
if [ "$CATEGORY" = "all" ]; then
    RECORDS=$(grep -E "\"userId\":\"$USER_ID\"" "$RECORDS_FILE" | tail -100)
else
    RECORDS=$(grep -E "\"userId\":\"$USER_ID\"" "$RECORDS_FILE" | grep "\"category\":\"$CATEGORY\"")
fi

if [ -z "$RECORDS" ]; then
    echo "{\"error\": \"没有找到记录\", \"category\": \"$CATEGORY\"}"
    exit 0
fi

# 格式化输出
echo "$RECORDS" | jq -s '
    sort_by(.time) | reverse |
    map({
        id: .id,
        amount: .amount,
        category: .category,
        note: .note,
        time: .time
    }) |
    {
        success: true,
        count: length,
        records: .
    }
'
