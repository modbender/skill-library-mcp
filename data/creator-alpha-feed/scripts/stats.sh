#!/bin/bash
###############################################################################
# 工具脚本: 统计历史收集数据
# 用法: ./stats.sh [天数，默认7天]
###############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIPELINE_DIR="$(dirname "$SCRIPT_DIR")"
DAYS="${1:-7}"

echo ""
echo "📊 AI内容收集统计 - 最近 $DAYS 天"
echo "═══════════════════════════════════════════════════════════"
echo ""

# 检查是否有数据
if [[ ! -d "$PIPELINE_DIR/collected" ]]; then
    echo "❌ 未找到收集数据目录"
    exit 1
fi

# 获取最近N天的日期列表
RECENT_DATES=$(ls "$PIPELINE_DIR/collected/" 2>/dev/null | grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' | sort -r | head -$DAYS)

if [[ -z "$RECENT_DATES" ]]; then
    echo "❌ 未找到任何收集数据"
    exit 1
fi

# 统计表头
printf "%-12s %-8s %-8s %-8s %-20s\n" "日期" "总数" "HN" "Reddit" "来源"
echo "───────────────────────────────────────────────────────────"

# 统计每天的数据
TOTAL_ALL=0
TOTAL_HN=0
TOTAL_REDDIT=0

for date in $RECENT_DATES; do
    JSON_FILE="$PIPELINE_DIR/collected/$date/raw-content.json"
    
    if [[ -f "$JSON_FILE" ]]; then
        # 总条数
        COUNT=$(jq '[.sources[].items | length] | add' "$JSON_FILE" 2>/dev/null || echo "0")
        
        # HN条数
        HN_COUNT=$(jq '.sources[] | select(.id == "hn-ai") | .items | length' "$JSON_FILE" 2>/dev/null || echo "0")
        
        # Reddit条数
        REDDIT_COUNT=$(jq '[.sources[] | select(.id | startswith("reddit-")) | .items | length] | add' "$JSON_FILE" 2>/dev/null || echo "0")
        
        # 来源列表
        SOURCES=$(jq -r '.sources[].name' "$JSON_FILE" 2>/dev/null | tr '\n' ',' | sed 's/,$//')
        
        printf "%-12s %-8s %-8s %-8s %-20s\n" "$date" "$COUNT" "$HN_COUNT" "$REDDIT_COUNT" "${SOURCES:0:18}"
        
        TOTAL_ALL=$((TOTAL_ALL + COUNT))
        TOTAL_HN=$((TOTAL_HN + HN_COUNT))
        TOTAL_REDDIT=$((TOTAL_REDDIT + REDDIT_COUNT))
    else
        printf "%-12s %-8s %-8s %-8s %-20s\n" "$date" "N/A" "-" "-" "-"
    fi
done

echo "───────────────────────────────────────────────────────────"
printf "%-12s %-8s %-8s %-8s\n" "总计" "$TOTAL_ALL" "$TOTAL_HN" "$TOTAL_REDDIT"
echo ""

# 平均值
AVG=$((TOTAL_ALL / DAYS))
echo "📈 平均每天: $AVG 条"
echo ""

# 检查是否有推荐数据
echo "📋 最近推荐情况:"
echo "───────────────────────────────────────────────────────────"

for date in $(echo "$RECENT_DATES" | head -3); do
    MD_FILE="$PIPELINE_DIR/filtered/$date/wechat-worthy.md"
    if [[ -f "$MD_FILE" ]]; then
        # 统计推荐数量（粗略统计标题行）
        RECOMMEND_COUNT=$(grep -c "^### [0-9]\\+\." "$MD_FILE" 2>/dev/null || echo "0")
        echo "  $date: $RECOMMEND_COUNT 条推荐"
    else
        echo "  $date: 未分析"
    fi
done

echo ""
