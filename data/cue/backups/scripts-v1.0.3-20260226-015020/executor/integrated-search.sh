#!/bin/bash
#
# Integrated Search Executor - QVeris + Tavily 整合执行器
# 根据监控类型自动选择最佳数据源

set -e

SOURCE="$1"
CONDITION="$2"
CATEGORY="${3:-Data}"  # Price, Data, Event
SYMBOL="${4:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 检查环境变量和依赖
check_env() {
    local deps_ok=true
    
    # 检查 Tavily（必需）
    if [ -z "$TAVILY_API_KEY" ]; then
        echo "❌ TAVILY_API_KEY 未配置" >&2
        echo "" >&2
        echo "请按以下步骤配置：" >&2
        echo "1. 访问 https://tavily.com 注册账号" >&2
        echo "2. 获取 API Key" >&2
        echo "3. 执行：echo 'TAVILY_API_KEY=your-key' >> ~/.openclaw/.env" >&2
        echo "4. 重启：openclaw gateway restart" >&2
        deps_ok=false
    fi
    
    # 检查 QVeris（可选）
    if [ -z "$QVERIS_API_KEY" ]; then
        echo "⚠️  QVERIS_API_KEY 未配置，将仅使用 Tavily" >&2
        echo "   （如需实时股价数据，建议配置 QVeris）" >&2
    fi
    
    if [ "$deps_ok" = false ]; then
        exit 1
    fi
}

# 使用 Tavily 搜索
search_with_tavily() {
    local query="$1"
    
    echo "   [Tavily] 搜索: $query" >&2
    
    local response
    response=$(curl -s -X POST "https://api.tavily.com/search" \
        -H "Content-Type: application/json" \
        -d "{
            \"api_key\": \"${TAVILY_API_KEY}\",
            \"query\": \"${query}\",
            \"search_depth\": \"advanced\",
            \"include_answer\": true,
            \"max_results\": 5,
            \"time_range\": \"day\"
        }" 2>/dev/null)
    
    # 提取答案
    local answer
    answer=$(echo "$response" | jq -r '.answer // empty' 2>/dev/null)
    
    if [ -n "$answer" ]; then
        echo "$answer"
        return 0
    else
        return 1
    fi
}

# 使用 QVeris 获取实时数据（curl 直接调用，无需 skill）
search_with_qveris() {
    local query="$1"
    local symbol="${2:-}"
    
    if [ -z "$QVERIS_API_KEY" ]; then
        echo "   [QVeris] API Key 未配置" >&2
        return 1
    fi
    
    echo "   [QVeris] 搜索工具: $query" >&2
    
    # Step 1: 搜索工具（curl 直接调用）
    local search_result
    search_result=$(curl -s -X POST "https://qveris.ai/api/v1/search" \
        -H "Authorization: Bearer ${QVERIS_API_KEY}" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"${query}\", \"limit\": 5}" 2>/dev/null)
    
    if [ $? -ne 0 ] || [ -z "$search_result" ]; then
        echo "   [QVeris] 搜索失败" >&2
        return 1
    fi
    
    # 提取第一个工具ID
    local tool_id
    tool_id=$(echo "$search_result" | jq -r '.tools[0].tool_id // empty' 2>/dev/null)
    local search_id
    search_id=$(echo "$search_result" | jq -r '.search_id // empty' 2>/dev/null)
    
    if [ -z "$tool_id" ] || [ -z "$search_id" ] || [ -z "$symbol" ]; then
        echo "   [QVeris] 未找到合适工具" >&2
        return 1
    fi
    
    echo "   [QVeris] 执行工具: $tool_id" >&2
    
    # Step 2: 执行工具（curl 直接调用）
    local result
    result=$(curl -s -X POST "https://qveris.ai/api/v1/tools/execute?tool_id=${tool_id}" \
        -H "Authorization: Bearer ${QVERIS_API_KEY}" \
        -H "Content-Type: application/json" \
        -d "{\"search_id\": \"${search_id}\", \"parameters\": {\"symbol\": \"${symbol}\"}, \"max_response_size\": 20480}" 2>/dev/null)
    
    if [ $? -eq 0 ] && [ -n "$result" ]; then
        local output
        output=$(echo "$result" | jq -r '.result // .data // .' 2>/dev/null)
        if [ -n "$output" ] && [ "$output" != "null" ]; then
            echo "$output"
            return 0
        fi
    fi
    
    return 1
}

# 主执行逻辑
main() {
    check_env
    
    # 构建搜索查询
    local query="${SOURCE} ${CONDITION}"
    query=$(echo "$query" | sed 's/[<>|=]/ /g' | tr -s ' ')
    
    echo "🔍 智能选择数据源..." >&2
    echo "   监控类型: ${CATEGORY}" >&2
    echo "   标的: ${SYMBOL:-无}" >&2
    
    local result=""
    local exit_code=1
    
    case "$CATEGORY" in
        "Price")
            # 股价监控：优先使用 QVeris 获取实时数据
            if [ -n "$SYMBOL" ] && [ -n "$QVERIS_API_KEY" ]; then
                echo "   策略: 使用 QVeris 获取实时股价" >&2
                result=$(search_with_qveris "stock price real-time" "$SYMBOL")
                exit_code=$?
            fi
            
            # QVeris 失败，回退到 Tavily
            if [ $exit_code -ne 0 ]; then
                echo "   策略: QVeris 不可用，使用 Tavily 搜索股价信息" >&2
                result=$(search_with_tavily "$query")
                exit_code=$?
            fi
            ;;
            
        "Data")
            # 数据监控（龙虎榜等）：使用 Tavily 搜索
            echo "   策略: 使用 Tavily 搜索数据信息" >&2
            result=$(search_with_tavily "$query")
            exit_code=$?
            ;;
            
        "Event"|*)
            # 事件监控：使用 Tavily 搜索新闻
            echo "   策略: 使用 Tavily 搜索新闻事件" >&2
            result=$(search_with_tavily "$query")
            exit_code=$?
            ;;
    esac
    
    # 输出结果
    if [ $exit_code -eq 0 ] && [ -n "$result" ]; then
        echo "$result"
        exit 0
    else
        echo "error: 未能获取有效数据" >&2
        exit 1
    fi
}

main
