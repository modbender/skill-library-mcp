#!/bin/bash
# prune-queue-history.sh - Archive old terminal queue tasks from tasks.json
# Skill: dev-team

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/utils.sh" ]]; then
    source "$SCRIPT_DIR/utils.sh"
else
    get_root_dir() { echo "$(dirname "$(dirname "$SCRIPT_DIR")")"; }
    RED='\033[0;31m'
    YELLOW='\033[1;33m'
    NC='\033[0m'
fi

SKILL_DIR="$(cd "$(dirname "$SCRIPT_DIR")" && pwd)"
QUEUE_FILE="$SKILL_DIR/assets/tasks.json"
LEGACY_QUEUE_FILE="$SKILL_DIR/queue/tasks.json"
QUEUE_LOCK_DIR="${QUEUE_FILE}.lock"
ARCHIVE_DIR="$SKILL_DIR/assets/logs/archives"
trap 'release_file_lock "$QUEUE_LOCK_DIR"' EXIT

KEEP_DAYS=7
KEEP_COUNT=50
KEEP_FAIL_CANCEL_DAYS=0
KEEP_FAIL_CANCEL_COUNT=2
DRY_RUN=false
KEEP_DAYS_SET=false
KEEP_COUNT_SET=false
KEEP_FAIL_CANCEL_DAYS_SET=false
KEEP_FAIL_CANCEL_COUNT_SET=false

usage() {
    echo "Usage: $0 [--keep-days <days>] [--keep-count <n>] [--keep-fail-cancel-days <days>] [--keep-fail-cancel-count <n>] [--dry-run]"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --keep-days) KEEP_DAYS="$2"; KEEP_DAYS_SET=true; shift 2 ;;
        --keep-count) KEEP_COUNT="$2"; KEEP_COUNT_SET=true; shift 2 ;;
        --keep-fail-cancel-days) KEEP_FAIL_CANCEL_DAYS="$2"; KEEP_FAIL_CANCEL_DAYS_SET=true; shift 2 ;;
        --keep-fail-cancel-count) KEEP_FAIL_CANCEL_COUNT="$2"; KEEP_FAIL_CANCEL_COUNT_SET=true; shift 2 ;;
        --dry-run) DRY_RUN=true; shift ;;
        -h|--help) usage ;;
        *) usage ;;
    esac
done

if [[ ! -f "$QUEUE_FILE" && -f "$LEGACY_QUEUE_FILE" ]]; then
    cp "$LEGACY_QUEUE_FILE" "$QUEUE_FILE"
fi

if [[ ! -f "$QUEUE_FILE" ]]; then
    echo -e "${YELLOW}No queue file found: $QUEUE_FILE${NC}"
    exit 0
fi

if [[ -f "$SKILL_DIR/config/user.json" ]]; then
    CFG_KEEP_DAYS=$(python3 -c "import json; cfg=json.load(open('$SKILL_DIR/config/user.json', encoding='utf-8')); qa=(cfg.get('queueArchive') or cfg.get('archive') or {}); print(qa.get('keepDays', ''))" 2>/dev/null || true)
    CFG_KEEP_COUNT=$(python3 -c "import json; cfg=json.load(open('$SKILL_DIR/config/user.json', encoding='utf-8')); qa=(cfg.get('queueArchive') or cfg.get('archive') or {}); print(qa.get('keepCount', ''))" 2>/dev/null || true)
    CFG_FAIL_DAYS=$(python3 -c "import json; cfg=json.load(open('$SKILL_DIR/config/user.json', encoding='utf-8')); qa=(cfg.get('queueArchive') or cfg.get('archive') or {}); print(qa.get('keepFailedCancelledDays', ''))" 2>/dev/null || true)
    CFG_FAIL_COUNT=$(python3 -c "import json; cfg=json.load(open('$SKILL_DIR/config/user.json', encoding='utf-8')); qa=(cfg.get('queueArchive') or cfg.get('archive') or {}); print(qa.get('keepFailedCancelledCount', ''))" 2>/dev/null || true)
    [[ "$KEEP_DAYS_SET" != "true" && -n "$CFG_KEEP_DAYS" && "$CFG_KEEP_DAYS" =~ ^[0-9]+$ ]] && KEEP_DAYS="$CFG_KEEP_DAYS"
    [[ "$KEEP_COUNT_SET" != "true" && -n "$CFG_KEEP_COUNT" && "$CFG_KEEP_COUNT" =~ ^[0-9]+$ ]] && KEEP_COUNT="$CFG_KEEP_COUNT"
    [[ "$KEEP_FAIL_CANCEL_DAYS_SET" != "true" && -n "$CFG_FAIL_DAYS" && "$CFG_FAIL_DAYS" =~ ^[0-9]+$ ]] && KEEP_FAIL_CANCEL_DAYS="$CFG_FAIL_DAYS"
    [[ "$KEEP_FAIL_CANCEL_COUNT_SET" != "true" && -n "$CFG_FAIL_COUNT" && "$CFG_FAIL_COUNT" =~ ^[0-9]+$ ]] && KEEP_FAIL_CANCEL_COUNT="$CFG_FAIL_COUNT"
fi

if [[ ! "$KEEP_DAYS" =~ ^[0-9]+$ ]] || [[ ! "$KEEP_COUNT" =~ ^[0-9]+$ ]] || [[ ! "$KEEP_FAIL_CANCEL_DAYS" =~ ^[0-9]+$ ]] || [[ ! "$KEEP_FAIL_CANCEL_COUNT" =~ ^[0-9]+$ ]]; then
    echo -e "${RED}Error: keep/prune values must be non-negative integers${NC}"
    exit 1
fi

mkdir -p "$ARCHIVE_DIR"
ARCHIVE_FILE="$ARCHIVE_DIR/queue-history-$(date +%Y-%m).jsonl"
acquire_file_lock "$QUEUE_LOCK_DIR" 120 || exit 1

python3 <<PYEOF
import json
import time

queue_file = "$QUEUE_FILE"
archive_file = "$ARCHIVE_FILE"
keep_days = int("$KEEP_DAYS")
keep_count = int("$KEEP_COUNT")
keep_fail_cancel_days = int("$KEEP_FAIL_CANCEL_DAYS")
keep_fail_cancel_count = int("$KEEP_FAIL_CANCEL_COUNT")
dry_run = "$DRY_RUN" == "true"

terminal_statuses = {"done", "merged", "failed", "cancelled", "cleaned", "dispatch_failed"}
fail_cancel_statuses = {"failed", "cancelled", "dispatch_failed"}
now_ms = int(time.time() * 1000)
cutoff_ms = now_ms - keep_days * 24 * 60 * 60 * 1000
fail_cancel_cutoff_ms = now_ms - keep_fail_cancel_days * 24 * 60 * 60 * 1000

with open(queue_file, "r", encoding="utf-8") as f:
    data = json.load(f)

items = data.get("items", [])

def sort_ts(item):
    return (
        item.get("lastSyncedAt")
        or item.get("dispatchedAt")
        or item.get("claimedAt")
        or item.get("createdAt")
        or 0
    )

terminal = [i for i in items if i.get("status") in terminal_statuses]
activeish = [i for i in items if i.get("status") not in terminal_statuses]
terminal_sorted = sorted(terminal, key=sort_ts, reverse=True)
fail_cancel_sorted = [i for i in terminal_sorted if i.get("status") in fail_cancel_statuses]
non_fail_cancel_sorted = [i for i in terminal_sorted if i.get("status") not in fail_cancel_statuses]

keep_recent_ids = set(id(i) for i in non_fail_cancel_sorted[:keep_count])
keep_fail_cancel_ids = set(id(i) for i in fail_cancel_sorted[:keep_fail_cancel_count])

to_archive = []
kept_terminal = []
for i in terminal_sorted:
    ts = sort_ts(i)
    status = i.get("status")
    if id(i) in keep_recent_ids:
        kept_terminal.append(i); continue
    if status in fail_cancel_statuses and id(i) in keep_fail_cancel_ids:
        kept_terminal.append(i); continue
    if status in fail_cancel_statuses:
        if ts and ts < fail_cancel_cutoff_ms:
            to_archive.append(i)
        else:
            kept_terminal.append(i)
        continue
    if ts and ts < cutoff_ms:
        to_archive.append(i)
    else:
        kept_terminal.append(i)

remaining = activeish + kept_terminal
remaining.sort(key=lambda i: (i.get("createdAt") or 0), reverse=True)

archived_counts = {}
for rec in to_archive:
    s = rec.get("status", "unknown")
    archived_counts[s] = archived_counts.get(s, 0) + 1

if not dry_run:
    if to_archive:
        with open(archive_file, "a", encoding="utf-8") as f:
            for rec in to_archive:
                f.write(json.dumps(rec, ensure_ascii=False) + "\\n")
    data["items"] = remaining
    data["updatedAt"] = now_ms
    data["queueStats"] = {
        "queued": sum(1 for i in remaining if i.get("status") == "queued"),
        "claimed": sum(1 for i in remaining if i.get("status") == "claimed"),
        "dispatched": sum(1 for i in remaining if i.get("status") == "dispatched"),
        "running": sum(1 for i in remaining if i.get("status") == "running"),
        "terminal": sum(1 for i in remaining if i.get("status") in terminal_statuses),
        "other": sum(1 for i in remaining if i.get("status") not in terminal_statuses | {"queued","claimed","dispatched","running"}),
    }
    with open(queue_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if dry_run:
    print(f"Dry run: would archive {len(to_archive)} queue records to {archive_file}")
    print(f"Archive counts by status: {archived_counts}")
    print(f"Remaining queue records: {len(remaining)}")
else:
    print(f"Archived {len(to_archive)} queue records -> {archive_file}")
    print(f"Archive counts by status: {archived_counts}")
    print(f"Remaining queue records: {len(remaining)}")
PYEOF

