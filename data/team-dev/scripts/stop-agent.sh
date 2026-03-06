#!/bin/bash
# stop-agent.sh - Stop a running agent
# Skill: dev-team

set -e

# 引入公共函数库
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/utils.sh" ]]; then
    source "$SCRIPT_DIR/utils.sh"
else
    # 回退：定义基础函数
    get_root_dir() { echo "$(dirname "$(dirname "$SCRIPT_DIR")")"; }
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    NC='\033[0m'
fi

SKILL_DIR="$(cd "$(dirname "$SCRIPT_DIR")" && pwd)"
TASKS_FILE="$SKILL_DIR/assets/active-tasks.json"
TASKS_LOCK_DIR="$(get_tasks_lock_dir)"
trap 'release_file_lock "$TASKS_LOCK_DIR"' EXIT

# 检查依赖
check_dependency "tmux" "tmux" || exit 1

usage() {
    echo "Usage: $0 --branch <branch>"
    echo "       $0 --session <session-name>"
    echo "       $0 --all"
    echo ""
    echo "Options:"
    echo "  --branch     Branch name to stop"
    echo "  --session    Tmux session name to stop"
    echo "  --all        Stop all running agents"
    exit 1
}

BRANCH=""
SESSION=""
STOP_ALL=false

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --branch) BRANCH="$2"; shift 2 ;;
        --session) SESSION="$2"; shift 2 ;;
        --all) STOP_ALL=true; shift ;;
        -h|--help) usage ;;
        *) usage ;;
    esac
done

if [[ -z "$BRANCH" && -z "$SESSION" && "$STOP_ALL" != "true" ]]; then
    usage
fi

if [[ ! -f "$TASKS_FILE" ]]; then
    echo -e "${RED}Error: Tasks file not found${NC}"
    exit 1
fi

# 停止代理
STOP_ALL_PY="False"
if [[ "$STOP_ALL" == "true" ]]; then
    STOP_ALL_PY="True"
fi

acquire_file_lock "$TASKS_LOCK_DIR" 60 || exit 1
python3 << PYEOF
import json
import subprocess
import sys
import time

TASKS_FILE = '$TASKS_FILE'
STOP_BRANCH = '$BRANCH'
STOP_SESSION = '$SESSION'
STOP_ALL = $STOP_ALL_PY

with open(TASKS_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

stopped = []
failed = []

def maybe_mark_cleanup_eligible(agent):
    if agent.get('cleanupMode') != 'session_ttl':
        return
    ttl = agent.get('cleanupAfterSeconds', 3600)
    try:
        ttl = int(ttl if ttl is not None else 3600)
    except Exception:
        ttl = 3600
    ttl = max(0, ttl)
    agent['cleanupEligibleAt'] = int(time.time() * 1000) + ttl * 1000

for agent in data.get('agents', []):
    if agent.get('status') != 'running':
        continue

    session = agent.get('tmuxSession', '')
    branch = agent.get('branch', '')
    worktree = agent.get('worktree', '')

    # 判断是否需要停止
    should_stop = False
    if STOP_ALL:
        should_stop = True
    elif STOP_BRANCH and branch == STOP_BRANCH:
        should_stop = True
    elif STOP_SESSION and session == STOP_SESSION:
        should_stop = True

    if should_stop:
        # Kill tmux session
        result = subprocess.run(['tmux', 'kill-session', '-t', session], capture_output=True)
        if result.returncode == 0:
            agent['status'] = 'cancelled'
            agent['cancelledAt'] = int(subprocess.run(['date', '+%s'], capture_output=True).stdout.strip()) * 1000
            maybe_mark_cleanup_eligible(agent)
            stopped.append(branch)
            print(f"Stopped agent: {branch} (session: {session})")
        else:
            # If session is already gone, still allow registry cancellation.
            has_session = subprocess.run(['tmux', 'has-session', '-t', session], capture_output=True)
            if has_session.returncode != 0:
                agent['status'] = 'cancelled'
                agent['cancelledAt'] = int(subprocess.run(['date', '+%s'], capture_output=True).stdout.strip()) * 1000
                agent.setdefault('checks', {})['cancelledWithoutLiveSession'] = True
                maybe_mark_cleanup_eligible(agent)
                stopped.append(branch)
                print(f"Marked cancelled (session already dead): {branch}")
            else:
                failed.append(branch)
                print(f"Failed to stop agent: {branch}")

# 保存更新
with open(TASKS_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

if stopped:
    print(f"\nTotal stopped: {len(stopped)}")
if failed:
    print(f"Failed to stop: {len(failed)}")
    sys.exit(1)
PYEOF

echo -e "${GREEN}Done${NC}"
