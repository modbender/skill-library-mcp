#!/bin/bash
# claim-task.sh - Claim one queued task and dispatch via spawn-agent.sh
# Skill: dev-team

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh" 2>/dev/null || true

SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
QUEUE_FILE="$SKILL_DIR/assets/tasks.json"
QUEUE_LOCK_DIR="${QUEUE_FILE}.lock"
SPAWN_SCRIPT="$SKILL_DIR/scripts/spawn-agent.sh"
RECOMMEND_SCRIPT="$SKILL_DIR/scripts/recommend-agent.sh"
trap 'release_file_lock "$QUEUE_LOCK_DIR"' EXIT

TASK_ID=""
AGENT="auto"
PHASE=""
FORMAT="text"
DRY_RUN=0

usage() {
    cat <<'EOF'
Usage:
  claim-task.sh [--task-id <id>] [--agent codex|claude|gemini|cursor|auto] [--phase build|review|fixup] [--dry-run] [--format text|json]

Notes:
  - Claims a single queued task atomically, then dispatches it via spawn-agent.sh.
  - If --task-id omitted, selects the highest-priority queued task matching filters.
EOF
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --task-id) TASK_ID="$2"; shift 2 ;;
        --agent) AGENT="$2"; shift 2 ;;
        --phase) PHASE="$2"; shift 2 ;;
        --dry-run) DRY_RUN=1; shift ;;
        --format) FORMAT="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) usage ;;
    esac
done

[[ "$AGENT" =~ ^(auto|codex|claude|gemini|cursor)$ ]] || { echo "Invalid --agent" >&2; exit 1; }
[[ -z "$PHASE" || "$PHASE" =~ ^(build|review|fixup)$ ]] || { echo "Invalid --phase" >&2; exit 1; }
[[ "$FORMAT" =~ ^(text|json)$ ]] || { echo "Invalid --format" >&2; exit 1; }
[[ -x "$SPAWN_SCRIPT" ]] || { echo "spawn-agent.sh not found/executable" >&2; exit 1; }

[[ -f "$QUEUE_FILE" ]] || echo '{"items":[]}' > "$QUEUE_FILE"

acquire_file_lock "$QUEUE_LOCK_DIR" 60 || exit 1
CLAIM_TMP=$(mktemp)
REQUESTED_AGENT="$AGENT" FILTER_PHASE="$PHASE" TARGET_TASK_ID="$TASK_ID" DRY_RUN_CLAIM="$DRY_RUN" python3 <<PYEOF > "$CLAIM_TMP"
import json, os, time, sys
from pathlib import Path

queue_file = Path("$QUEUE_FILE")
data = json.loads(queue_file.read_text(encoding="utf-8"))
items = data.get("items")
if not isinstance(items, list):
    items = []
    data["items"] = items

requested_agent = os.environ.get("REQUESTED_AGENT","auto")
target_task_id = os.environ.get("TARGET_TASK_ID","").strip()
filter_phase = os.environ.get("FILTER_PHASE","").strip()
dry_run_claim = os.environ.get("DRY_RUN_CLAIM","0") == "1"
now_ms = int(time.time() * 1000)

# 回收过期 claimed 租约，避免上次 dispatch 异常后任务卡死
for item in items:
    if item.get("status") != "claimed":
        continue
    lease = item.get("claimLeaseUntil")
    try:
        lease = int(lease) if lease is not None else 0
    except Exception:
        lease = 0
    if lease and lease < now_ms:
        item["status"] = "queued"
        item["requeuedAt"] = now_ms
        item["requeueReason"] = "claim_lease_expired"
        item["claimLeaseUntil"] = None

def priority_rank(p):
    return {"urgent":0,"high":1,"medium":2,"low":3}.get((p or "medium"), 9)

def eligible(item):
    if item.get("status") != "queued":
        return False
    if target_task_id and item.get("id") != target_task_id:
        return False
    if filter_phase and item.get("phase") != filter_phase:
        return False
    allowed = item.get("allowedAgents") or []
    if requested_agent != "auto" and allowed and requested_agent not in allowed:
        return False
    return True

candidates = [i for i in items if eligible(i)]
candidates.sort(key=lambda x: (priority_rank(x.get("priority")), x.get("createdAt", 0)))
if not candidates:
    print(json.dumps({"ok": False, "reason": "no_queued_task_match"}, ensure_ascii=False))
    raise SystemExit(0)

selected = candidates[0]
task_view = dict(selected)
task_view["claimRequestedAgent"] = requested_agent
if dry_run_claim:
    print(json.dumps({"ok": True, "dryRun": True, "task": task_view}, ensure_ascii=False, indent=2))
    raise SystemExit(0)

selected["status"] = "claimed"
selected["claimedAt"] = now_ms
selected["claimLeaseUntil"] = now_ms + 5 * 60 * 1000
selected["claimRequestedAgent"] = requested_agent
selected["claimedBy"] = "claim-task.sh"
selected.setdefault("attempts", 0)
selected["attempts"] = int(selected.get("attempts") or 0) + 1

data["updatedAt"] = now_ms
data["queueStats"] = {
    "queued": sum(1 for i in items if i.get("status") == "queued"),
    "claimed": sum(1 for i in items if i.get("status") == "claimed"),
    "dispatched": sum(1 for i in items if i.get("status") == "dispatched"),
    "dispatchFailed": sum(1 for i in items if i.get("status") == "dispatch_failed"),
}
queue_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"ok": True, "task": selected}, ensure_ascii=False, indent=2))
PYEOF

if [[ "$FORMAT" == "json" && "$DRY_RUN" -eq 1 ]]; then
    cat "$CLAIM_TMP"
    release_file_lock "$QUEUE_LOCK_DIR"
    exit 0
fi

CLAIM_OK=$(python3 - <<PYEOF
import json
d=json.load(open("$CLAIM_TMP","r",encoding="utf-8"))
print("1" if d.get("ok") else "0")
PYEOF
)
if [[ "$CLAIM_OK" != "1" ]]; then
    if [[ "$FORMAT" == "json" ]]; then
        cat "$CLAIM_TMP"
    else
        python3 - <<PYEOF
import json
d=json.load(open("$CLAIM_TMP","r",encoding="utf-8"))
print("No task claimed:", d.get("reason"))
PYEOF
    fi
    release_file_lock "$QUEUE_LOCK_DIR"
    exit 0
fi

if [[ "$DRY_RUN" -eq 1 ]]; then
    if [[ "$FORMAT" == "json" ]]; then
        cat "$CLAIM_TMP"
    else
        python3 - <<PYEOF
import json
d=json.load(open("$CLAIM_TMP","r",encoding="utf-8"))
t=d["task"]
print(f"Would claim: {t.get('id')} ({t.get('phase')} {t.get('priority')}) -> {t.get('branch')}")
PYEOF
    fi
    release_file_lock "$QUEUE_LOCK_DIR"
    exit 0
fi

# 释放首轮 claim 锁；dispatch 完成后会再次加锁写回结果
release_file_lock "$QUEUE_LOCK_DIR"

# Extract task fields for dispatch
TASK_META=$(python3 - <<PYEOF
import json, base64
d=json.load(open("$CLAIM_TMP","r",encoding="utf-8"))
t=d["task"]
for key in ["id","title","description","phase","repo","repoPath","branch","completionMode","mergeMethod","prompt"]:
    v=t.get(key)
    if v is None: v=""
    print(f"{key}=" + base64.b64encode(str(v).encode("utf-8")).decode("ascii"))
print("autoMerge=" + ("1" if t.get("autoMerge") else "0"))
print("cleanupAfterSeconds=" + ("" if t.get("cleanupAfterSeconds") is None else str(t.get("cleanupAfterSeconds"))))
print("agentModel=" + base64.b64encode(str(t.get("agentModel") or "").encode("utf-8")).decode("ascii"))
print("allowedAgents=" + base64.b64encode(json.dumps(t.get("allowedAgents") or [], ensure_ascii=False).encode("utf-8")).decode("ascii"))
print("preferredAgents=" + base64.b64encode(json.dumps(t.get("preferredAgents") or [], ensure_ascii=False).encode("utf-8")).decode("ascii"))
PYEOF
)

decode_meta() {
    local key="$1"
    printf '%s\n' "$TASK_META" | sed -n "s/^${key}=//p" | head -n1
}

_b64d() {
    B64_IN="$1" python3 - <<'PYEOF'
import base64, os
print(base64.b64decode(os.environ.get("B64_IN","")).decode("utf-8"), end="")
PYEOF
}

TASK_ID_CLAIMED=$(_b64d "$(decode_meta id)")
TASK_TITLE=$(_b64d "$(decode_meta title)")
TASK_DESC=$(_b64d "$(decode_meta description)")
TASK_PHASE=$(_b64d "$(decode_meta phase)")
TASK_REPO=$(_b64d "$(decode_meta repo)")
TASK_REPO_PATH=$(_b64d "$(decode_meta repoPath)")
TASK_BRANCH=$(_b64d "$(decode_meta branch)")
TASK_COMPLETION=$(_b64d "$(decode_meta completionMode)")
TASK_MERGE_METHOD=$(_b64d "$(decode_meta mergeMethod)")
TASK_PROMPT=$(_b64d "$(decode_meta prompt)")
TASK_AGENT_MODEL=$(_b64d "$(decode_meta agentModel)")
TASK_AUTO_MERGE=$(printf '%s\n' "$TASK_META" | sed -n 's/^autoMerge=//p' | head -n1)
TASK_CLEANUP_AFTER=$(printf '%s\n' "$TASK_META" | sed -n 's/^cleanupAfterSeconds=//p' | head -n1)
TASK_ALLOWED_JSON=$(_b64d "$(decode_meta allowedAgents)")
TASK_PREFERRED_JSON=$(_b64d "$(decode_meta preferredAgents)")

SELECTED_AGENT="$AGENT"
if [[ "$SELECTED_AGENT" == "auto" ]]; then
    if [[ -x "$RECOMMEND_SCRIPT" ]]; then
        _tmp_prompt=$(mktemp)
        printf '%s' "$TASK_PROMPT" > "$_tmp_prompt"
        rec_json=$("$RECOMMEND_SCRIPT" --description "$TASK_DESC" --prompt-file "$_tmp_prompt" --phase "${TASK_PHASE:-build}" --format json 2>/dev/null || true)
        rm -f "$_tmp_prompt"
        if [[ -n "$rec_json" ]]; then
            rec_agent=$(printf '%s' "$rec_json" | python3 -c "import sys,json; print(json.load(sys.stdin).get('recommendedAgent','auto'))" 2>/dev/null || echo auto)
            [[ -n "$rec_agent" ]] && SELECTED_AGENT="$rec_agent"
        fi
    fi
fi

# Enforce task-level allowedAgents if present
if [[ -n "$TASK_ALLOWED_JSON" ]]; then
    ALLOW_CHECK=$(TASK_ALLOWED_JSON="$TASK_ALLOWED_JSON" SELECTED_AGENT="$SELECTED_AGENT" python3 - <<'PYEOF'
import json, os
allowed = json.loads(os.environ.get("TASK_ALLOWED_JSON","[]") or "[]")
sel = os.environ.get("SELECTED_AGENT","")
if allowed and sel not in allowed:
    print("0")
else:
    print("1")
PYEOF
)
    if [[ "$ALLOW_CHECK" != "1" ]]; then
        SELECTED_AGENT=$(TASK_PREFERRED_JSON="$TASK_PREFERRED_JSON" TASK_ALLOWED_JSON="$TASK_ALLOWED_JSON" python3 - <<'PYEOF'
import json, os
pref = json.loads(os.environ.get("TASK_PREFERRED_JSON","[]") or "[]")
allowed = json.loads(os.environ.get("TASK_ALLOWED_JSON","[]") or "[]")
for a in pref:
    if not allowed or a in allowed:
        print(a); raise SystemExit
if allowed:
    print(allowed[0]); raise SystemExit
print("codex")
PYEOF
)
    fi
fi

PROMPT_FILE=$(mktemp)
printf '%s' "$TASK_PROMPT" > "$PROMPT_FILE"

SPAWN_CMD=("$SPAWN_SCRIPT" "--agent" "$SELECTED_AGENT" "--phase" "${TASK_PHASE:-build}")
if [[ -n "$TASK_REPO_PATH" ]]; then
    SPAWN_CMD+=("--repo-path" "$TASK_REPO_PATH")
elif [[ -n "$TASK_REPO" ]]; then
    SPAWN_CMD+=("--repo" "$TASK_REPO")
fi
SPAWN_CMD+=("--branch" "$TASK_BRANCH" "--description" "${TASK_TITLE:-$TASK_DESC}" "--completion-mode" "${TASK_COMPLETION:-pr}" "--prompt-file" "$PROMPT_FILE")
[[ -n "$TASK_AGENT_MODEL" ]] && SPAWN_CMD+=("--agent-model" "$TASK_AGENT_MODEL")
[[ "$TASK_AUTO_MERGE" == "1" ]] && SPAWN_CMD+=("--auto-merge")
[[ -n "$TASK_MERGE_METHOD" ]] && SPAWN_CMD+=("--merge-method" "$TASK_MERGE_METHOD")
[[ -n "$TASK_CLEANUP_AFTER" ]] && SPAWN_CMD+=("--cleanup-after-seconds" "$TASK_CLEANUP_AFTER")

SPAWN_OUT=$(mktemp)
set +e
"${SPAWN_CMD[@]}" >"$SPAWN_OUT" 2>&1
SPAWN_RC=$?
set -e
rm -f "$PROMPT_FILE"

acquire_file_lock "$QUEUE_LOCK_DIR" 60 || exit 1
RESULT_JSON=$(python3 <<PYEOF
import json, time, os, re
from pathlib import Path

queue_file = Path("$QUEUE_FILE")
data = json.loads(queue_file.read_text(encoding="utf-8"))
items = data.get("items", [])
now_ms = int(time.time() * 1000)
target_id = "$TASK_ID_CLAIMED"
spawn_rc = int("$SPAWN_RC")
spawn_out = Path("$SPAWN_OUT").read_text(encoding="utf-8", errors="ignore")
selected_agent = "$SELECTED_AGENT"

session = None
worktree = None
for line in spawn_out.splitlines():
    if line.startswith("Session: "):
        session = line.split("Session: ",1)[1].strip()
    if line.startswith("Worktree: "):
        worktree = line.split("Worktree: ",1)[1].strip()

for item in items:
    if item.get("id") != target_id:
        continue
    item["claimedByAgent"] = selected_agent
    item["claimLeaseUntil"] = None
    item["lastDispatchAt"] = now_ms
    item["dispatchAttemptCount"] = int(item.get("dispatchAttemptCount") or 0) + 1
    item["spawnExitCode"] = spawn_rc
    item["spawnOutputPreview"] = "\n".join(spawn_out.splitlines()[-20:])
    if spawn_rc == 0:
        item["status"] = "dispatched"
        item["dispatchedAt"] = now_ms
        item["tmuxSession"] = session
        item["worktree"] = worktree
        item["selectedAgent"] = selected_agent
    else:
        item["status"] = "dispatch_failed"
        item["dispatchFailedAt"] = now_ms
    break

data["updatedAt"] = now_ms
data["queueStats"] = {
    "queued": sum(1 for i in items if i.get("status") == "queued"),
    "claimed": sum(1 for i in items if i.get("status") == "claimed"),
    "dispatched": sum(1 for i in items if i.get("status") == "dispatched"),
    "dispatchFailed": sum(1 for i in items if i.get("status") == "dispatch_failed"),
}
queue_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

print(json.dumps({
    "ok": spawn_rc == 0,
    "taskId": target_id,
    "selectedAgent": selected_agent,
    "spawnExitCode": spawn_rc,
    "tmuxSession": session,
    "worktree": worktree,
}, ensure_ascii=False, indent=2))
PYEOF
)
release_file_lock "$QUEUE_LOCK_DIR"
rm -f "$SPAWN_OUT" "$CLAIM_TMP"

if [[ "$FORMAT" == "json" ]]; then
    echo "$RESULT_JSON"
else
    RESULT_JSON_PAYLOAD="$RESULT_JSON" python3 - <<'PYEOF'
import json, os
d=json.loads(os.environ.get("RESULT_JSON_PAYLOAD","{}"))
if d.get("ok"):
    print(f"Claimed+dispatched: {d.get('taskId')} -> {d.get('selectedAgent')}")
    print(f"  session: {d.get('tmuxSession')}")
    print(f"  worktree: {d.get('worktree')}")
else:
    print(f"Dispatch failed: {d.get('taskId')} -> {d.get('selectedAgent')} (rc={d.get('spawnExitCode')})")
PYEOF
fi

[[ "${RESULT_JSON}" == *'"ok": true'* ]] || exit 1
