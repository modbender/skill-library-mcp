#!/bin/bash
# todoist_api.sh - Todoist REST API 封装脚本
# 用法: ./todoist_api.sh <method> <endpoint> [data]

set -e

# 配置变量（需要用户设置）
TODOIST_TOKEN="${TODOIST_TOKEN:-}"
API_BASE="https://api.todoist.com/api/v1"

# 检查 token
if [[ -z "$TODOIST_TOKEN" ]]; then
    echo "错误: TODOIST_TOKEN 未设置"
    echo "请设置环境变量: export TODOIST_TOKEN='your-token'"
    exit 1
fi

# 参数检查
if [[ $# -lt 2 ]]; then
    echo "用法: $0 <method> <endpoint> [data]"
    echo ""
    echo "示例:"
    echo "  $0 GET projects"
    echo "  $0 GET tasks?project_id=123"
    echo "  $0 POST tasks '{\"content\": \"新任务\", \"project_id\": \"123\"}'"
    echo "  $0 POST tasks/12345 '{\"content\": \"更新任务\"}'"
    exit 1
fi

METHOD="$1"
ENDPOINT="$2"
DATA="$3"

# 构建完整 URL
URL="${API_BASE}/${ENDPOINT}"

# 发送请求
if [[ -n "$DATA" ]]; then
    curl -s -X "$METHOD" \
        -H "Authorization: Bearer ${TODOIST_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "$DATA" \
        "$URL"
else
    curl -s -X "$METHOD" \
        -H "Authorization: Bearer ${TODOIST_TOKEN}" \
        "$URL"
fi
