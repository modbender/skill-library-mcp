#!/bin/bash
# claude-fallback.sh — 当 Codex weekly limit 耗尽时，用 Claude AgentTeam 替代执行任务
# 用法: claude-fallback.sh <project_name> <project_dir> <task_message>
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
STATE_DIR="${HOME}/.autopilot/state"

PROJECT_NAME="${1:?用法: claude-fallback.sh <project_name> <project_dir> <task>}"
PROJECT_DIR="${2:?缺少 project_dir}"
TASK="${3:?缺少 task}"

log() { echo "[claude-fallback $(date '+%H:%M:%S')] $*"; }

if [ -f "${SCRIPT_DIR}/autopilot-lib.sh" ]; then
    # shellcheck disable=SC1091
    source "${SCRIPT_DIR}/autopilot-lib.sh"
else
    log "⚠️ autopilot-lib.sh not found, telegram notifications disabled"
    send_telegram() { :; }
fi

# 防并发
LOCK_DIR="${HOME}/.autopilot/locks/claude-${PROJECT_NAME}.lock.d"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
    log "⏭ 已有 Claude 任务在执行 ${PROJECT_NAME}，跳过"
    exit 0
fi
trap 'rm -rf "$LOCK_DIR"' EXIT

log "🤖 启动 Claude AgentTeam 替代 Codex: ${PROJECT_NAME}"
log "📋 任务: ${TASK:0:200}"
send_telegram "🤖 ${PROJECT_NAME}: Codex 额度不足，切换 Claude AgentTeam 执行任务
📋 ${TASK:0:200}"

# 读取项目的 CONVENTIONS.md 作为上下文
CONVENTIONS=""
if [ -f "${PROJECT_DIR}/CONVENTIONS.md" ]; then
    CONVENTIONS=$(head -100 "${PROJECT_DIR}/CONVENTIONS.md" 2>/dev/null || true)
fi

# 读取 prd-todo.md 了解当前进度
PRD_TODO=""
if [ -f "${PROJECT_DIR}/prd-todo.md" ]; then
    PRD_TODO=$(head -80 "${PROJECT_DIR}/prd-todo.md" 2>/dev/null || true)
fi

# 构造完整 prompt
FULL_PROMPT="你正在替代 Codex 为项目 ${PROJECT_NAME} 工作。项目目录: ${PROJECT_DIR}

## 任务
${TASK}

## 规则
1. 完成后必须 git add + git commit（遵循 conventional commits）
2. 不要 git push
3. 先阅读 CONVENTIONS.md 了解项目规范
4. 修改代码后确保不破坏现有功能
5. 每个逻辑变更一个 commit，不要把所有改动塞一个 commit"

if [ -n "$CONVENTIONS" ]; then
    FULL_PROMPT="${FULL_PROMPT}

## CONVENTIONS.md (摘要)
${CONVENTIONS:0:2000}"
fi

if [ -n "$PRD_TODO" ]; then
    FULL_PROMPT="${FULL_PROMPT}

## prd-todo.md (当前进度)
${PRD_TODO:0:1500}"
fi

# 记录开始时间
START_TS=$(date +%s)

# 用 openclaw agent 执行（在项目目录下运行，timeout 10分钟）
log "🚀 调用 openclaw agent..."
RESULT=$(cd "$PROJECT_DIR" && openclaw agent \
    -m "$FULL_PROMPT" \
    --local \
    --thinking low \
    --timeout 600 \
    --json \
    2>&1) || true

END_TS=$(date +%s)
DURATION=$(( END_TS - START_TS ))

# 检查是否有新 commit
NEW_COMMITS=$(git -C "$PROJECT_DIR" log --oneline --since="${START_TS}" 2>/dev/null | head -5 || true)

if [ -n "$NEW_COMMITS" ]; then
    COMMIT_COUNT=$(echo "$NEW_COMMITS" | wc -l | tr -dc '0-9')
    log "✅ Claude 完成任务，产出 ${COMMIT_COUNT} 个 commit (${DURATION}s)"
    send_telegram "✅ ${PROJECT_NAME}: Claude AgentTeam 完成！(${DURATION}s)
📝 ${COMMIT_COUNT} 个 commit:
${NEW_COMMITS}"

    # 标记 queue task 完成
    LATEST_HASH=$(git -C "$PROJECT_DIR" rev-parse --short HEAD 2>/dev/null || echo "")
    "${SCRIPT_DIR}/task-queue.sh" done "$PROJECT_NAME" "$LATEST_HASH" 2>/dev/null || true

    # 清理状态
    rm -f "${STATE_DIR}/stalled-alert-${PROJECT_NAME}"
    echo 0 > "${HOME}/.autopilot/state/nudge-count-${PROJECT_NAME}" 2>/dev/null || true
else
    log "⚠️ Claude 未产出 commit (${DURATION}s)"
    # 保存输出用于调试
    echo "$RESULT" > "${STATE_DIR}/claude-fallback-output-${PROJECT_NAME}.log" 2>/dev/null || true
    send_telegram "⚠️ ${PROJECT_NAME}: Claude AgentTeam 执行 ${DURATION}s 但无 commit，可能需手动检查
日志: ~/.autopilot/state/claude-fallback-output-${PROJECT_NAME}.log"
fi

log "🏁 Claude fallback 完成: ${PROJECT_NAME} (${DURATION}s)"
