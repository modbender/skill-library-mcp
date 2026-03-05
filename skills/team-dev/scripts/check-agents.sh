#!/bin/bash
# check-agents.sh - Monitor running agents
# Skill: dev-team

set -e

# 引入公共函数库
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/utils.sh" ]]; then
    source "$SCRIPT_DIR/utils.sh"
else
    # 回退：定义基础函数
    get_root_dir() { echo "$(dirname "$(dirname "$SCRIPT_DIR")")"; }
fi

SKILL_DIR="$(cd "$(dirname "$SCRIPT_DIR")" && pwd)"
REPOS_BASE_DIR="$(dirname "$SKILL_DIR")"
TASKS_FILE="$SKILL_DIR/assets/active-tasks.json"
TASKS_LOCK_DIR="$(get_tasks_lock_dir)"
NOTIFY_FILE="$SKILL_DIR/assets/notifications.json"
AUTO_CLEANUP_ON_CHECK=true
AUTO_PRUNE_ON_CHECK=true
AUTO_PRUNE_QUEUE_ON_CHECK=true
trap 'release_file_lock "$TASKS_LOCK_DIR"' EXIT

# 从配置文件读取重试设置
MAX_RETRIES=3
RETRY_DELAY=60
AUTO_MERGE_DEFAULT=0
if [[ -f "$SKILL_DIR/config/user.json" ]]; then
    CONFIG_RETRY=$(python3 -c "import json; print(json.load(open('$SKILL_DIR/config/user.json')).get('retry', {}).get('maxAttempts', 3))" 2>/dev/null)
    [[ -n "$CONFIG_RETRY" ]] && MAX_RETRIES=$CONFIG_RETRY
    CONFIG_RETRY_DELAY=$(python3 -c "import json; print(json.load(open('$SKILL_DIR/config/user.json')).get('retry', {}).get('delaySeconds', 60))" 2>/dev/null)
    [[ -n "$CONFIG_RETRY_DELAY" ]] && RETRY_DELAY=$CONFIG_RETRY_DELAY
    CONFIG_AUTO_MERGE=$(python3 -c "import json; print(1 if json.load(open('$SKILL_DIR/config/user.json')).get('pr', {}).get('autoMerge', False) else 0)" 2>/dev/null)
    [[ -n "$CONFIG_AUTO_MERGE" ]] && AUTO_MERGE_DEFAULT=$CONFIG_AUTO_MERGE
    CFG_AUTO_CLEANUP_ON_CHECK=$(python3 -c "import json; cfg=json.load(open('$SKILL_DIR/config/user.json')); print((cfg.get('cleanup') or {}).get('autoCleanup', True))" 2>/dev/null || echo "True")
    CFG_AUTO_PRUNE_ON_CHECK=$(python3 -c "import json; cfg=json.load(open('$SKILL_DIR/config/user.json')); print((cfg.get('archive') or {}).get('autoPruneOnCleanup', True))" 2>/dev/null || echo "True")
    CFG_AUTO_PRUNE_QUEUE_ON_CHECK=$(python3 -c "import json; cfg=json.load(open('$SKILL_DIR/config/user.json')); print((cfg.get('queueArchive') or {}).get('autoPruneOnCheck', True))" 2>/dev/null || echo "True")
    [[ "$CFG_AUTO_CLEANUP_ON_CHECK" == "False" || "$CFG_AUTO_CLEANUP_ON_CHECK" == "false" ]] && AUTO_CLEANUP_ON_CHECK=false
    [[ "$CFG_AUTO_PRUNE_ON_CHECK" == "False" || "$CFG_AUTO_PRUNE_ON_CHECK" == "false" ]] && AUTO_PRUNE_ON_CHECK=false
    [[ "$CFG_AUTO_PRUNE_QUEUE_ON_CHECK" == "False" || "$CFG_AUTO_PRUNE_QUEUE_ON_CHECK" == "false" ]] && AUTO_PRUNE_QUEUE_ON_CHECK=false
fi

# 检查依赖
check_required_dependencies 2>/dev/null || {
    echo "Warning: Some dependencies are missing, but continuing..."
}

echo "Checking agents..."

if [[ ! -f "$TASKS_FILE" ]]; then
    echo "No tasks file found"
    exit 0
fi

# 检查每个运行中的代理
acquire_file_lock "$TASKS_LOCK_DIR" 120 || exit 1
TEMP_FILE=$(mktemp)
cp "$TASKS_FILE" "$TEMP_FILE"

LIB_DIR="$SCRIPT_DIR/lib"
RC=1
if [[ -x "$LIB_DIR/check_agents.py" ]]; then
    python3 "$LIB_DIR/check_agents.py" \
        --tasks-file "$TEMP_FILE" \
        --notify-file "$NOTIFY_FILE" \
        --repos-base "$REPOS_BASE_DIR" \
        --max-retries "$MAX_RETRIES" \
        --retry-delay "$RETRY_DELAY" \
        --auto-merge-default "$AUTO_MERGE_DEFAULT"
    RC=$?
else
    echo "Error: $LIB_DIR/check_agents.py not found or not executable" >&2
    rm -f "$TEMP_FILE"
    exit 1
fi

if [[ $RC -eq 0 ]]; then
    mv "$TEMP_FILE" "$TASKS_FILE"
else
    rm -f "$TEMP_FILE"
    exit 1
fi

# 释放 active-tasks 锁后再触发后续维护脚本，避免自锁
release_file_lock "$TASKS_LOCK_DIR"

if [[ "$AUTO_CLEANUP_ON_CHECK" == "true" && -x "$SKILL_DIR/scripts/cleanup-worktrees.sh" ]]; then
    echo "Auto cleanup after check-agents..."
    "$SKILL_DIR/scripts/cleanup-worktrees.sh" || echo "Warning: cleanup-worktrees.sh failed"
elif [[ "$AUTO_PRUNE_ON_CHECK" == "true" && -x "$SKILL_DIR/scripts/prune-history.sh" ]]; then
    echo "Auto prune after check-agents..."
    "$SKILL_DIR/scripts/prune-history.sh" || echo "Warning: prune-history.sh failed"
fi

if [[ -x "$SKILL_DIR/scripts/sync-queue-status.sh" ]]; then
    echo "Sync queue status after check-agents..."
    "$SKILL_DIR/scripts/sync-queue-status.sh" || echo "Warning: sync-queue-status.sh failed"
fi

if [[ "$AUTO_PRUNE_QUEUE_ON_CHECK" == "true" && -x "$SKILL_DIR/scripts/prune-queue-history.sh" ]]; then
    echo "Prune queue history after check-agents..."
    "$SKILL_DIR/scripts/prune-queue-history.sh" || echo "Warning: prune-queue-history.sh failed"
fi
