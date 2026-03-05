#!/bin/bash
# 生成消费汇总报告
# 用法: summary.sh [today|week|month] [用户ID]

PERIOD="${1:-today}"
USER_ID="${2:-.*}"
DATA_DIR="$HOME/.expense-tracker"
RECORDS_FILE="$DATA_DIR/records.jsonl"
CONFIG_FILE="$DATA_DIR/config.json"

if [ ! -f "$RECORDS_FILE" ]; then
    echo '{"error": "暂无消费记录"}'
    exit 0
fi

# 读取配置
if [ -f "$CONFIG_FILE" ]; then
    MONTHLY_BUDGET=$(jq -r '.monthlyBudget // 5000' "$CONFIG_FILE")
else
    MONTHLY_BUDGET=5000
fi

# 根据时间范围筛选
case "$PERIOD" in
    today)
        DATE_FILTER=$(date +%Y-%m-%d)
        TITLE="今日消费汇总"
        ;;
    week)
        DATE_FILTER=$(date +%Y-%m)
        # 获取本周起止日期
        WEEK_START=$(date -d "last monday" +%Y-%m-%d 2>/dev/null || date -v-monday +%Y-%m-%d)
        TITLE="本周消费汇总"
        ;;
    month)
        DATE_FILTER=$(date +%Y-%m)
        TITLE="本月消费汇总"
        ;;
    *)
        DATE_FILTER="$PERIOD"
        TITLE="${PERIOD} 消费汇总"
        ;;
esac

# 提取记录并计算
if [ "$PERIOD" = "today" ]; then
    RECORDS=$(grep "$DATE_FILTER" "$RECORDS_FILE" | grep -E "\"userId\":\"$USER_ID\"" || true)
else
    RECORDS=$(grep -E "\"userId\":\"$USER_ID\"" "$RECORDS_FILE" | grep "$DATE_FILTER" || true)
fi

if [ -z "$RECORDS" ]; then
    echo "{\"error\": \"没有找到消费记录\", \"period\": \"$PERIOD\"}"
    exit 0
fi

# 计算总金额
TOTAL=$(echo "$RECORDS" | jq -s '[.[].amount] | add // 0')

# 按分类统计
CATEGORY_STATS=$(echo "$RECORDS" | jq -s '
    group_by(.category) | 
    map({
        category: .[0].category,
        total: ([.[].amount] | add),
        count: length
    }) | 
    sort_by(-.total)
')

# 统计笔数
COUNT=$(echo "$RECORDS" | jq -s 'length')

# 本月累计
MONTH=$(date +%Y-%m)
MONTH_RECORDS=$(grep "$MONTH" "$RECORDS_FILE" | grep -E "\"userId\":\"$USER_ID\"" || true)
MONTH_TOTAL=$(echo "$MONTH_RECORDS" | jq -s '[.[].amount] | add // 0' 2>/dev/null || echo "0")

# 预算剩余
BUDGET_REMAINING=$(echo "$MONTHLY_BUDGET - $MONTH_TOTAL" | bc)

# 输出 JSON 结果
cat << EOF
{
    "success": true,
    "period": "$PERIOD",
    "title": "$TITLE",
    "date": "$(date +%Y-%m-%d)",
    "total": $TOTAL,
    "count": $COUNT,
    "categories": $CATEGORY_STATS,
    "monthSummary": {
        "total": $MONTH_TOTAL,
        "budget": $MONTHLY_BUDGET,
        "remaining": $BUDGET_REMAINING
    }
}
EOF
