#!/bin/bash
# Skill 搜索脚本

QUERY="$1"
LIMIT="${2:-10}"

if [ -z "$QUERY" ]; then
    echo "用法: search.sh <关键词> [数量]"
    exit 1
fi

echo "🔍 搜索: $QUERY"
echo "================================"

clawhub search "$QUERY" --limit "$LIMIT"
