#!/bin/bash
# sync_task.sh - 创建或更新 Todoist 任务并设置 section
# 用法: ./sync_task.sh <action> <task_json> [task_id]
# action: create | update

set -e

# 配置变量（需要用户设置）
TODOIST_TOKEN="${TODOIST_TOKEN:-}"
PROJECT_ID="${TODOIST_PROJECT_ID:-}"
SECTION_IN_PROGRESS="${SECTION_IN_PROGRESS:-}"  # 进行中 section ID
SECTION_WAITING="${SECTION_WAITING:-}"          # 等待中 section ID
SECTION_DONE="${SECTION_DONE:-}"                # 已完成 section ID

# 检查配置
if [[ -z "$TODOIST_TOKEN" ]]; then
    echo "错误: TODOIST_TOKEN 未设置"
    exit 1
fi

if [[ -z "$PROJECT_ID" ]]; then
    echo "错误: TODOIST_PROJECT_ID 未设置"
    echo "请设置: export TODOIST_PROJECT_ID='your-project-id'"
    exit 1
fi

# 参数检查
if [[ $# -lt 2 ]]; then
    echo "用法: $0 <action> <task_json> [task_id]"
    echo ""
    echo "action: create | update"
    echo ""
    echo "状态 section:"
    echo "  - in_progress: 进行中 🟡"
    echo "  - waiting: 等待中 🟠"
    echo "  - done: 已完成 🟢"
    echo ""
    echo "示例:"
    echo "  $0 create '{\"content\": \"新任务\", \"status\": \"in_progress\"}'"
    echo "  $0 update '{\"status\": \"done\"}' 12345"
    exit 1
fi

ACTION="$1"
TASK_JSON="$2"
TASK_ID="$3"

API_BASE="https://api.todoist.com/api/v1"

# 解析 status 并映射到 section_id
parse_status() {
    local json="$1"
    local status=$(echo "$json" | grep -o '"status"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/"status"[[:space:]]*:[[:space:]]*"\([^"]*\)"/\1/')

    case "$status" in
        "in_progress")
            echo "$SECTION_IN_PROGRESS"
            ;;
        "waiting")
            echo "$SECTION_WAITING"
            ;;
        "done")
            echo "$SECTION_DONE"
            ;;
        *)
            echo ""
            ;;
    esac
}

# 获取 section_id
SECTION_ID=$(parse_status "$TASK_JSON")

# 构建 API 请求
if [[ "$ACTION" == "create" ]]; then
    # 创建任务
    if [[ -n "$SECTION_ID" ]]; then
        TASK_JSON=$(echo "$TASK_JSON" | sed "s/\"status\"[[:space:]]*:[[:space:]]*\"[^\"]*\"/\"section_id\": \"$SECTION_ID\"/")
    fi

    # 添加 project_id
    if ! echo "$TASK_JSON" | grep -q '"project_id"'; then
        TASK_JSON=$(echo "$TASK_JSON" | sed "s/}/, \"project_id\": \"$PROJECT_ID\"}/")
    fi

    curl -s -X POST \
        -H "Authorization: Bearer ${TODOIST_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "$TASK_JSON" \
        "${API_BASE}/tasks"

elif [[ "$ACTION" == "update" ]]; then
    # 更新任务
    if [[ -z "$TASK_ID" ]]; then
        echo "错误: 更新任务需要提供 task_id"
        exit 1
    fi

    if [[ -n "$SECTION_ID" ]]; then
        TASK_JSON=$(echo "$TASK_JSON" | sed "s/\"status\"[[:space:]]*:[[:space:]]*\"[^\"]*\"/\"section_id\": \"$SECTION_ID\"/")
    fi

    curl -s -X POST \
        -H "Authorization: Bearer ${TODOIST_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "$TASK_JSON" \
        "${API_BASE}/tasks/${TASK_ID}"

else
    echo "错误: 未知操作 '$ACTION'"
    echo "支持的操作: create, update"
    exit 1
fi
