#!/bin/bash
# spotlight-search.sh - 使用 macOS Spotlight 搜索文件
# 用法: spotlight-search.sh <directory> <query> [--limit N]

set -euo pipefail

# 忽略 SIGPIPE (当 head 提前退出时)
trap '' PIPE

show_usage() {
    cat << EOF
Usage: spotlight-search.sh <directory> <query> [--limit N]

Arguments:
  <directory>  Directory path to search
  <query>      Search query
  --limit N    Maximum number of results (default: 20)

Examples:
  spotlight-search.sh ~/Documents "project plan"
  spotlight-search.sh ~/research "machine learning" --limit 10
EOF
}

# 参数解析
if [ $# -lt 2 ]; then
    show_usage
    exit 1
fi

DIRECTORY="$1"
QUERY="$2"
LIMIT=20

# 检查可选参数
shift 2
while [ $# -gt 0 ]; do
    case "$1" in
        --limit)
            LIMIT="$2"
            shift 2
            ;;
        *)
            echo "Unknown argument: $1" >&2
            show_usage
            exit 1
            ;;
    esac
done

# Check if directory exists
if [ ! -d "$DIRECTORY" ]; then
    echo "Error: Directory not found: $DIRECTORY" >&2
    exit 1
fi

# Expand path (handle ~ etc)
DIRECTORY=$(cd "$DIRECTORY" && pwd)

# Search using mdfind
# -onlyin: limit search scope
# 2>/dev/null: ignore error messages
echo "🔍 Searching in $DIRECTORY for: $QUERY"
echo ""

results=$(mdfind -onlyin "$DIRECTORY" "$QUERY" 2>/dev/null | head -n "$LIMIT")

if [ -z "$results" ]; then
    echo "❌ No results found"
    exit 0
fi

# Count results
count=$(echo "$results" | wc -l | tr -d ' ')
echo "✅ Found $count results (showing up to $LIMIT):"
echo ""

# Output results
echo "$results" | while IFS= read -r file; do
    # 获取文件类型
    ext="${file##*.}"
    
    # 获取文件大小
    if [ -f "$file" ]; then
        size=$(ls -lh "$file" | awk '{print $5}')
        echo "📄 $file [$ext, $size]"
    elif [ -d "$file" ]; then
        echo "📁 $file/"
    else
        echo "❓ $file"
    fi
done

exit 0
