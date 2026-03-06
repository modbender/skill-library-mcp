#!/bin/bash
# sync-queue-status.sh - Sync queue tasks.json status from active-tasks.json
# Skill: dev-team

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh" 2>/dev/null || true

SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
QUEUE_FILE="$SKILL_DIR/assets/tasks.json"
LEGACY_QUEUE_FILE="$SKILL_DIR/queue/tasks.json"
TASKS_FILE="$SKILL_DIR/assets/active-tasks.json"
QUEUE_LOCK_DIR="${QUEUE_FILE}.lock"
TASKS_LOCK_DIR="$(get_tasks_lock_dir)"
trap 'release_file_lock "$QUEUE_LOCK_DIR"; release_file_lock "$TASKS_LOCK_DIR"' EXIT

FORMAT="text"
DRY_RUN=0

usage() {
    echo "Usage: $0 [--dry-run] [--format text|json]"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run) DRY_RUN=1; shift ;;
        --format) FORMAT="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) usage ;;
    esac
done
[[ "$FORMAT" =~ ^(text|json)$ ]] || { echo "Invalid --format" >&2; exit 1; }

if [[ ! -f "$QUEUE_FILE" && -f "$LEGACY_QUEUE_FILE" ]]; then
    cp "$LEGACY_QUEUE_FILE" "$QUEUE_FILE"
fi
[[ -f "$QUEUE_FILE" ]] || { [[ "$FORMAT" == "json" ]] && echo '{"ok":true,"updated":0,"skipped":"no_queue"}' || echo "No queue file"; exit 0; }
[[ -f "$TASKS_FILE" ]] || { [[ "$FORMAT" == "json" ]] && echo '{"ok":true,"updated":0,"skipped":"no_active_tasks"}' || echo "No active-tasks.json"; exit 0; }

acquire_file_lock "$TASKS_LOCK_DIR" 60 || exit 1
acquire_file_lock "$QUEUE_LOCK_DIR" 60 || exit 1

TMP_OUT=$(mktemp)
python3 <<PYEOF > "$TMP_OUT"
import json, time, os
from pathlib import Path

queue_file = Path("$QUEUE_FILE")
tasks_file = Path("$TASKS_FILE")
dry_run = bool($DRY_RUN)

queue_data = json.loads(queue_file.read_text(encoding="utf-8"))
tasks_data = json.loads(tasks_file.read_text(encoding="utf-8"))
items = queue_data.get("items")
if not isinstance(items, list):
    items = []
    queue_data["items"] = items

active_agents = tasks_data.get("agents") or []
now_ms = int(time.time() * 1000)

def norm_path(p):
    try:
        return os.path.realpath(p) if p else ""
    except Exception:
        return p or ""

active_index = {}
for a in active_agents:
    key = (
        a.get("branch") or "",
        norm_path(a.get("repoPath") or "")
    )
    active_index.setdefault(key, []).append(a)

updated = 0
changes = []

for item in items:
    q_status = item.get("status")
    branch = item.get("branch") or ""
    repo_path = norm_path(item.get("repoPath") or "")
    if not branch:
        continue

    matches = active_index.get((branch, repo_path), [])
    if not matches and not repo_path:
        # fallback: branch only (older queue items may omit repoPath)
        for (b, rp), arr in active_index.items():
            if b == branch:
                matches.extend(arr)

    if not matches:
        # Keep queued/claimed/dispatched untouched if no active task match.
        continue

    # Prefer newest task record for the branch
    matches.sort(key=lambda a: (a.get("startedAt") or 0), reverse=True)
    a = matches[0]
    a_status = a.get("status")
    effective_status = (a.get("effectiveStatus") or a_status or "")

    next_status = item.get("status")
    if a_status == "running":
        next_status = "running"
    elif a_status in {"waiting_checks","checks_failed","waiting_review","review_changes_requested","review_human_attention","waiting_human_approve","merge_ready","merge_queued"}:
        next_status = a_status
    elif a_status in {"done","merged","failed","cancelled","cleaned"}:
        next_status = a_status
    else:
        next_status = a_status or next_status

    changed = False
    if item.get("status") != next_status and next_status:
        item["status"] = next_status
        changed = True
    if item.get("activeStatus") != a_status:
        item["activeStatus"] = a_status
        changed = True
    if item.get("effectiveStatus") != effective_status:
        item["effectiveStatus"] = effective_status
        changed = True
    if item.get("linkedTmuxSession") != a.get("tmuxSession"):
        item["linkedTmuxSession"] = a.get("tmuxSession")
        changed = True
    if item.get("linkedWorktree") != a.get("worktree"):
        item["linkedWorktree"] = a.get("worktree")
        changed = True
    if item.get("linkedAgent") != a.get("agent"):
        item["linkedAgent"] = a.get("agent")
        changed = True
    if item.get("activeTaskId") != (a.get("id") or a.get("branch")):
        item["activeTaskId"] = a.get("id") or a.get("branch")
        changed = True
    if item.get("linkedAt") is None:
        item["linkedAt"] = now_ms
        changed = True

    if changed:
        updated += 1
        item["lastSyncedAt"] = now_ms
        changes.append({
            "id": item.get("id"),
            "branch": branch,
            "from": q_status,
            "to": item.get("status"),
            "activeStatus": a_status
        })

queue_data["updatedAt"] = now_ms
queue_data["queueStats"] = {
    "queued": sum(1 for i in items if i.get("status") == "queued"),
    "claimed": sum(1 for i in items if i.get("status") == "claimed"),
    "dispatched": sum(1 for i in items if i.get("status") == "dispatched"),
    "running": sum(1 for i in items if i.get("status") == "running"),
    "terminal": sum(1 for i in items if i.get("status") in {"done","merged","failed","cancelled","cleaned"}),
    "other": sum(1 for i in items if i.get("status") not in {"queued","claimed","dispatched","running","done","merged","failed","cancelled","cleaned"}),
}

if not dry_run and updated:
    queue_file.write_text(json.dumps(queue_data, ensure_ascii=False, indent=2), encoding="utf-8")

print(json.dumps({"ok": True, "updated": updated, "changes": changes, "queueStats": queue_data.get("queueStats", {})}, ensure_ascii=False, indent=2))
PYEOF

RESULT_JSON="$(cat "$TMP_OUT")"
rm -f "$TMP_OUT"

release_file_lock "$QUEUE_LOCK_DIR"
release_file_lock "$TASKS_LOCK_DIR"

if [[ "$FORMAT" == "json" ]]; then
    echo "$RESULT_JSON"
else
    RESULT_JSON_ENV="$RESULT_JSON" python3 - <<'PYEOF'
import json, os
d=json.loads(os.environ.get("RESULT_JSON_ENV","{}"))
print(f"Synced queue status: updated={d.get('updated',0)}")
for c in d.get("changes", [])[:20]:
    print(f"  {c.get('id')}: {c.get('from')} -> {c.get('to')} (active={c.get('activeStatus')})")
print(f"queueStats: {d.get('queueStats')}")
PYEOF
fi
