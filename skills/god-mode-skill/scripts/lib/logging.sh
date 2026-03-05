#!/usr/bin/env bash
# Logging utilities for god-mode
# Provides activity logging to ~/.god-mode/logs/

GOD_MODE_HOME="${GOD_MODE_HOME:-$HOME/.god-mode}"
LOG_DIR="$GOD_MODE_HOME/logs"
LOG_FILE="$LOG_DIR/activity.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Log a message with timestamp
# Usage: log_info "message"
log_info() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] INFO: $message" >> "$LOG_FILE"
}

# Log an error
# Usage: log_error "message"
log_error() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] ERROR: $message" >> "$LOG_FILE"
}

# Log a command execution
# Usage: log_command "sync" "github:user/repo"
log_command() {
    local command="$1"
    local target="${2:-}"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] COMMAND: god $command $target" >> "$LOG_FILE"
}

# Log sync operation
# Usage: log_sync_start "project_id"
log_sync_start() {
    local project_id="$1"
    log_info "SYNC START: $project_id"
}

# Usage: log_sync_complete "project_id" commits prs issues
log_sync_complete() {
    local project_id="$1"
    local commits="$2"
    local prs="$3"
    local issues="$4"
    log_info "SYNC COMPLETE: $project_id - $commits commits, $prs PRs, $issues issues"
}

# Log analysis operation
# Usage: log_analysis_start "project_id" "agent_gaps"
log_analysis_start() {
    local project_id="$1"
    local type="$2"
    log_info "ANALYSIS START: $project_id ($type)"
}

# Usage: log_analysis_complete "project_id" "agent_gaps" cache_hit
log_analysis_complete() {
    local project_id="$1"
    local type="$2"
    local from_cache="${3:-false}"
    if [[ "$from_cache" == "true" ]]; then
        log_info "ANALYSIS COMPLETE: $project_id ($type) [from cache]"
    else
        log_info "ANALYSIS COMPLETE: $project_id ($type) [fresh]"
    fi
}

# Rotate logs (keep last 30 days)
# Usage: log_rotate
log_rotate() {
    find "$LOG_DIR" -name "*.log" -mtime +30 -delete 2>/dev/null || true
    log_info "Log rotation complete"
}

# Get log file path
# Usage: get_log_file
get_log_file() {
    echo "$LOG_FILE"
}

# Tail recent activity
# Usage: log_tail [lines]
log_tail() {
    local lines="${1:-50}"
    tail -n "$lines" "$LOG_FILE" 2>/dev/null || echo "No logs yet"
}
