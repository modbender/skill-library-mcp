#!/bin/bash
# add_comment.sh - 为 Todoist 任务添加进度评论
# 用法: ./add_comment.sh <task_id> <comment>

set -e

# 配置变量
TODOIST_TOKEN="${TODOIST_TOKEN:-}"

# 检查配置
if [[ -z "$TODOIST_TOKEN" ]]; then
    echo "错误: TODOIST_TOKEN 未设置"
    echo "请设置: export TODOIST_TOKEN='your-token'"
    exit 1
fi

# 参数检查
if [[ $# -lt 2 ]]; then
    echo "用法: $0 <task_id> <comment>"
    echo ""
    echo "示例:"
    echo "  $0 12345 '已完成数据收集'"
    echo "  $0 12345 '遇到问题：API 超时，正在重试'"
    exit 1
fi

TASK_ID="$1"
COMMENT="$2"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

API_BASE="https://api.todoist.com/rest/v2"

# 构建评论 JSON（包含时间戳）
COMMENT_JSON=$(cat <<EOF
{
  "task_id": "$TASK_ID",
  "content": "[$TIMESTAMP] $COMMENT"
}
EOF
)

# 发送请求
curl -s -X POST \
    -H "Authorization: Bearer ${TODOIST_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "$COMMENT_JSON" \
    "${API_BASE}/comments"

echo ""
echo "✅ 评论已添加到任务 $TASK_ID"
