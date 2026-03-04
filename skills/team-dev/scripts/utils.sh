#!/bin/bash
# utils.sh - 公共函数库
# Dev Team Skill 通用工具函数

# ============================================================
# 路径设置
# ============================================================

# 获取脚本所在目录的绝对路径
get_skill_dir() {
    echo "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
}

# 获取 skill 根目录（scripts 的父目录）
get_root_dir() {
    local script_dir="$(get_skill_dir)"
    echo "$(dirname "$script_dir")"
}

# ============================================================
# 依赖检查
# ============================================================

# 检查单个命令是否存在
check_dependency() {
    local cmd="$1"
    local name="${2:-$cmd}"
    if ! command -v "$cmd" &> /dev/null; then
        echo "Error: $name is required but not installed." >&2
        return 1
    fi
    return 0
}

# 批量检查依赖
check_dependencies() {
    local deps=("$@")
    local missing=()
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing+=("$dep")
        fi
    done
    if [[ ${#missing[@]} -gt 0 ]]; then
        echo "Error: Missing dependencies: ${missing[*]}" >&2
        return 1
    fi
    return 0
}

# 检查脚本所需的全部依赖
check_required_dependencies() {
    local deps=("tmux" "git" "gh" "python3")
    check_dependencies "${deps[@]}"
}

# ============================================================
# 仓库操作
# ============================================================

# 获取仓库默认分支
# 优先从本地仓库读取，否则尝试从 gh 获取，最后回退到 main
get_default_branch() {
    local repo="$1"

    if [[ -z "$repo" ]]; then
        echo "main"
        return
    fi

    # 优先从本地仓库获取
    if [[ -d "$repo" ]]; then
        local branch
        branch=$(git -C "$repo" symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
        if [[ -n "$branch" ]]; then
            echo "$branch"
            return
        fi

        # 尝试获取当前分支作为默认分支
        branch=$(git -C "$repo" rev-parse --abbrev-ref HEAD 2>/dev/null)
        if [[ -n "$branch" ]]; then
            echo "$branch"
            return
        fi
    fi

    # 尝试从 gh 获取
    if command -v gh &> /dev/null; then
        local default_branch
        default_branch=$(gh repo view "$repo" --json defaultBranchRef -q '.defaultBranchRef.name' 2>/dev/null)
        if [[ -n "$default_branch" ]]; then
            echo "$default_branch"
            return
        fi
    fi

    # 回退到 main
    echo "main"
}

# 检查仓库是否存在
repo_exists() {
    local repo="$1"
    [[ -d "$repo" ]]
}

# ============================================================
# 任务文件操作
# ============================================================

# 获取产出物目录路径
get_assets_dir() {
    local root_dir="$(get_root_dir)"
    echo "$root_dir/assets"
}

# 获取任务文件路径
get_tasks_file() {
    local root_dir="$(get_root_dir)"
    echo "$root_dir/assets/active-tasks.json"
}

# 获取任务文件锁目录路径（mkdir 原子锁）
get_tasks_lock_dir() {
    local tasks_file
    tasks_file="$(get_tasks_file)"
    echo "${tasks_file}.lock"
}

# 获取队列文件路径
get_queue_file() {
    local root_dir="$(get_root_dir)"
    echo "$root_dir/assets/tasks.json"
}

# 获取通知文件路径
get_notify_file() {
    local root_dir="$(get_root_dir)"
    echo "$root_dir/assets/notifications.json"
}

# 获取日志目录路径
get_logs_dir() {
    local root_dir="$(get_root_dir)"
    echo "$root_dir/assets/logs"
}

# ============================================================
# Agent 配置
# ============================================================

# 获取 Agent 配置文件路径
get_agent_config() {
    local root_dir="$(get_root_dir)"
    echo "$root_dir/config/agents.json"
}

# 获取用户配置文件路径
get_user_config() {
    local root_dir="$(get_root_dir)"
    echo "$root_dir/config/user.json"
}

# ============================================================
# 日志输出
# ============================================================

# 彩色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

# ============================================================
# 字符串处理
# ============================================================

# 清理分支名中的非法字符（用于 session 名称）
sanitize_branch_name() {
    echo "$1" | tr '/' '-' | tr ' ' '-' | tr '_' '-'
}

# ============================================================
# JSON 操作
# ============================================================

# 读取 JSON 字段（简单实现）
json_get() {
    local file="$1"
    local key="$2"
    python3 -c "
import json
with open('$file', 'r') as f:
    data = json.load(f)
keys = '$key'.split('.')
result = data
for k in keys:
    result = result.get(k, {})
print(result if result else '')
" 2>/dev/null
}

# ============================================================
# 文件锁（兼容 macOS，无 flock 依赖）
# ============================================================

acquire_file_lock() {
    local lock_dir="$1"
    local timeout_seconds="${2:-60}"
    local waited=0

    if [[ -z "$lock_dir" ]]; then
        log_error "acquire_file_lock requires lock_dir"
        return 1
    fi

    while true; do
        if mkdir "$lock_dir" 2>/dev/null; then
            {
                echo "pid=$$"
                echo "startedAt=$(date +%s)"
                echo "host=$(hostname 2>/dev/null || echo unknown)"
            } > "$lock_dir/meta" 2>/dev/null || true
            return 0
        fi

        # 尝试清理陈旧锁（持有进程不存在）
        if [[ -f "$lock_dir/meta" ]]; then
            local lock_pid
            lock_pid=$(sed -n 's/^pid=//p' "$lock_dir/meta" 2>/dev/null | head -n1)
            if [[ -n "$lock_pid" ]] && ! kill -0 "$lock_pid" 2>/dev/null; then
                rm -rf "$lock_dir" 2>/dev/null || true
                continue
            fi
        fi

        if [[ "$waited" -ge "$timeout_seconds" ]]; then
            log_error "Timeout acquiring lock: $lock_dir"
            return 1
        fi

        sleep 1
        waited=$((waited + 1))
    done
}

release_file_lock() {
    local lock_dir="$1"
    if [[ -n "$lock_dir" ]]; then
        rm -rf "$lock_dir" 2>/dev/null || true
    fi
}
