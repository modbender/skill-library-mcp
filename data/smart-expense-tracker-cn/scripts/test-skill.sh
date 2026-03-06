#!/bin/bash
# 测试脚本 - 验证所有功能
# 用法: test-skill.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$HOME/.expense-tracker"

echo "=== 智能记账助手测试 ==="
echo ""

# 清理旧数据
rm -rf "$DATA_DIR"

echo "1. 测试记账功能..."
RESULT=$("$SCRIPT_DIR/record.sh" "午饭35元" "test_user")
echo "$RESULT" | jq .
echo ""

echo "2. 测试再记一笔..."
RESULT=$("$SCRIPT_DIR/record.sh" "打车25" "test_user")
echo "$RESULT" | jq .
echo ""

echo "3. 测试分类识别（奶茶）..."
RESULT=$("$SCRIPT_DIR/record.sh" "奶茶18块" "test_user")
echo "$RESULT" | jq .
echo ""

echo "4. 测试今日汇总..."
RESULT=$("$SCRIPT_DIR/summary.sh" today "test_user")
echo "$RESULT" | jq .
echo ""

echo "5. 测试设置预算..."
RESULT=$("$SCRIPT_DIR/set-budget.sh" 3000 "test_user")
echo "$RESULT" | jq .
echo ""

echo "6. 测试查询记录..."
RESULT=$("$SCRIPT_DIR/query.sh" all 7 "test_user")
echo "$RESULT" | jq .
echo ""

echo "7. 测试导出..."
RESULT=$("$SCRIPT_DIR/export-records.sh" "$(date +%Y-%m)" json "test_user")
echo "$RESULT" | jq .
echo ""

echo "=== 测试完成 ==="
echo "数据存储在: $DATA_DIR"
