#!/bin/bash
# get-hot.sh - 获取知乎热榜
# 用法: ./get-hot.sh [--limit N] [--format json|markdown|simple]

set -e

# 默认参数
LIMIT=50
FORMAT="markdown"

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --limit)
            LIMIT="$2"
            shift 2
            ;;
        --format)
            FORMAT="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# 数据源 URL
DATA_URL="https://raw.githubusercontent.com/towelong/zhihu-hot-questions/main/README.md"

# 获取数据
RAW_DATA=$(curl -s "$DATA_URL" 2>/dev/null)

if [[ -z "$RAW_DATA" ]]; then
    echo "Error: Cannot fetch data" >&2
    exit 1
fi

# 提取热榜列表
ITEMS=$(echo "$RAW_DATA" | sed -n '/<!-- BEGIN -->/,/<!-- END -->/p' | grep -E '^[0-9]+\.')

if [[ -z "$ITEMS" ]]; then
    echo "Error: No items found" >&2
    exit 1
fi

# 根据格式输出
case "$FORMAT" in
    json)
        echo "{"
        echo "  \"date\": \"$(date +%Y-%m-%d)\","
        echo "  \"source\": \"zhihu-hot-questions\","
        echo "  \"items\": ["
        
        FIRST=true
        echo "$ITEMS" | head -n "$LIMIT" | while IFS= read -r line; do
            # 解析标题和链接
            TITLE=$(echo "$line" | sed -E 's/^[0-9]+\. \[(.+)\]\(.+\)/\1/' | sed 's/"/\\"/g')
            URL=$(echo "$line" | sed -E 's/^[0-9]+\. \[.+\]\((.+)\)/\1/')
            RANK=$(echo "$line" | sed -E 's/^([0-9]+)\..*/\1/')
            
            if [[ "$FIRST" != "true" ]]; then
                echo ","
            fi
            FIRST=false
            
            echo -n "    {\"rank\": $RANK, \"title\": \"$TITLE\", \"url\": \"$URL\"}"
        done
        echo ""
        echo "  ]"
        echo "}"
        ;;
    
    markdown)
        echo "# 知乎热榜 - $(date +%Y-%m-%d)"
        echo ""
        echo "*数据来源: [zhihu-hot-questions](https://github.com/towelong/zhihu-hot-questions)*"
        echo ""
        
        echo "$ITEMS" | head -n "$LIMIT"
        
        echo ""
        echo "---"
        TOTAL=$(echo "$ITEMS" | wc -l)
        echo "*共 $TOTAL 条热门话题*"
        ;;
    
    simple)
        echo "$ITEMS" | head -n "$LIMIT"
        ;;
    
    *)
        echo "Error: Unknown format $FORMAT" >&2
        exit 1
        ;;
esac
