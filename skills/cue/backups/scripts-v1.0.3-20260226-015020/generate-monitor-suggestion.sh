#!/bin/bash
#
# Monitor Suggestion Generator - 通用监控建议生成器
# 支持多种监控类型，易于扩展

# 允许部分命令失败，关键错误再退出
set -o pipefail

REPORT_URL="$1"
TASK_TOPIC="$2"
OUTPUT_FILE="${3:-/tmp/monitor_suggestion_$(date +%s).json}"

if [ -z "$REPORT_URL" ] || [ -z "$TASK_TOPIC" ]; then
    echo '{"error": "Report URL and task topic required"}' >&2
    exit 1
fi

# 提取股票代码
extract_symbol() {
    local topic="$1"
    local symbol=$(echo "$topic" | grep -oE '[0-9]{6}' | head -1)
    
    if [ -n "$symbol" ]; then
        if [ "${symbol:0:1}" = "6" ]; then
            echo "${symbol}.SH"
        else
            echo "${symbol}.SZ"
        fi
    else
        echo ""
    fi
}

# 匹配监控类型
match_type() {
    local topic="$1"
    
    if echo "$topic" | grep -qE "龙虎榜|机构席位|游资"; then
        echo "longhubang"
    elif echo "$topic" | grep -qE "产业链|供应链|上下游"; then
        echo "industry"
    elif echo "$topic" | grep -qE "公告|新闻|政策|事件"; then
        echo "news"
    elif echo "$topic" | grep -qE "股价|行情|涨跌|大盘|指数"; then
        echo "price"
    else
        echo "generic"
    fi
}

# 获取监控类型配置
get_config() {
    local type="$1"
    local topic="$2"
    local symbol="$3"
    
    case "$type" in
        "longhubang")
            echo "{
                \"category\": \"Data\",
                \"significance\": \"High\",
                \"source\": \"沪深交易所\",
                \"frequency_cron\": \"0 17 * * 1-5\",
                \"semantic_trigger\": \"出现在当日龙虎榜，机构净买入或游资大额参与\",
                \"search_query\": \"${topic} 龙虎榜 机构席位 游资\"
            }"
            ;;
        "industry")
            echo "{
                \"category\": \"Event\",
                \"significance\": \"Medium\",
                \"source\": \"综合信源\",
                \"frequency_cron\": \"0 9 * * 1-5\",
                \"semantic_trigger\": \"产业链上下游出现重要变化或政策支持\",
                \"search_query\": \"${topic} 产业链 政策 上下游\"
            }"
            ;;
        "news")
            echo "{
                \"category\": \"Event\",
                \"significance\": \"High\",
                \"source\": \"财联社\",
                \"frequency_cron\": \"0 */4 * * *\",
                \"semantic_trigger\": \"发布重大公告、新闻或政策变化\",
                \"search_query\": \"${topic} 公告 新闻 政策\"
            }"
            ;;
        "price")
            echo "{
                \"category\": \"Data\",
                \"significance\": \"High\",
                \"source\": \"东方财富\",
                \"frequency_cron\": \"0 17 * * 1-5\",
                \"semantic_trigger\": \"出现在当日龙虎榜或成交异常放大\",
                \"search_query\": \"${symbol} ${topic} 龙虎榜 成交 异动\"
            }"
            ;;
        *)
            echo "{
                \"category\": \"Event\",
                \"significance\": \"Medium\",
                \"source\": \"综合信源\",
                \"frequency_cron\": \"0 9 * * 1-5\",
                \"semantic_trigger\": \"出现重要新闻、公告或数据变化\",
                \"search_query\": \"${topic} 最新动态 公告 新闻\"
            }"
            ;;
    esac
}

# 检查是否已有相似监控（简化版）
check_existing_monitor() {
    local symbol="$1"
    local topic="$2"
    local monitors_dir="$HOME/.cuecue/users/${FEISHU_CHAT_ID:-default}/monitors"
    
    # 如果无法访问监控目录，直接返回
    [ -d "$monitors_dir" ] || return 1
    
    for f in "$monitors_dir"/*.json; do
        [ -f "$f" ] || continue
        
        # 快速检查：如果标的(symbol)相同且不为空，认为是重复
        if [ -n "$symbol" ]; then
            local existing_symbol
            existing_symbol=$(jq -r '.symbol // ""' "$f" 2>/dev/null)
            if [ "$existing_symbol" = "$symbol" ]; then
                echo "$(basename "$f")"
                return 0
            fi
        fi
    done
    
    return 1
}

# 主逻辑
echo "🔍 分析研究主题，生成监控建议..." >&2

# 提取信息
MONITOR_TYPE=$(match_type "$TASK_TOPIC")
SYMBOL=$(extract_symbol "$TASK_TOPIC")

# 检查是否已有相似监控
EXISTING_MONITOR=$(check_existing_monitor "$SYMBOL" "$TASK_TOPIC")
if [ -n "$EXISTING_MONITOR" ]; then
    echo "" >&2
    echo "⚠️  检测到已有相似监控项: $EXISTING_MONITOR" >&2
    echo "   建议先查看现有监控，避免重复创建。" >&2
    echo "   如需创建新的差异化监控，请描述具体需求。" >&2
fi

# 构建标题
TITLE="${TASK_TOPIC}动态监控"
[ -n "$SYMBOL" ] && TITLE="${TASK_TOPIC}(${SYMBOL})异动监控"

# 如果有重复，在标题中标注
[ -n "$EXISTING_MONITOR" ] && TITLE="${TITLE}(差异化)"

# 获取类型配置
TYPE_CONFIG=$(get_config "$MONITOR_TYPE" "$TASK_TOPIC" "$SYMBOL")

# 获取当前时间
NOW=$(date -Iseconds)

# 构建完整监控建议
jq -n \
    --arg title "$TITLE" \
    --arg symbol "$SYMBOL" \
    --arg reason "基于研究报告，${TASK_TOPIC}值得持续关注" \
    --arg report_url "$REPORT_URL" \
    --arg created_at "$NOW" \
    --arg start_date "$NOW" \
    --argjson type_config "$TYPE_CONFIG" \
    '{
        title: $title,
        symbol: $symbol,
        category: $type_config.category,
        significance: $type_config.significance,
        source: $type_config.source,
        frequency_cron: $type_config.frequency_cron,
        semantic_trigger: $type_config.semantic_trigger,
        search_query: $type_config.search_query,
        reason_for_user: $reason,
        report_url: $report_url,
        created_at: $created_at,
        start_date: $start_date,
        requires_confirmation: true
    }' > "$OUTPUT_FILE"

# 输出友好格式
echo "" >&2
echo "📊 建议监控项：" >&2
echo "  标题: $TITLE" >&2
echo "  类型: $(jq -r '.category' "$OUTPUT_FILE")" >&2
echo "  标的: ${SYMBOL:-无具体标的}" >&2
echo "  触发: $(jq -r '.semantic_trigger' "$OUTPUT_FILE")" >&2
echo "  频率: $(jq -r '.frequency_cron' "$OUTPUT_FILE")" >&2
echo "" >&2
echo "💡 回复 Y 创建此监控，或输入自定义监控需求" >&2

# 返回文件路径
echo "$OUTPUT_FILE"
