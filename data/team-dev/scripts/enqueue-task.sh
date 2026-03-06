#!/bin/bash
# enqueue-task.sh - Add a task to dev-team queue (Queue/Claim mode)
# Skill: dev-team

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh" 2>/dev/null || true

SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
QUEUE_FILE="$SKILL_DIR/assets/tasks.json"
QUEUE_LOCK_DIR="${QUEUE_FILE}.lock"
trap 'release_file_lock "$QUEUE_LOCK_DIR"' EXIT

PHASE="build"
PRIORITY="medium"
STATUS="queued"
COMPLETION_MODE="pr"
AUTO_MERGE=0
MERGE_METHOD="squash"
CLEANUP_AFTER_SECONDS=""
AGENT_MODEL=""
TASK_ID=""
TITLE=""
DESCRIPTION=""
PROMPT=""
PROMPT_B64_INPUT=""
REPO=""
REPO_PATH=""
BRANCH=""
BRANCH_STRATEGY="feature"
FORMAT="text"

declare -a PREFERRED_AGENTS=()
declare -a ALLOWED_AGENTS=()
declare -a CAPABILITIES=()
declare -a DOD_ITEMS=()

usage() {
    cat <<'EOF'
Usage:
  enqueue-task.sh --repo-path <path> --branch <branch> --description <desc> \
    [--title <title>] [--phase build|review|fixup] [--priority low|medium|high|urgent] \
    [--completion-mode pr|session] [--prompt <text> | --prompt-file <file> | --prompt-b64 <b64>] \
    [--preferred-agents a,b,c] [--allowed-agents a,b,c] [--capabilities x,y] \
    [--dod "item"]... [--format text|json]

Notes:
  - Queue task stores prompt text inline (UTF-8) for stable later claiming.
  - Use --prompt-file for complex multi-line prompts.
EOF
    exit 1
}

split_csv_into_array() {
    local csv="$1"
    local target="$2"
    local v
    local _items=()
    IFS=',' read -r -a _items <<< "$csv"
    for v in "${_items[@]}"; do
        v="$(echo "$v" | xargs)"
        [[ -z "$v" ]] && continue
        case "$target" in
            PREFERRED_AGENTS) PREFERRED_AGENTS+=("$v") ;;
            ALLOWED_AGENTS) ALLOWED_AGENTS+=("$v") ;;
            CAPABILITIES) CAPABILITIES+=("$v") ;;
            *) ;;
        esac
    done
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --id) TASK_ID="$2"; shift 2 ;;
        --title) TITLE="$2"; shift 2 ;;
        --description) DESCRIPTION="$2"; shift 2 ;;
        --repo) REPO="$2"; shift 2 ;;
        --repo-path) REPO_PATH="$2"; shift 2 ;;
        --branch) BRANCH="$2"; shift 2 ;;
        --branch-strategy) BRANCH_STRATEGY="$2"; shift 2 ;;
        --phase) PHASE="$2"; shift 2 ;;
        --priority) PRIORITY="$2"; shift 2 ;;
        --completion-mode) COMPLETION_MODE="$2"; shift 2 ;;
        --auto-merge) AUTO_MERGE=1; shift ;;
        --merge-method) MERGE_METHOD="$2"; shift 2 ;;
        --cleanup-after-seconds) CLEANUP_AFTER_SECONDS="$2"; shift 2 ;;
        --agent-model) AGENT_MODEL="$2"; shift 2 ;;
        --preferred-agents) split_csv_into_array "$2" PREFERRED_AGENTS; shift 2 ;;
        --allowed-agents) split_csv_into_array "$2" ALLOWED_AGENTS; shift 2 ;;
        --capabilities) split_csv_into_array "$2" CAPABILITIES; shift 2 ;;
        --dod) DOD_ITEMS+=("$2"); shift 2 ;;
        --prompt) PROMPT="$2"; shift 2 ;;
        --prompt-file)
            [[ -f "$2" ]] || { echo "Prompt file not found: $2" >&2; exit 1; }
            PROMPT="$(cat "$2")"
            shift 2
            ;;
        --prompt-b64) PROMPT_B64_INPUT="$2"; shift 2 ;;
        --format) FORMAT="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) echo "Unknown option: $1" >&2; usage ;;
    esac
done

[[ -n "$DESCRIPTION" && -n "$BRANCH" ]] || usage
[[ -n "$REPO" || -n "$REPO_PATH" ]] || { echo "Error: --repo or --repo-path is required" >&2; usage; }
[[ "$PHASE" =~ ^(build|review|fixup)$ ]] || { echo "Error: invalid --phase" >&2; exit 1; }
[[ "$PRIORITY" =~ ^(low|medium|high|urgent)$ ]] || { echo "Error: invalid --priority" >&2; exit 1; }
[[ "$COMPLETION_MODE" =~ ^(pr|session)$ ]] || { echo "Error: invalid --completion-mode" >&2; exit 1; }
[[ "$MERGE_METHOD" =~ ^(squash|merge|rebase)$ ]] || { echo "Error: invalid --merge-method" >&2; exit 1; }
if [[ -n "$CLEANUP_AFTER_SECONDS" && ! "$CLEANUP_AFTER_SECONDS" =~ ^[0-9]+$ ]]; then
    echo "Error: --cleanup-after-seconds must be non-negative integer" >&2
    exit 1
fi

if [[ -z "$PROMPT" && -n "$PROMPT_B64_INPUT" ]]; then
    PROMPT=$(PROMPT_B64_IN="$PROMPT_B64_INPUT" python3 - <<'PYEOF'
import base64, os
raw = os.environ.get("PROMPT_B64_IN", "")
print(base64.b64decode(raw).decode("utf-8"), end="")
PYEOF
)
fi
[[ -n "$PROMPT" ]] || { echo "Error: prompt is required (--prompt/--prompt-file/--prompt-b64)" >&2; exit 1; }

acquire_file_lock "$QUEUE_LOCK_DIR" 60 || exit 1

DESC_B64=$(printf '%s' "$DESCRIPTION" | base64 | tr -d '\n')
TITLE_B64=$(printf '%s' "${TITLE:-$DESCRIPTION}" | base64 | tr -d '\n')
PROMPT_B64=$(printf '%s' "$PROMPT" | base64 | tr -d '\n')
REPO_B64=$(printf '%s' "$REPO" | base64 | tr -d '\n')
REPO_PATH_B64=$(printf '%s' "$REPO_PATH" | base64 | tr -d '\n')
BRANCH_B64=$(printf '%s' "$BRANCH" | base64 | tr -d '\n')
BRANCH_STRATEGY_B64=$(printf '%s' "$BRANCH_STRATEGY" | base64 | tr -d '\n')
AGENT_MODEL_B64=$(printf '%s' "$AGENT_MODEL" | base64 | tr -d '\n')
PREFERRED_JOINED=$(printf '%s\n' "${PREFERRED_AGENTS[@]}")
ALLOWED_JOINED=$(printf '%s\n' "${ALLOWED_AGENTS[@]}")
CAPS_JOINED=$(printf '%s\n' "${CAPABILITIES[@]}")
DOD_JOINED=$(printf '%s\n' "${DOD_ITEMS[@]}")
PREFERRED_JSON=$(QUEUE_LINES="$PREFERRED_JOINED" python3 - <<'PYEOF'
import json, os
arr=[x.strip() for x in os.environ.get("QUEUE_LINES","").splitlines() if x.strip()]
print(json.dumps(arr, ensure_ascii=False))
PYEOF
)
ALLOWED_JSON=$(QUEUE_LINES="$ALLOWED_JOINED" python3 - <<'PYEOF'
import json, os
arr=[x.strip() for x in os.environ.get("QUEUE_LINES","").splitlines() if x.strip()]
print(json.dumps(arr, ensure_ascii=False))
PYEOF
)
CAPS_JSON=$(QUEUE_LINES="$CAPS_JOINED" python3 - <<'PYEOF'
import json, os
arr=[x.strip() for x in os.environ.get("QUEUE_LINES","").splitlines() if x.strip()]
print(json.dumps(arr, ensure_ascii=False))
PYEOF
)
DOD_JSON=$(QUEUE_LINES="$DOD_JOINED" python3 - <<'PYEOF'
import json, os
arr=[x.strip() for x in os.environ.get("QUEUE_LINES","").splitlines() if x.strip()]
print(json.dumps(arr, ensure_ascii=False))
PYEOF
)

python3 <<PYEOF
import base64, json, os, time, uuid
from pathlib import Path

queue_file = Path("$QUEUE_FILE")
queue_file.parent.mkdir(parents=True, exist_ok=True)

if queue_file.exists():
    try:
        data = json.loads(queue_file.read_text(encoding="utf-8"))
    except Exception:
        data = {}
else:
    data = {}

items = data.get("items")
if not isinstance(items, list):
    items = []

now_ms = int(time.time() * 1000)
task_id = "$TASK_ID".strip() or f"task-{time.strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"

if any((it.get("id") == task_id) for it in items):
    raise SystemExit(f"Task id already exists: {task_id}")

title = base64.b64decode("$TITLE_B64").decode("utf-8")
description = base64.b64decode("$DESC_B64").decode("utf-8")
prompt = base64.b64decode("$PROMPT_B64").decode("utf-8")
repo = base64.b64decode("$REPO_B64").decode("utf-8")
repo_path = base64.b64decode("$REPO_PATH_B64").decode("utf-8")
branch = base64.b64decode("$BRANCH_B64").decode("utf-8")
branch_strategy = base64.b64decode("$BRANCH_STRATEGY_B64").decode("utf-8")
agent_model = base64.b64decode("$AGENT_MODEL_B64").decode("utf-8") or None

item = {
    "id": task_id,
    "title": title,
    "description": description,
    "phase": "$PHASE",
    "priority": "$PRIORITY",
    "status": "$STATUS",
    "repo": repo or None,
    "repoPath": repo_path or None,
    "branch": branch,
    "branchStrategy": branch_strategy or "feature",
    "completionMode": "$COMPLETION_MODE",
    "autoMerge": bool($AUTO_MERGE),
    "mergeMethod": "$MERGE_METHOD",
    "cleanupAfterSeconds": int("$CLEANUP_AFTER_SECONDS") if "$CLEANUP_AFTER_SECONDS" else None,
    "preferredAgents": json.loads('''$PREFERRED_JSON'''),
    "allowedAgents": json.loads('''$ALLOWED_JSON'''),
    "capabilities": json.loads('''$CAPS_JSON'''),
    "dod": json.loads('''$DOD_JSON'''),
    "agentModel": agent_model,
    "prompt": prompt,
    "createdBy": "main-agent",
    "createdAt": now_ms,
}
items.append(item)
items.sort(key=lambda x: ({"urgent":0,"high":1,"medium":2,"low":3}.get(x.get("priority","medium"), 9), x.get("createdAt",0)))

data["items"] = items
data["updatedAt"] = now_ms
data["queueStats"] = {
    "queued": sum(1 for i in items if i.get("status") == "queued"),
    "claimed": sum(1 for i in items if i.get("status") == "claimed"),
    "dispatched": sum(1 for i in items if i.get("status") == "dispatched"),
}
queue_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

if "$FORMAT" == "json":
    print(json.dumps({"ok": True, "task": item}, ensure_ascii=False, indent=2))
else:
    print(f"Enqueued task: {task_id}")
    print(f"  phase: {item['phase']}")
    print(f"  priority: {item['priority']}")
    print(f"  repoPath: {item.get('repoPath') or ''}")
    print(f"  branch: {item['branch']}")
PYEOF
