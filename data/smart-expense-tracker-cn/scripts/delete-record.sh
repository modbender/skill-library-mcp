#!/bin/bash
# 删除记录
# 用法: delete-record.sh [记录ID或last] [用户ID]

RECORD_ID="$1"
USER_ID="${2:-default}"
DATA_DIR="$HOME/.expense-tracker"
RECORDS_FILE="$DATA_DIR/records.jsonl"

if [ ! -f "$RECORDS_FILE" ]; then
    echo '{"error": "暂无消费记录"}'
    exit 0
fi

if [ "$RECORD_ID" = "last" ]; then
    # 删除最后一条记录
    RECORD_ID=$(grep "\"userId\":\"$USER_ID\"" "$RECORDS_FILE" | tail -1 | jq -r '.id')
fi

if [ -z "$RECORD_ID" ]; then
    echo '{"error": "请指定要删除的记录ID或使用 \"last\" 删除最后一条"}'
    exit 1
fi

# 创建临时文件
TMP_FILE=$(mktemp)

# 删除指定记录（保留其他用户记录）
grep -v "\"id\":\"$RECORD_ID\"" "$RECORDS_FILE" > "$TMP_FILE"
mv "$TMP_FILE" "$RECORDS_FILE"

echo "{\"success\": true, \"deletedId\": \"$RECORD_ID\", \"message\": \"记录已删除\"}"
