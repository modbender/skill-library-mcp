#!/bin/bash
# Search Executor - 监控信息获取（Search层）
# 使用 Tavily API 获取监控所需信息

set -e

SOURCE="$1"
CONDITION="$2"

if [ -z "$SOURCE" ]; then
    echo "error: Source required" >&2
    exit 1
fi

# 构建搜索查询
# 将监控条件转化为搜索关键词
QUERY="$SOURCE $CONDITION"
QUERY=$(echo "$QUERY" | sed 's/[<>|=]/ /g' | tr -s ' ')

echo "   搜索查询: $QUERY" >&2

# 检查 API Key
if [ -z "$TAVILY_API_KEY" ]; then
    echo "error: TAVILY_API_KEY not configured" >&2
    exit 1
fi

# 调用 Tavily API
RESPONSE=$(curl -s -X POST "https://api.tavily.com/search" \
    -H "Content-Type: application/json" \
    -d "{
        \"api_key\": \"${TAVILY_API_KEY}\",
        \"query\": \"${QUERY}\",
        \"search_depth\": \"advanced\",
        \"include_answer\": true,
        \"max_results\": 5,
        \"time_range\": \"day\"
    }" 2>/dev/null)

# 检查响应
if echo "$RESPONSE" | jq -e '.error' >/dev/null 2>&1; then
    ERROR=$(echo "$RESPONSE" | jq -r '.error // "Unknown error"')
    echo "error: Tavily API error: $ERROR" >&2
    exit 1
fi

# 提取答案和结果
ANSWER=$(echo "$RESPONSE" | jq -r '.answer // empty')
RESULTS=$(echo "$RESPONSE" | jq -r '.results[] | "\(.title): \(.content | .[0:200])"' 2>/dev/null | head -5)

if [ -n "$ANSWER" ]; then
    echo "$ANSWER"
    echo ""
    echo "参考来源:"
    echo "$RESPONSE" | jq -r '.results[0].url // empty'
    exit 0
elif [ -n "$RESULTS" ]; then
    echo "$RESULTS"
    exit 0
else
    echo "error: No relevant information found" >&2
    exit 1
fi
