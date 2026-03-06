#!/bin/bash
# UniFuncs Deep Search API 调用脚本
# 用法: ./deep-search.sh "搜索问题" [model]

QUERY="$1"
MODEL="${2:-s2}"

if [ -z "$UNIFUNCS_API_KEY" ]; then
    echo "错误: 请设置 UNIFUNCS_API_KEY 环境变量"
    exit 1
fi

if [ -z "$QUERY" ]; then
    echo "用法: ./deep-search.sh \"搜索问题\" [model:s2|s1]"
    exit 1
fi

curl -s -X POST "https://api.unifuncs.com/deepsearch/v1/chat/completions" \
    -H "Authorization: Bearer $UNIFUNCS_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"model\": \"$MODEL\", \"messages\": [{\"role\": \"user\", \"content\": \"$QUERY\"}], \"stream\": false}"
