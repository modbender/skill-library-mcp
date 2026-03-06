#!/bin/bash
# list-queue.sh - List queued/claimed/dispatched tasks
# Skill: dev-team

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
QUEUE_FILE="$SKILL_DIR/assets/tasks.json"
LEGACY_QUEUE_FILE="$SKILL_DIR/queue/tasks.json"

STATUS_FILTER=""
PHASE_FILTER=""
FORMAT="table"

usage() {
    echo "Usage: $0 [--status queued|claimed|dispatched|all] [--phase build|review|fixup] [--format table|json]"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --status) STATUS_FILTER="$2"; shift 2 ;;
        --phase) PHASE_FILTER="$2"; shift 2 ;;
        --format) FORMAT="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) usage ;;
    esac
done

[[ -z "$STATUS_FILTER" || "$STATUS_FILTER" =~ ^(queued|claimed|dispatched|all)$ ]] || { echo "Invalid --status" >&2; exit 1; }
[[ -z "$PHASE_FILTER" || "$PHASE_FILTER" =~ ^(build|review|fixup)$ ]] || { echo "Invalid --phase" >&2; exit 1; }
[[ "$FORMAT" =~ ^(table|json)$ ]] || { echo "Invalid --format" >&2; exit 1; }

if [[ ! -f "$QUEUE_FILE" && -f "$LEGACY_QUEUE_FILE" ]]; then
    QUEUE_FILE="$LEGACY_QUEUE_FILE"
fi

if [[ ! -f "$QUEUE_FILE" ]]; then
    if [[ "$FORMAT" == "json" ]]; then
        echo '{"items":[]}'
    else
        echo "No queue file found: $QUEUE_FILE"
    fi
    exit 0
fi

python3 <<PYEOF
import json

data = json.load(open("$QUEUE_FILE", "r", encoding="utf-8"))
items = data.get("items", [])
status_filter = "$STATUS_FILTER"
phase_filter = "$PHASE_FILTER"
fmt = "$FORMAT"

def match(item):
    if status_filter and status_filter != "all" and item.get("status") != status_filter:
        return False
    if phase_filter and item.get("phase") != phase_filter:
        return False
    return True

rows = [i for i in items if match(i)]

if fmt == "json":
    print(json.dumps({"items": rows}, ensure_ascii=False, indent=2))
    raise SystemExit(0)

if not rows:
    print("Queue is empty (after filters)")
    raise SystemExit(0)

print(f"{'ID':<22} {'STATUS':<11} {'PHASE':<7} {'PRI':<6} {'AGENTS':<20} BRANCH")
for i in rows:
    agents = i.get("preferredAgents") or i.get("allowedAgents") or []
    agents_s = ",".join(agents[:3]) if agents else "-"
    if len(agents_s) > 20:
        agents_s = agents_s[:17] + "..."
    print(f"{(i.get('id') or '')[:22]:<22} {(i.get('status') or ''):<11} {(i.get('phase') or ''):<7} {(i.get('priority') or ''):<6} {agents_s:<20} {i.get('branch') or ''}")
PYEOF
