#!/bin/bash
# prd-audit.sh — 自动 PRD 验收
# 由 watchdog 在 commit 数达到阈值时触发
# 检查每个项目的 prd-todo.md，验证已实现的项，更新标记

set -u

STATE_DIR="$HOME/.autopilot/state"
COMMIT_COUNT_DIR="$STATE_DIR/watchdog-commits"
LOG="$HOME/.autopilot/logs/watchdog.log"

PRD_AUDIT_THRESHOLD=50  # 每 50 commits 触发一次
PRD_AUDIT_INTERVAL=21600  # 或每 6 小时

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [prd-audit] $*" >> "$LOG"
}

now_ts() {
    date +%s
}

PROJECTS_CONF="$HOME/.autopilot/projects.conf"
[ ! -f "$PROJECTS_CONF" ] && exit 0

while IFS= read -r line; do
    [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
    
    window="${line%%:*}"
    project_dir="${line#*:}"
    safe=$(echo "$window" | tr -cd 'a-zA-Z0-9_-')
    
    # 检查是否需要审计
    audit_ts_file="${COMMIT_COUNT_DIR}/${safe}-last-audit-ts"
    audit_count_file="${COMMIT_COUNT_DIR}/${safe}-since-audit"
    
    last_audit_ts=$(cat "$audit_ts_file" 2>/dev/null || echo 0)
    since_audit=$(cat "$audit_count_file" 2>/dev/null || echo 0)
    time_since=$(($(now_ts) - last_audit_ts))
    
    should_audit=false
    [ "$since_audit" -ge "$PRD_AUDIT_THRESHOLD" ] && should_audit=true
    [ "$time_since" -ge "$PRD_AUDIT_INTERVAL" ] && [ "$since_audit" -gt 0 ] && should_audit=true
    
    [ "$should_audit" = "false" ] && continue
    
    prd_todo="${project_dir}/prd-todo.md"
    [ ! -f "$prd_todo" ] && continue
    
    log "📋 ${window}: PRD audit triggered (${since_audit} commits, ${time_since}s since last)"
    
    # 写触发标记，由 cron（OpenClaw 子 agent）来执行实际验收
    echo "${project_dir}" > "${STATE_DIR}/prd-audit-trigger-${safe}"
    
    # 更新时间戳和计数
    now_ts > "$audit_ts_file"
    echo 0 > "$audit_count_file"
    
    log "📋 ${window}: PRD audit trigger written"
    
done < "$PROJECTS_CONF"
