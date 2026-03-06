#!/bin/bash
# cleanup-worktrees.sh - Clean up merged worktrees
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
REPOS_BASE_DIR="$(dirname "$SKILL_DIR")"
TASKS_FILE="$SKILL_DIR/assets/active-tasks.json"
TASKS_LOCK_DIR="$(get_tasks_lock_dir)"
PRUNE_SCRIPT="$SKILL_DIR/scripts/prune-history.sh"
trap 'release_file_lock "$TASKS_LOCK_DIR"' EXIT

# 检查依赖
check_dependency "git" "Git" || exit 1

# 读取归档配置
ARCHIVE_ENABLED=true
AUTO_PRUNE_ON_CLEANUP=true
ARCHIVE_KEEP_DAYS=7
ARCHIVE_KEEP_COUNT=50
REMOVE_ORPHAN_MANAGED_WORKTREES=true
MAX_SESSION_TERMINAL_TTL_SECONDS=3600
MAX_SESSION_FAIL_CANCEL_TTL_SECONDS=900
if [[ -f "$SKILL_DIR/config/user.json" ]]; then
    CFG_ARCHIVE_ENABLED=$(python3 -c "import json; print(json.load(open('$SKILL_DIR/config/user.json')).get('archive', {}).get('enabled', True))" 2>/dev/null || echo "True")
    CFG_AUTO_PRUNE=$(python3 -c "import json; print(json.load(open('$SKILL_DIR/config/user.json')).get('archive', {}).get('autoPruneOnCleanup', True))" 2>/dev/null || echo "True")
    CFG_KEEP_DAYS=$(python3 -c "import json; print(json.load(open('$SKILL_DIR/config/user.json')).get('archive', {}).get('keepDays', 7))" 2>/dev/null || echo "7")
    CFG_KEEP_COUNT=$(python3 -c "import json; print(json.load(open('$SKILL_DIR/config/user.json')).get('archive', {}).get('keepCount', 50))" 2>/dev/null || echo "50")
    CFG_REMOVE_ORPHANS=$(python3 -c "import json; cfg=json.load(open('$SKILL_DIR/config/user.json')); print((cfg.get('cleanup') or {}).get('removeOrphanManagedWorktrees', True))" 2>/dev/null || echo "True")
    CFG_MAX_SESSION_TTL=$(python3 -c "import json; cfg=json.load(open('$SKILL_DIR/config/user.json')); print((cfg.get('cleanup') or {}).get('maxSessionTerminalTtlSeconds', 3600))" 2>/dev/null || echo "3600")
    CFG_MAX_FAIL_CANCEL_TTL=$(python3 -c "import json; cfg=json.load(open('$SKILL_DIR/config/user.json')); print((cfg.get('cleanup') or {}).get('maxSessionFailedCancelledTtlSeconds', 900))" 2>/dev/null || echo "900")

    [[ "$CFG_ARCHIVE_ENABLED" == "False" || "$CFG_ARCHIVE_ENABLED" == "false" ]] && ARCHIVE_ENABLED=false
    [[ "$CFG_AUTO_PRUNE" == "False" || "$CFG_AUTO_PRUNE" == "false" ]] && AUTO_PRUNE_ON_CLEANUP=false
    [[ "$CFG_KEEP_DAYS" =~ ^[0-9]+$ ]] && ARCHIVE_KEEP_DAYS="$CFG_KEEP_DAYS"
    [[ "$CFG_KEEP_COUNT" =~ ^[0-9]+$ ]] && ARCHIVE_KEEP_COUNT="$CFG_KEEP_COUNT"
    [[ "$CFG_REMOVE_ORPHANS" == "False" || "$CFG_REMOVE_ORPHANS" == "false" ]] && REMOVE_ORPHAN_MANAGED_WORKTREES=false
    [[ "$CFG_MAX_SESSION_TTL" =~ ^[0-9]+$ ]] && MAX_SESSION_TERMINAL_TTL_SECONDS="$CFG_MAX_SESSION_TTL"
    [[ "$CFG_MAX_FAIL_CANCEL_TTL" =~ ^[0-9]+$ ]] && MAX_SESSION_FAIL_CANCEL_TTL_SECONDS="$CFG_MAX_FAIL_CANCEL_TTL"
fi

echo "Cleaning up worktrees..."

# 获取需要清理的任务
if [[ -f "$TASKS_FILE" ]]; then
    acquire_file_lock "$TASKS_LOCK_DIR" 120 || exit 1
    python3 << EOF
import json
import subprocess
import os
import sys
import time

TASKS_FILE = '$TASKS_FILE'
REPOS_BASE = '$REPOS_BASE_DIR'
TASKS_DIR = os.path.dirname(os.path.abspath(TASKS_FILE))
REMOVE_ORPHANS = '$REMOVE_ORPHAN_MANAGED_WORKTREES'.lower() == 'true'
MAX_SESSION_TTL = int('$MAX_SESSION_TERMINAL_TTL_SECONDS')
MAX_FAIL_CANCEL_TTL = int('$MAX_SESSION_FAIL_CANCEL_TTL_SECONDS')

with open(TASKS_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

cleaned = []
repos_checked = {}
managed_worktrees = set()
now_ms = int(time.time() * 1000)

def should_cleanup_session_ttl(agent):
    if agent.get('cleanupMode') != 'session_ttl':
        return False
    if agent.get('status') not in ['done', 'failed', 'cancelled']:
        return False
    status = agent.get('status')
    base_ts = agent.get('completedAt') or agent.get('failedAt') or agent.get('cancelledAt') or agent.get('startedAt') or now_ms
    raw_ttl = agent.get('cleanupAfterSeconds', 3600)
    try:
        raw_ttl = int(raw_ttl if raw_ttl is not None else 3600)
    except Exception:
        raw_ttl = 3600
    if status in ('failed', 'cancelled'):
        ttl = min(max(0, raw_ttl), max(0, MAX_FAIL_CANCEL_TTL))
    else:
        ttl = min(max(0, raw_ttl), max(0, MAX_SESSION_TTL))
    capped_eligible_at = int(base_ts) + max(0, ttl) * 1000
    eligible_at = agent.get('cleanupEligibleAt')
    if eligible_at is None:
        eligible_at = capped_eligible_at
        agent['cleanupEligibleAt'] = eligible_at
    else:
        try:
            eligible_at = int(eligible_at)
        except Exception:
            eligible_at = capped_eligible_at
        if eligible_at > capped_eligible_at:
            eligible_at = capped_eligible_at
            agent['cleanupEligibleAt'] = eligible_at
    return int(eligible_at) <= now_ms

for agent in data.get('agents', []):
    repo = agent.get('repo', '')
    repo_path = agent.get('repoPath', os.path.join(REPOS_BASE, repo))
    wt = agent.get('worktree', '')
    if wt and not os.path.isabs(wt):
        wt = os.path.abspath(os.path.join(TASKS_DIR, wt))
    if wt:
        managed_worktrees.add(os.path.abspath(wt))

for agent in data.get('agents', []):
    if agent.get('status') in ['cleaned']:
        continue
    if agent.get('status') not in ['done', 'failed', 'merged', 'cancelled']:
        continue

    repo = agent.get('repo', '')
    repo_path = agent.get('repoPath', os.path.join(REPOS_BASE, repo))
    worktree = agent.get('worktree', '')
    branch = agent.get('branch', '')
    if worktree and not os.path.isabs(worktree):
        worktree = os.path.abspath(os.path.join(TASKS_DIR, worktree))

    if not repo or not os.path.exists(repo_path):
        continue
    if not branch:
        continue

    force_cleanup = should_cleanup_session_ttl(agent)
    merged_by_remote = (
        agent.get('status') == 'merged'
        or bool((agent.get('checks') or {}).get('prMerged'))
        or bool((agent.get('checks') or {}).get('prMergedAt'))
    )
    if force_cleanup:
        print(f"Session TTL cleanup eligible: {branch}")
        if os.path.exists(worktree):
            subprocess.run(['git', 'worktree', 'remove', '--force', worktree], cwd=repo_path)
            print(f"Removed worktree: {worktree}")
            cleaned.append(agent.get('id') or branch)

        # session 模式临时任务默认允许删除分支（多为 test/tmp 分支）
        subprocess.run(['git', 'branch', '-D', branch], cwd=repo_path, capture_output=True)
        print(f"Removed branch (force): {branch}")
        agent['status'] = 'cleaned'
        agent['cleanedAt'] = now_ms
        agent.setdefault('checks', {})['cleanedBy'] = 'session_ttl'
        continue

    # PR 已在 GitHub 合并时，允许不依赖本地 main 更新直接清理（避免本地未 fetch/pull 卡住）
    if merged_by_remote:
        print(f"Branch '{branch}' marked merged by PR state")

        if os.path.exists(worktree):
            subprocess.run(['git', 'worktree', 'remove', '--force', worktree], cwd=repo_path)
            print(f"Removed worktree: {worktree}")
            cleaned.append(agent.get('id') or branch)

        # 本地分支可能因未 fetch/main 未更新导致 -d 失败；此时允许强删（PR 已合并）
        del_proc = subprocess.run(['git', 'branch', '-d', branch], cwd=repo_path, capture_output=True, text=True)
        if del_proc.returncode != 0:
            subprocess.run(['git', 'branch', '-D', branch], cwd=repo_path, capture_output=True)
            print(f"Removed branch (force): {branch}")
        else:
            print(f"Removed branch: {branch}")

        agent['status'] = 'cleaned'
        agent['cleanedAt'] = now_ms
        agent.setdefault('checks', {})['cleanedBy'] = 'pr_merged'
        continue

    # 获取仓库默认分支（只获取一次）
    if repo not in repos_checked:
        try:
            # 尝试获取 symbolic-ref
            result = subprocess.run(
                ['git', 'symbolic-ref', 'refs/remotes/origin/HEAD'],
                cwd=repo_path, capture_output=True, text=True
            )
            if result.returncode == 0:
                default_branch = result.stdout.strip().replace('refs/remotes/origin/', '')
            else:
                # 尝试当前分支
                result = subprocess.run(
                    ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                    cwd=repo_path, capture_output=True, text=True
                )
                default_branch = result.stdout.strip() if result.returncode == 0 else 'main'

            repos_checked[repo] = default_branch
        except Exception:
            repos_checked[repo] = 'main'

    default_branch = repos_checked.get(repo, 'main')

    # 检查分支是否已合并到默认分支
    if branch == default_branch:
        continue

    result = subprocess.run(
        ['git', 'merge-base', '--is-ancestor', branch, default_branch],
        cwd=repo_path, capture_output=True, text=True
    )

    if result.returncode == 0:
        print(f"Branch '{branch}' is merged into '{default_branch}'")

        # 移除 worktree
        if os.path.exists(worktree):
            subprocess.run(['git', 'worktree', 'remove', '--force', worktree], cwd=repo_path)
            print(f"Removed worktree: {worktree}")
            cleaned.append(agent.get('id') or branch)

        # 移除分支
        subprocess.run(['git', 'branch', '-d', branch], cwd=repo_path, capture_output=True)
        print(f"Removed branch: {branch}")
        agent['status'] = 'cleaned'
        agent['cleanedAt'] = now_ms
        agent.setdefault('checks', {})['cleanedBy'] = 'merged_local'

# 更新活跃计数
data['activeCount'] = len([a for a in data.get('agents', []) if a.get('status') == 'running'])

with open(TASKS_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Cleaned {len(cleaned)} worktrees")

if REMOVE_ORPHANS:
    repos_to_scan = {}
    for agent in data.get('agents', []):
        repo = agent.get('repo', '')
        repo_path = agent.get('repoPath', os.path.join(REPOS_BASE, repo))
        if repo and repo_path and os.path.isdir(repo_path):
            repos_to_scan[repo] = repo_path

    orphan_cleaned = 0
    for repo, repo_path in repos_to_scan.items():
        proc = subprocess.run(['git', 'worktree', 'list', '--porcelain'], cwd=repo_path, capture_output=True, text=True)
        if proc.returncode != 0:
            continue
        current_path = None
        current_branch = None
        entries = []
        for line in (proc.stdout or '').splitlines():
            if line.startswith('worktree '):
                if current_path:
                    entries.append((current_path, current_branch))
                current_path = line.split(' ', 1)[1].strip()
                current_branch = None
            elif line.startswith('branch '):
                current_branch = line.split(' ', 1)[1].strip().replace('refs/heads/', '')
            elif line.strip() == '' and current_path:
                entries.append((current_path, current_branch))
                current_path = None
                current_branch = None
        if current_path:
            entries.append((current_path, current_branch))

        repo_real = os.path.realpath(repo_path)
        repo_parent = os.path.dirname(repo_real)
        expected_prefix = f"{os.path.basename(repo_real)}-"
        for wt_path, wt_branch in entries:
            if not wt_path:
                continue
            wt_real = os.path.realpath(wt_path)
            if wt_real == repo_real:
                continue
            if wt_real in managed_worktrees:
                continue
            if os.path.dirname(wt_real) != repo_parent:
                continue
            if not os.path.basename(wt_real).startswith(expected_prefix):
                continue
            # 避免删掉仍有 tmux 会话在跑但 registry 丢失的目录（保守）
            session_guess = None
            if wt_branch:
                session_suffix = wt_branch.replace('/', '-').replace(' ', '-').replace('_', '-')
                for agent_name in ('codex', 'claude', 'gemini', 'cursor'):
                    s = f'{agent_name}-{session_suffix}'
                    has = subprocess.run(['tmux', 'has-session', '-t', s], capture_output=True)
                    if has.returncode == 0:
                        session_guess = s
                        break
            if session_guess:
                continue

            rm_proc = subprocess.run(['git', 'worktree', 'remove', '--force', wt_real], cwd=repo_path, capture_output=True, text=True)
            if rm_proc.returncode == 0:
                orphan_cleaned += 1
                print(f"Removed orphan worktree: {wt_real}")
                if wt_branch:
                    subprocess.run(['git', 'branch', '-D', wt_branch], cwd=repo_path, capture_output=True)
            else:
                print(f"Warning: failed to remove orphan worktree: {wt_real} ({(rm_proc.stderr or rm_proc.stdout).strip()})")
    if orphan_cleaned:
        print(f"Cleaned orphan managed worktrees: {orphan_cleaned}")
EOF
else
    echo "No tasks file found"
fi

echo "Cleanup complete"
release_file_lock "$TASKS_LOCK_DIR"

if [[ "$ARCHIVE_ENABLED" == "true" && "$AUTO_PRUNE_ON_CLEANUP" == "true" && -x "$PRUNE_SCRIPT" ]]; then
    echo "Running history prune (keepDays=$ARCHIVE_KEEP_DAYS, keepCount=$ARCHIVE_KEEP_COUNT)..."
    "$PRUNE_SCRIPT" --keep-days "$ARCHIVE_KEEP_DAYS" --keep-count "$ARCHIVE_KEEP_COUNT" || \
        echo "Warning: prune-history failed"
fi
