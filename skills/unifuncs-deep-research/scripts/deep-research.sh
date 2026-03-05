#!/bin/bash
# UniFuncs Deep Research API 调用脚本
# 用法: ./deep-research.sh "研究主题" [model] [output_type]

QUERY="$1"
MODEL="${2:-u2}"
OUTPUT_TYPE="${3:-report}"

if [ -z "$UNIFUNCS_API_KEY" ]; then
    echo "错误: 请设置 UNIFUNCS_API_KEY 环境变量"
    exit 1
fi

if [ -z "$QUERY" ]; then
    echo "用法: ./deep-research.sh \"研究主题\" [model:u2|u1|u1-pro] [output_type:report|summary|wechat-article]"
    exit 1
fi

curl -s -X POST "https://api.unifuncs.com/deepresearch/v1/chat/completions" \
    -H "Authorization: Bearer $UNIFUNCS_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"model\": \"$MODEL\", \"messages\": [{\"role\": \"user\", \"content\": \"$QUERY\"}], \"output_type\": \"$OUTPUT_TYPE\", \"stream\": false}"
