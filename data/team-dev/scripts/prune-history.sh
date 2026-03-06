#!/bin/bash
# prune-history.sh - Archive old completed task records from active-tasks.json
# Skill: dev-team

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/utils.sh" ]]; then
    source "$SCRIPT_DIR/utils.sh"
else
    get_root_dir() { echo "$(dirname "$(dirname "$SCRIPT_DIR")")"; }
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    NC='\033[0m'
fi

SKILL_DIR="$(cd "$(dirname "$SCRIPT_DIR")" && pwd)"
TASKS_FILE="$SKILL_DIR/assets/active-tasks.json"
TASKS_LOCK_DIR="$(get_tasks_lock_dir)"
ARCHIVE_DIR="$SKILL_DIR/assets/logs/archives"
trap 'release_file_lock "$TASKS_LOCK_DIR"' EXIT

KEEP_DAYS=0
KEEP_COUNT=12
KEEP_FAIL_CANCEL_DAYS=0
KEEP_FAIL_CANCEL_COUNT=2
DRY_RUN=false
KEEP_DAYS_SET=false
KEEP_COUNT_SET=false
KEEP_FAIL_CANCEL_DAYS_SET=false
KEEP_FAIL_CANCEL_COUNT_SET=false

usage() {
    echo "Usage: $0 [--keep-days <days>] [--keep-count <n>] [--keep-fail-cancel-days <days>] [--keep-fail-cancel-count <n>] [--dry-run]"
    echo ""
    echo "Options:"
    echo "  --keep-days    Archive completed records older than N days (default: 0, use config archive.keepDays)"
    echo "  --keep-count   Always keep the most recent N completed records (default: 12)"
    echo "  --keep-fail-cancel-days  Archive failed/cancelled older than N days (default: 0)"
    echo "  --keep-fail-cancel-count Always keep newest N failed/cancelled (default: 2)"
    echo "  --dry-run      Preview only, do not modify files"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --keep-days) KEEP_DAYS="$2"; KEEP_DAYS_SET=true; shift 2 ;;
        --keep-count) KEEP_COUNT="$2"; KEEP_COUNT_SET=true; shift 2 ;;
        --keep-fail-cancel-days) KEEP_FAIL_CANCEL_DAYS="$2"; KEEP_FAIL_CANCEL_DAYS_SET=true; shift 2 ;;
        --keep-fail-cancel-count) KEEP_FAIL_CANCEL_COUNT="$2"; KEEP_FAIL_CANCEL_COUNT_SET=true; shift 2 ;;
        --dry-run) DRY_RUN=true; shift ;;
        -h|--help) usage ;;
        *) usage ;;
    esac
done

if [[ -f "$SKILL_DIR/config/user.json" ]]; then
    CFG_KEEP_DAYS=$(python3 -c "import json; cfg=json.load(open('$SKILL_DIR/config/user.json', encoding='utf-8')); print((cfg.get('archive') or {}).get('keepDays', ''))" 2>/dev/null || true)
    CFG_KEEP_COUNT=$(python3 -c "import json; cfg=json.load(open('$SKILL_DIR/config/user.json', encoding='utf-8')); print((cfg.get('archive') or {}).get('keepCount', ''))" 2>/dev/null || true)
    CFG_FAIL_DAYS=$(python3 -c "import json; cfg=json.load(open('$SKILL_DIR/config/user.json', encoding='utf-8')); print((cfg.get('archive') or {}).get('keepFailedCancelledDays', ''))" 2>/dev/null || true)
    CFG_FAIL_COUNT=$(python3 -c "import json; cfg=json.load(open('$SKILL_DIR/config/user.json', encoding='utf-8')); print((cfg.get('archive') or {}).get('keepFailedCancelledCount', ''))" 2>/dev/null || true)
    [[ "$KEEP_DAYS_SET" != "true" && -n "$CFG_KEEP_DAYS" && "$CFG_KEEP_DAYS" =~ ^[0-9]+$ ]] && KEEP_DAYS="$CFG_KEEP_DAYS"
    [[ "$KEEP_COUNT_SET" != "true" && -n "$CFG_KEEP_COUNT" && "$CFG_KEEP_COUNT" =~ ^[0-9]+$ ]] && KEEP_COUNT="$CFG_KEEP_COUNT"
    [[ "$KEEP_FAIL_CANCEL_DAYS_SET" != "true" && -n "$CFG_FAIL_DAYS" && "$CFG_FAIL_DAYS" =~ ^[0-9]+$ ]] && KEEP_FAIL_CANCEL_DAYS="$CFG_FAIL_DAYS"
    [[ "$KEEP_FAIL_CANCEL_COUNT_SET" != "true" && -n "$CFG_FAIL_COUNT" && "$CFG_FAIL_COUNT" =~ ^[0-9]+$ ]] && KEEP_FAIL_CANCEL_COUNT="$CFG_FAIL_COUNT"
fi

if [[ ! "$KEEP_DAYS" =~ ^[0-9]+$ ]] || [[ ! "$KEEP_COUNT" =~ ^[0-9]+$ ]] || [[ ! "$KEEP_FAIL_CANCEL_DAYS" =~ ^[0-9]+$ ]] || [[ ! "$KEEP_FAIL_CANCEL_COUNT" =~ ^[0-9]+$ ]]; then
    echo -e "${RED}Error: keep/prune values must be non-negative integers${NC}"
    exit 1
fi

if [[ ! -f "$TASKS_FILE" ]]; then
    echo -e "${YELLOW}No tasks file found: $TASKS_FILE${NC}"
    exit 0
fi

mkdir -p "$ARCHIVE_DIR"
ARCHIVE_FILE="$ARCHIVE_DIR/task-history-$(date +%Y-%m).jsonl"
acquire_file_lock "$TASKS_LOCK_DIR" 120 || exit 1

python3 << PYEOF
import json
import os
import time

tasks_file = '$TASKS_FILE'
archive_file = '$ARCHIVE_FILE'
keep_days = int('$KEEP_DAYS')
keep_count = int('$KEEP_COUNT')
keep_fail_cancel_days = int('$KEEP_FAIL_CANCEL_DAYS')
keep_fail_cancel_count = int('$KEEP_FAIL_CANCEL_COUNT')
dry_run = '$DRY_RUN' == 'true'

terminal_statuses = {'done', 'failed', 'cancelled', 'cleaned', 'merged'}
fail_cancel_statuses = {'failed', 'cancelled'}
now_ms = int(time.time() * 1000)
cutoff_ms = now_ms - keep_days * 24 * 60 * 60 * 1000
fail_cancel_cutoff_ms = now_ms - keep_fail_cancel_days * 24 * 60 * 60 * 1000

with open(tasks_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

agents = data.get('agents', [])

def sort_ts(a):
    return (
        a.get('cleanedAt')
        or a.get('completedAt')
        or a.get('failedAt')
        or a.get('cancelledAt')
        or a.get('startedAt')
        or 0
    )

completed = [a for a in agents if a.get('status') in terminal_statuses]
running = [a for a in agents if a.get('status') not in terminal_statuses]
completed_sorted = sorted(completed, key=sort_ts, reverse=True)

fail_cancel_sorted = [a for a in completed_sorted if a.get('status') in fail_cancel_statuses]
non_fail_cancel_sorted = [a for a in completed_sorted if a.get('status') not in fail_cancel_statuses]
keep_fail_cancel_ids = set(id(a) for a in fail_cancel_sorted[:keep_fail_cancel_count])

keep_recent_ids = set()
for a in non_fail_cancel_sorted[:keep_count]:
    keep_recent_ids.add(id(a))

to_archive = []
kept_completed = []
for a in completed_sorted:
    ts = sort_ts(a)
    status = a.get('status')
    if id(a) in keep_recent_ids:
        kept_completed.append(a)
        continue
    if status in fail_cancel_statuses and id(a) in keep_fail_cancel_ids:
        kept_completed.append(a)
        continue
    if status in fail_cancel_statuses:
        if ts and ts < fail_cancel_cutoff_ms:
            to_archive.append(a)
        else:
            kept_completed.append(a)
        continue
    if ts and ts < cutoff_ms:
        to_archive.append(a)
    else:
        kept_completed.append(a)

remaining = running + kept_completed
remaining.sort(key=lambda a: (a.get('startedAt') or 0), reverse=True)

if dry_run:
    archived_counts = {}
    for rec in to_archive:
        s = rec.get('status', 'unknown')
        archived_counts[s] = archived_counts.get(s, 0) + 1
    print(f"Dry run: would archive {len(to_archive)} records to {archive_file}")
    print(f"Archive counts by status: {archived_counts}")
    print(f"Remaining records: {len(remaining)}")
else:
    if to_archive:
        with open(archive_file, 'a', encoding='utf-8') as f:
            for rec in to_archive:
                f.write(json.dumps(rec, ensure_ascii=False) + '\\n')

    data['agents'] = remaining
    data['activeCount'] = len([a for a in remaining if a.get('status') == 'running'])
    with open(tasks_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    archived_counts = {}
    for rec in to_archive:
        s = rec.get('status', 'unknown')
        archived_counts[s] = archived_counts.get(s, 0) + 1
    print(f"Archived {len(to_archive)} records -> {archive_file}")
    print(f"Archive counts by status: {archived_counts}")
    print(f"Remaining records: {len(remaining)}")
    print(f"Active agents: {data['activeCount']}")
PYEOF
