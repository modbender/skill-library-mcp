#!/bin/bash
# spawn-agent.sh - Spawn a coding agent for a task
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
    sanitize_branch_name() { echo "$1" | tr '/' '-' | tr ' ' '-' | tr '_' '-'; }
fi

# 使用公共函数获取路径
SKILL_DIR="$(get_root_dir)"
REPOS_BASE_DIR="$(dirname "$SKILL_DIR")"  # skill 上级目录作为仓库根目录
TASKS_FILE="$SKILL_DIR/assets/active-tasks.json"
TASKS_LOCK_DIR="$(get_tasks_lock_dir)"
LOGS_DIR="$SKILL_DIR/logs"
LAUNCHERS_DIR="$LOGS_DIR/launchers"
trap 'release_file_lock "$TASKS_LOCK_DIR"' EXIT

# 从配置文件读取最大代理数
MAX_AGENTS=5
COMPLETION_MODE="pr"
CLEANUP_AFTER_SECONDS=""
AGENT_MODEL=""
CURSOR_MODE="dev"
PROMPT_B64_INPUT=""
REQUESTED_AGENT=""
AUTO_SELECTION_REASON=""
AUTO_MERGE=0
MERGE_METHOD="squash"
AGENT_PHASE="build"
PROTECTED_BRANCHES_CSV="main,master"
if [[ -f "$SKILL_DIR/config/user.json" ]]; then
    CONFIG_MAX=$(python3 -c "import json; print(json.load(open('$SKILL_DIR/config/user.json')).get('maxAgents', 5))" 2>/dev/null)
    [[ -n "$CONFIG_MAX" ]] && MAX_AGENTS=$CONFIG_MAX
    CONFIG_PROTECTED_BRANCHES=$(python3 -c "import json; import sys; cfg=json.load(open('$SKILL_DIR/config/user.json')); arr=((cfg.get('workflow') or {}).get('protectedBranches')) or ['main','master']; print(','.join(arr))" 2>/dev/null)
    [[ -n "$CONFIG_PROTECTED_BRANCHES" ]] && PROTECTED_BRANCHES_CSV="$CONFIG_PROTECTED_BRANCHES"
fi

# 检查必需依赖
check_required_dependencies 2>/dev/null || {
    echo -e "${RED}Error: Missing required dependencies${NC}"
    exit 1
}

usage() {
    echo "Usage: $0 --agent <codex|claude|gemini|cursor|auto> (--repo <repo> | --repo-path <path>) --branch <branch> --description <desc> --prompt <prompt> [--completion-mode pr|session]"
    echo "       $0 --agent <codex|claude|gemini|cursor|auto> (--repo <repo> | --repo-path <path>) --branch <branch> --description <desc> --prompt-file <file> [--completion-mode pr|session]"
    echo ""
    echo "Options:"
    echo "  --agent        Agent type: codex, claude, gemini, cursor, auto"
    echo "  --repo         Repository name (in repos root directory)"
    echo "  --repo-path    Absolute or relative repository path (overrides --repo lookup)"
    echo "  --branch       Branch name"
    echo "  --description  Task description"
    echo "  --prompt       Prompt text (use quotes for multi-line)"
    echo "  --prompt-file  Read prompt from file (recommended for shell-special chars)"
    echo "  --prompt-b64   Base64 encoded prompt (safe for automation)"
    echo "  --agent-model  Override model name for selected agent"
    echo "  --cursor-mode Cursor run mode: dev|plan (cursor only, default: dev)"
    echo "  --phase       Agent selection phase: build|review|fixup (default: build)"
    echo "  --completion-mode  Completion rule: pr (default) or session"
    echo "  --auto-merge   (pr mode) Trigger gh pr merge --auto after checks/review pass"
    echo "  --merge-method (pr mode) merge method: squash|merge|rebase (default: squash)"
    echo "  --cleanup-after-seconds  TTL for temp worktree cleanup (session mode default: 3600)"
    exit 1
}

# 解析参数
PROMPT=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --agent) AGENT="$2"; shift 2 ;;
        --repo) REPO="$2"; shift 2 ;;
        --repo-path) REPO_PATH_INPUT="$2"; shift 2 ;;
        --branch) BRANCH="$2"; shift 2 ;;
        --description) DESCRIPTION="$2"; shift 2 ;;
        --agent-model) AGENT_MODEL="$2"; shift 2 ;;
        --cursor-mode) CURSOR_MODE="$2"; shift 2 ;;
        --phase) AGENT_PHASE="$2"; shift 2 ;;
        --completion-mode) COMPLETION_MODE="$2"; shift 2 ;;
        --auto-merge) AUTO_MERGE=1; shift 1 ;;
        --merge-method) MERGE_METHOD="$2"; shift 2 ;;
        --cleanup-after-seconds) CLEANUP_AFTER_SECONDS="$2"; shift 2 ;;
        --prompt) PROMPT="$2"; shift 2 ;;
        --prompt-b64) PROMPT_B64_INPUT="$2"; shift 2 ;;
        --prompt-file)
            if [[ ! -f "$2" ]]; then
                echo -e "${RED}Error: Prompt file not found: $2${NC}"
                exit 1
            fi
            PROMPT=$(cat "$2")
            shift 2
            ;;
        *) usage ;;
    esac
done

# 验证必需参数
if [[ -z "$AGENT" || -z "$BRANCH" || -z "$DESCRIPTION" ]]; then
    usage
fi

if [[ ! "$AGENT_PHASE" =~ ^(build|review|fixup)$ ]]; then
    echo -e "${RED}Error: --phase must be build|review|fixup${NC}"
    exit 1
fi
if [[ ! "$CURSOR_MODE" =~ ^(dev|plan)$ ]]; then
    echo -e "${RED}Error: --cursor-mode must be dev|plan${NC}"
    exit 1
fi
if [[ -z "$REPO" && -z "$REPO_PATH_INPUT" ]]; then
    echo -e "${RED}Error: --repo or --repo-path is required${NC}"
    usage
fi

# 如果没有提供 prompt，检查是否有内容
if [[ -z "$PROMPT" && -n "$PROMPT_B64_INPUT" ]]; then
    PROMPT=$(PROMPT_B64_IN="$PROMPT_B64_INPUT" python3 - <<'PYEOF'
import base64, os
raw = os.environ.get("PROMPT_B64_IN", "")
try:
    print(base64.b64decode(raw).decode("utf-8"), end="")
except Exception:
    pass
PYEOF
)
fi
if [[ -z "$PROMPT" ]]; then
    echo -e "${RED}Error: --prompt, --prompt-file, or --prompt-b64 is required${NC}"
    usage
fi

# 禁止 subagent 在受保护分支上直接工作（避免直接提交 main/master）
IFS=',' read -r -a _PROTECTED_BRANCHES <<< "$PROTECTED_BRANCHES_CSV"
for _pb in "${_PROTECTED_BRANCHES[@]}"; do
    _pb_trimmed="$(echo "$_pb" | xargs)"
    [[ -z "$_pb_trimmed" ]] && continue
    if [[ "$BRANCH" == "$_pb_trimmed" ]]; then
        echo -e "${RED}Error: Branch '$BRANCH' is protected for subagent tasks. Use a feature branch and PR flow.${NC}"
        exit 1
    fi
done

# 验证 agent 类型
case $AGENT in
    codex|claude|gemini|cursor|auto) ;;
    *) echo -e "${RED}Error: Invalid agent type: $AGENT${NC}"; usage ;;
esac

REQUESTED_AGENT="$AGENT"
case $COMPLETION_MODE in
    pr|session) ;;
    *) echo -e "${RED}Error: Invalid --completion-mode: $COMPLETION_MODE${NC}"; usage ;;
esac
case $MERGE_METHOD in
    squash|merge|rebase) ;;
    *) echo -e "${RED}Error: Invalid --merge-method: $MERGE_METHOD${NC}"; usage ;;
esac
if [[ -n "$CLEANUP_AFTER_SECONDS" && ! "$CLEANUP_AFTER_SECONDS" =~ ^[0-9]+$ ]]; then
    echo -e "${RED}Error: --cleanup-after-seconds must be a non-negative integer${NC}"
    exit 1
fi
if [[ -z "$CLEANUP_AFTER_SECONDS" && "$COMPLETION_MODE" == "session" ]]; then
    CLEANUP_AFTER_SECONDS=3600
fi
if [[ "$COMPLETION_MODE" != "pr" && "$AUTO_MERGE" -eq 1 ]]; then
    echo -e "${YELLOW}Warning: --auto-merge only applies to completion-mode=pr; ignoring${NC}"
    AUTO_MERGE=0
fi

resolve_auto_agent() {
    local rec_script="$SCRIPT_DIR/recommend-agent.sh"
    if [[ ! -f "$rec_script" ]]; then
        AGENT="codex"
        AUTO_SELECTION_REASON="recommend-agent.sh missing -> codex"
        return
    fi

    local tmp_prompt_file
    tmp_prompt_file=$(mktemp)
    printf '%s' "$PROMPT" > "$tmp_prompt_file"
    local rec_json
    rec_json=$("$rec_script" --description "$DESCRIPTION" --prompt-file "$tmp_prompt_file" --phase "$AGENT_PHASE" --format json 2>/dev/null || true)
    rm -f "$tmp_prompt_file"

    if [[ -z "$rec_json" ]]; then
        AGENT="codex"
        AUTO_SELECTION_REASON="recommendation failed -> codex"
        return
    fi

    AGENT=$(printf '%s' "$rec_json" | python3 -c "import sys,json; print(json.load(sys.stdin).get('recommendedAgent','codex'))" 2>/dev/null || echo codex)
    if [[ -z "$AGENT_MODEL" ]]; then
        AGENT_MODEL=$(printf '%s' "$rec_json" | python3 -c "import sys,json; print(json.load(sys.stdin).get('recommendedModel') or '')" 2>/dev/null || true)
    fi
    AUTO_SELECTION_REASON=$(printf '%s' "$rec_json" | python3 -c "import sys,json; d=json.load(sys.stdin); r=(d.get('ranking') or [{}])[0]; print('; '.join((r.get('reasons') or [])[:4]))" 2>/dev/null || true)
}

check_agent_health() {
    local agent_type="$1"
    case "$agent_type" in
        codex)
            command -v codex >/dev/null 2>&1 || { echo "codex CLI not found" >&2; return 1; }
            codex --version >/dev/null 2>&1 || { echo "codex --version failed" >&2; return 1; }
            ;;
        claude)
            command -v claude >/dev/null 2>&1 || { echo "claude CLI not found" >&2; return 1; }
            claude --version >/dev/null 2>&1 || { echo "claude --version failed" >&2; return 1; }
            ;;
        gemini)
            command -v gemini >/dev/null 2>&1 || { echo "gemini CLI not found" >&2; return 1; }
            ;;
        cursor)
            command -v cursor >/dev/null 2>&1 || { echo "cursor CLI not found" >&2; return 1; }
            local cursor_status
            cursor_status=$(cursor agent status 2>&1 || true)
            if echo "$cursor_status" | grep -qi "not logged in"; then
                # 某些环境（非交互 shell / keychain 可见性差异）会误报未登录，tmux 场景再探测一次
                if command -v tmux >/dev/null 2>&1; then
                    local probe_session="teamdev-cursor-probe-$$"
                    local probe_file="/tmp/${probe_session}.txt"
                    tmux new-session -d -s "$probe_session" "cursor agent status > '$probe_file' 2>&1" >/dev/null 2>&1 || true
                    sleep 2
                    local tmux_cursor_status=""
                    [[ -f "$probe_file" ]] && tmux_cursor_status=$(cat "$probe_file" 2>/dev/null || true)
                    tmux kill-session -t "$probe_session" >/dev/null 2>&1 || true
                    rm -f "$probe_file" >/dev/null 2>&1 || true
                    if ! echo "$tmux_cursor_status" | grep -qi "not logged in"; then
                        return 0
                    fi
                fi
                echo "cursor agent not logged in (run: cursor agent login)" >&2
                return 1
            fi
            ;;
    esac
    return 0
}

if [[ "$AGENT" == "auto" ]]; then
    resolve_auto_agent
fi

if [[ "$AGENT" != "cursor" && "$CURSOR_MODE" != "dev" ]]; then
    echo -e "${YELLOW}Warning: --cursor-mode only applies to cursor; ignoring for $AGENT${NC}"
    CURSOR_MODE="dev"
fi
if [[ "$AGENT" == "cursor" && "$CURSOR_MODE" == "plan" ]]; then
    if [[ -n "$AGENT_MODEL" && "$AGENT_MODEL" != "gpt-5.3-codex" ]]; then
        echo -e "${YELLOW}Warning: cursor plan mode requires gpt-5.3-codex; overriding --agent-model${NC}"
    fi
    AGENT_MODEL="gpt-5.3-codex"
fi

# 检查 agentPolicy（enabledAgents + phaseAllowedAgents）
if [[ -f "$SKILL_DIR/config/user.json" ]]; then
    POLICY_CHECK=$(python3 - <<PYEOF
import json
cfg = json.load(open("$SKILL_DIR/config/user.json", "r", encoding="utf-8"))
policy = cfg.get("agentPolicy") or {}
enabled = policy.get("enabledAgents")
phase_allowed = (policy.get("phaseAllowedAgents") or {}).get("$AGENT_PHASE")
agent = "$AGENT"

if isinstance(enabled, list) and enabled:
    if agent not in enabled:
        print(f"disabled:{agent}")
        raise SystemExit(2)

if isinstance(phase_allowed, list) and phase_allowed:
    if agent not in phase_allowed:
        print(f"phase_disallowed:{agent}:$AGENT_PHASE")
        raise SystemExit(3)

print("ok")
PYEOF
    ) || rc=$?
    rc=${rc:-0}
    if [[ "$rc" -ne 0 ]]; then
        case "$POLICY_CHECK" in
            disabled:*)
                echo -e "${RED}Error: Agent '$AGENT' is disabled by config.user.json agentPolicy.enabledAgents${NC}"
                ;;
            phase_disallowed:*)
                echo -e "${RED}Error: Agent '$AGENT' is not allowed in phase '$AGENT_PHASE' (agentPolicy.phaseAllowedAgents)${NC}"
                ;;
            *)
                echo -e "${RED}Error: Failed to validate agentPolicy${NC}"
                ;;
        esac
        exit 1
    fi
fi

if ! check_agent_health "$AGENT"; then
    if [[ "$REQUESTED_AGENT" == "auto" ]]; then
        for fallback_agent in codex claude gemini cursor; do
            [[ "$fallback_agent" == "$AGENT" ]] && continue
            if check_agent_health "$fallback_agent"; then
                AUTO_SELECTION_REASON="${AUTO_SELECTION_REASON:+$AUTO_SELECTION_REASON; }fallback:$fallback_agent(health)"
                AGENT="$fallback_agent"
                if [[ "$AGENT" != "cursor" && "$AGENT_MODEL" == "composer-1.5" ]]; then
                    AGENT_MODEL=""
                fi
                break
            fi
        done
        check_agent_health "$AGENT" || exit 1
    else
        if [[ "$AGENT" == "cursor" ]]; then
            echo -e "${YELLOW}Tip: Cursor 登录后再试：cursor agent login${NC}"
            echo -e "${YELLOW}Tip: 查看模型列表：cursor agent --list-models（当前会报 Keychain 错误时需先修复登录）${NC}"
        fi
        exit 1
    fi
fi

echo -e "${GREEN}Spawning $AGENT agent for: $DESCRIPTION${NC}"
[[ -n "$AUTO_SELECTION_REASON" ]] && echo "Selection reason: $AUTO_SELECTION_REASON"
[[ -n "$AGENT_MODEL" ]] && echo "Model override: $AGENT_MODEL"

# 检查当前代理数量（加锁，避免并发写撞文件）
acquire_file_lock "$TASKS_LOCK_DIR" 30 || exit 1
if [[ -f "$TASKS_FILE" ]]; then
    ACTIVE_COUNT=$(grep -o '"status": "running"' "$TASKS_FILE" | wc -l || echo 0)
else
    ACTIVE_COUNT=0
fi
release_file_lock "$TASKS_LOCK_DIR"

if [[ $ACTIVE_COUNT -ge $MAX_AGENTS ]]; then
    echo -e "${RED}Error: Maximum agents ($MAX_AGENTS) already running${NC}"
    exit 1
fi

# 使用绝对路径
if [[ -n "$REPO_PATH_INPUT" ]]; then
    if [[ "$REPO_PATH_INPUT" = /* ]]; then
        REPO_PATH="$REPO_PATH_INPUT"
    else
        REPO_PATH="$(cd "$SKILL_DIR" && cd "$REPO_PATH_INPUT" 2>/dev/null && pwd)" || {
            echo -e "${RED}Error: Invalid --repo-path: $REPO_PATH_INPUT${NC}"
            exit 1
        }
    fi
    if [[ -z "$REPO" ]]; then
        REPO="$(basename "$REPO_PATH")"
    fi
    REPO_PARENT_DIR="$(dirname "$REPO_PATH")"
else
    REPO_PATH="$REPOS_BASE_DIR/$REPO"
    REPO_PARENT_DIR="$REPOS_BASE_DIR"
fi

SANITIZED_BRANCH=$(sanitize_branch_name "$BRANCH")
WORKTREE_DIR="$REPO_PARENT_DIR/${REPO}-${SANITIZED_BRANCH}"
SESSION_NAME="${AGENT}-${SANITIZED_BRANCH}"
LOG_FILE="$LOGS_DIR/${SESSION_NAME}.log"

echo "Repository: $REPO_PATH"
echo "Worktree: $WORKTREE_DIR"

# 确保日志目录存在
mkdir -p "$LOGS_DIR"

# 检查仓库是否存在
if [[ ! -d "$REPO_PATH" ]]; then
    if [[ -n "$REPO_PATH_INPUT" ]]; then
        echo -e "${RED}Error: --repo-path does not exist: $REPO_PATH${NC}"
        exit 1
    fi
    echo -e "${YELLOW}Warning: Repo $REPO not found locally${NC}"
    echo "Creating minimal repo structure..."
    mkdir -p "$REPO_PATH"
    cd "$REPO_PATH"
    git init
    git commit --allow-empty -m "Initial commit"
    cd "$SKILL_DIR"
fi

# 解析 git URL 获取默认分支（如果有）
DEFAULT_BRANCH=$(get_default_branch "$REPO_PATH")

if [[ "$COMPLETION_MODE" == "pr" ]]; then
    if ! git -C "$REPO_PATH" remote get-url origin >/dev/null 2>&1; then
        echo -e "${YELLOW}Warning: Repo has no 'origin' remote. PR flow may fail until you add a GitHub remote.${NC}"
    fi
    if command -v gh >/dev/null 2>&1; then
        GH_AUTH_STATUS=$(gh auth status 2>&1 || true)
        if echo "$GH_AUTH_STATUS" | grep -qi "token in default is invalid\\|not logged in\\|not logged into any github hosts"; then
            echo -e "${YELLOW}Warning: gh auth invalid. PR/CI/review automation in check-agents.sh will not work until 'gh auth login'.${NC}"
        fi
    fi
fi

# 创建 worktree
cd "$REPO_PATH"
if [[ ! -d "$WORKTREE_DIR" ]]; then
    if git show-ref --verify --quiet "refs/heads/$BRANCH" || git show-ref --verify --quiet "refs/remotes/origin/$BRANCH"; then
        git worktree add "$WORKTREE_DIR" "$BRANCH" 2>/dev/null || git worktree add "$WORKTREE_DIR" -B "$BRANCH" "${DEFAULT_BRANCH:-HEAD}"
    else
        git worktree add "$WORKTREE_DIR" -b "$BRANCH" "${DEFAULT_BRANCH:-HEAD}" 2>/dev/null || git worktree add "$WORKTREE_DIR" -b "$BRANCH"
    fi
else
    echo "Worktree already exists"
fi

# 安装依赖
if [[ -f "$WORKTREE_DIR/package.json" ]]; then
    echo "Installing dependencies..."
    cd "$WORKTREE_DIR"
    pnpm install 2>/dev/null || npm install 2>/dev/null || echo "No dependencies to install"
    cd "$SKILL_DIR"
fi

# 构建 Agent 命令
build_agent_cmd() {
    local agent_type="$1"
    local prompt="$2"
    local worktree="$3"
    local agent_model="$4"
    local cursor_mode="$5"

    # 尝试从配置文件读取
    local config_file="$SKILL_DIR/config/agents.json"
    if [[ -f "$config_file" ]]; then
        AGENT_TYPE="$agent_type" PROMPT_TEXT="$prompt" WORKTREE_PATH="$worktree" CONFIG_PATH="$config_file" AGENT_MODEL="$agent_model" CURSOR_MODE="$cursor_mode" python3 << 'PYEOF'
import json
import os
import shlex
import sys

config = json.load(open(os.environ['CONFIG_PATH']))
agent_type = os.environ['AGENT_TYPE']
prompt = os.environ['PROMPT_TEXT']
worktree = os.environ['WORKTREE_PATH']
agent_model = os.environ.get('AGENT_MODEL') or ''
cursor_mode = os.environ.get('CURSOR_MODE') or 'dev'
agent = config.get('agents', {}).get(agent_type, {})

if agent:
    cmd = [agent.get('command', agent_type)]
    cmd.extend(agent.get('args', []))

    cwd_arg = agent.get('cwdArg')
    if cwd_arg:
        cmd.extend([cwd_arg, worktree])
    model_arg = agent.get('modelArg')
    model_to_use = agent_model or agent.get('defaultModel')
    if model_arg and model_to_use:
        cmd.extend([model_arg, model_to_use])
    if agent_type == 'cursor' and cursor_mode == 'plan':
        cmd.extend(['--mode', 'plan'])

    cmd.append(prompt)
    print(' '.join(shlex.quote(str(part)) for part in cmd))
else:
    # 回退到硬编码
    print('')
    sys.exit(1)
PYEOF
        return
    fi

    # 硬编码回退
    case $agent_type in
        codex)
            if [[ -n "$agent_model" ]]; then
                echo "codex exec --dangerously-bypass-approvals-and-sandbox -C '$worktree' --model '$agent_model' '$prompt'"
            else
                echo "codex exec --dangerously-bypass-approvals-and-sandbox -C '$worktree' '$prompt'"
            fi
            ;;
        claude)
            if [[ -n "$agent_model" ]]; then
                echo "claude --dangerously-skip-permissions -p --model '$agent_model' '$prompt'"
            else
                echo "claude --dangerously-skip-permissions -p '$prompt'"
            fi
            ;;
        gemini) echo "gemini -p '$prompt'" ;;
        cursor)
            if [[ -n "$agent_model" ]]; then
                if [[ "$cursor_mode" == "plan" ]]; then
                    echo "cursor agent -f -p --mode plan --workspace '$worktree' --model '$agent_model' '$prompt'"
                else
                    echo "cursor agent -f -p --workspace '$worktree' --model '$agent_model' '$prompt'"
                fi
            else
                if [[ "$cursor_mode" == "plan" ]]; then
                    echo "cursor agent -f -p --mode plan --workspace '$worktree' '$prompt'"
                else
                    echo "cursor agent -f -p --workspace '$worktree' '$prompt'"
                fi
            fi
            ;;
    esac
}

CMD=$(build_agent_cmd "$AGENT" "$PROMPT" "$WORKTREE_DIR" "$AGENT_MODEL" "$CURSOR_MODE")
LAUNCH_SCRIPT="$LAUNCHERS_DIR/${SESSION_NAME}.sh"

if [[ -z "$CMD" ]]; then
    echo -e "${RED}Error: Failed to build agent command${NC}"
    exit 1
fi

# 生成启动脚本（避免超长命令直接塞给 tmux 导致会话落成空壳 shell）
mkdir -p "$LAUNCHERS_DIR"
CMD_B64=$(printf '%s' "$CMD" | base64 | tr -d '\n')
WORKTREE_B64=$(printf '%s' "$WORKTREE_DIR" | base64 | tr -d '\n')
LOG_FILE_B64=$(printf '%s' "$LOG_FILE" | base64 | tr -d '\n')
LAUNCH_SCRIPT_B64=$(printf '%s' "$LAUNCH_SCRIPT" | base64 | tr -d '\n')
python3 << PYEOF
import base64
import os

cmd = base64.b64decode('$CMD_B64').decode('utf-8')
worktree = base64.b64decode('$WORKTREE_B64').decode('utf-8')
log_file = base64.b64decode('$LOG_FILE_B64').decode('utf-8')
launch_script = base64.b64decode('$LAUNCH_SCRIPT_B64').decode('utf-8')

os.makedirs(os.path.dirname(launch_script), exist_ok=True)
with open(launch_script, 'w', encoding='utf-8', newline='\\n') as f:
    f.write('#!/usr/bin/env bash\\n')
    f.write('set -uo pipefail\\n')
    f.write(f'cd {worktree!r} || exit 1\\n')
    f.write(f'{cmd} 2>&1 | tee -a {log_file!r}\\n')
    f.write('exit \\${PIPESTATUS[0]}\\n')
os.chmod(launch_script, 0o755)
PYEOF

# 创建 tmux 会话，执行启动脚本
echo "Starting agent (logs: $LOG_FILE)..."
tmux new-session -d -s "$SESSION_NAME" "bash '$LAUNCH_SCRIPT'" 2>/dev/null || \
    tmux send-keys -t "$SESSION_NAME" "bash '$LAUNCH_SCRIPT'" Enter

# 验证会话是否创建成功
if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo -e "${RED}Error: Failed to create tmux session${NC}"
    exit 1
fi

# 更新任务文件
TIMESTAMP=$(date +%s)000
TEMP_FILE=$(mktemp)
PROMPT_B64=$(printf '%s' "$PROMPT" | base64 | tr -d '\n')
DESC_B64=$(printf '%s' "$DESCRIPTION" | base64 | tr -d '\n')
AGENT_MODEL_B64=$(printf '%s' "$AGENT_MODEL" | base64 | tr -d '\n')
CURSOR_MODE_B64=$(printf '%s' "$CURSOR_MODE" | base64 | tr -d '\n')
REQUESTED_AGENT_B64=$(printf '%s' "$REQUESTED_AGENT" | base64 | tr -d '\n')
AUTO_REASON_B64=$(printf '%s' "$AUTO_SELECTION_REASON" | base64 | tr -d '\n')
CLEANUP_AFTER_PY="None"
if [[ -n "$CLEANUP_AFTER_SECONDS" ]]; then
    CLEANUP_AFTER_PY="$CLEANUP_AFTER_SECONDS"
fi
CLEANUP_MODE_PY="'none'"
if [[ "$COMPLETION_MODE" == "session" ]]; then
    CLEANUP_MODE_PY="'session_ttl'"
fi

if [[ -f "$TASKS_FILE" ]]; then
    acquire_file_lock "$TASKS_LOCK_DIR" 60 || exit 1
    # 添加新代理到现有文件
    python3 << PYEOF
import json
import base64

with open('$TASKS_FILE', 'r', encoding='utf-8') as f:
    data = json.load(f)

if 'agents' not in data:
    data['agents'] = []

data['agents'].append({
    'id': '$BRANCH',
    'tmuxSession': '$SESSION_NAME',
    'agent': '$AGENT',
    'requestedAgent': base64.b64decode('$REQUESTED_AGENT_B64').decode('utf-8'),
    'agentModel': base64.b64decode('$AGENT_MODEL_B64').decode('utf-8') or None,
    'cursorMode': (base64.b64decode('$CURSOR_MODE_B64').decode('utf-8') if '$AGENT' == 'cursor' else None),
    'agentSelectionReason': base64.b64decode('$AUTO_REASON_B64').decode('utf-8') or None,
    'description': base64.b64decode('$DESC_B64').decode('utf-8'),
    'repo': '$REPO',
    'repoPath': '$REPO_PATH',
    'worktree': '$WORKTREE_DIR',
    'branch': '$BRANCH',
    'defaultBranch': '$DEFAULT_BRANCH',
    'startedAt': $TIMESTAMP,
    'status': 'running',
    'completionMode': '$COMPLETION_MODE',
    'autoMerge': ${AUTO_MERGE},
    'mergeMethod': '$MERGE_METHOD',
    'cleanupMode': $CLEANUP_MODE_PY,
    'cleanupAfterSeconds': $CLEANUP_AFTER_PY,
    'retryCount': 0,
    'notifyOnComplete': True,
    'logFile': '$LOG_FILE',
    'launchScript': '$LAUNCH_SCRIPT',
    'prompt': base64.b64decode('$PROMPT_B64').decode('utf-8'),
    'commandShell': ''
})

data['activeCount'] = len([a for a in data['agents'] if a.get('status') == 'running'])

with open('$TEMP_FILE', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
PYEOF
else
    acquire_file_lock "$TASKS_LOCK_DIR" 60 || exit 1
    # 创建新文件
    python3 << PYEOF
import json
import base64

data = {
    'agents': [{
        'id': '$BRANCH',
        'tmuxSession': '$SESSION_NAME',
        'agent': '$AGENT',
        'requestedAgent': base64.b64decode('$REQUESTED_AGENT_B64').decode('utf-8'),
        'agentModel': base64.b64decode('$AGENT_MODEL_B64').decode('utf-8') or None,
        'cursorMode': (base64.b64decode('$CURSOR_MODE_B64').decode('utf-8') if '$AGENT' == 'cursor' else None),
        'agentSelectionReason': base64.b64decode('$AUTO_REASON_B64').decode('utf-8') or None,
        'description': base64.b64decode('$DESC_B64').decode('utf-8'),
        'repo': '$REPO',
        'repoPath': '$REPO_PATH',
        'worktree': '$WORKTREE_DIR',
        'branch': '$BRANCH',
        'defaultBranch': '$DEFAULT_BRANCH',
        'startedAt': $TIMESTAMP,
        'status': 'running',
        'completionMode': '$COMPLETION_MODE',
        'autoMerge': ${AUTO_MERGE},
        'mergeMethod': '$MERGE_METHOD',
        'cleanupMode': $CLEANUP_MODE_PY,
        'cleanupAfterSeconds': $CLEANUP_AFTER_PY,
        'retryCount': 0,
        'notifyOnComplete': True,
        'logFile': '$LOG_FILE',
        'launchScript': '$LAUNCH_SCRIPT',
        'prompt': base64.b64decode('$PROMPT_B64').decode('utf-8'),
        'commandShell': ''
    }],
    'maxAgents': $MAX_AGENTS,
    'activeCount': 1
}

with open('$TEMP_FILE', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
PYEOF
fi

mv "$TEMP_FILE" "$TASKS_FILE"
release_file_lock "$TASKS_LOCK_DIR"

echo -e "${GREEN}Agent spawned successfully!${NC}"
echo "Session: $SESSION_NAME"
echo "Worktree: $WORKTREE_DIR"
echo "Log file: $LOG_FILE"
