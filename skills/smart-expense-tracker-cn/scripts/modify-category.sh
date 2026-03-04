#!/bin/bash
# 修改记录分类
# 用法: modify-category.sh [记录ID] [新分类] [用户ID]

RECORD_ID="$1"
NEW_CATEGORY="$2"
USER_ID="${3:-default}"
DATA_DIR="$HOME/.expense-tracker"
RECORDS_FILE="$DATA_DIR/records.jsonl"

if [ -z "$RECORD_ID" ] || [ -z "$NEW_CATEGORY" ]; then
    echo '{"error": "用法: modify-category.sh [记录ID] [新分类]"}'
    exit 1
fi

if [ ! -f "$RECORDS_FILE" ]; then
    echo '{"error": "暂无消费记录"}'
    exit 0
fi

# 验证分类是否有效
VALID_CATEGORIES="food transport shopping entertainment medical education other"
if ! echo "$VALID_CATEGORIES" | grep -qw "$NEW_CATEGORY"; then
    echo "{\"error\": \"无效分类，支持: $VALID_CATEGORIES\"}"
    exit 1
fi

# 创建临时文件
TMP_FILE=$(mktemp)

# 更新指定记录的分类
jq --arg id "$RECORD_ID" --arg cat "$NEW_CATEGORY" '
    if .id == $id then .category = $cat else . end
' "$RECORDS_FILE" > "$TMP_FILE"
mv "$TMP_FILE" "$RECORDS_FILE"

echo "{\"success\": true, \"recordId\": \"$RECORD_ID\", \"newCategory\": \"$NEW_CATEGORY\", \"message\": \"分类已修改\"}"
