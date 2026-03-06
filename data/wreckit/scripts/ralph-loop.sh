#!/usr/bin/env bash
# wreckit — Ralph Loop gate validator
# Validates that IMPLEMENTATION_PLAN.md exists, has numbered tasks, and tracks completion
# Usage: ./ralph-loop.sh [project-path]
# Output: JSON with status PASS/FAIL/WARN

set -euo pipefail
PROJECT="${1:-.}"
MODE="${MODE:-${WRECKIT_MODE:-BUILD}}"
PROJECT="$(cd "$PROJECT" && pwd)"
cd "$PROJECT"

PLAN_FILE="IMPLEMENTATION_PLAN.md"
ISSUES_FILE=$(mktemp)

action_issue() {
  echo "$1" >> "$ISSUES_FILE"
}

STATUS="PASS"
TOTAL=0
COMPLETED=0

if [ ! -f "$PLAN_FILE" ]; then
  if [ "$MODE" = "AUDIT" ]; then
    STATUS="WARN"
    action_issue "Missing IMPLEMENTATION_PLAN.md (AUDIT mode)"
  else
    STATUS="FAIL"
    action_issue "Missing IMPLEMENTATION_PLAN.md (non-AUDIT mode)"
  fi
else
  while IFS= read -r line; do
    desc=""
    is_task=0
    completed=false

    if echo "$line" | grep -qE '^[0-9]+\.'; then
      is_task=1
      desc=$(echo "$line" | sed -E 's/^[0-9]+\.\s*//')
    elif echo "$line" | grep -qE '^- \[[xX ]\]'; then
      is_task=1
      desc=$(echo "$line" | sed -E 's/^- \[[xX ]\]\s*//')
      if echo "$line" | grep -qE '^- \[[xX]\]'; then
        completed=true
      fi
    fi

    if [ "$is_task" -eq 1 ]; then
      TOTAL=$((TOTAL + 1))
      if echo "$line" | grep -q '~~'; then
        completed=true
      fi
      if [ "$completed" = true ]; then
        COMPLETED=$((COMPLETED + 1))
      fi

      if [ -z "${desc//[[:space:]]/}" ]; then
        action_issue "Empty task description"
        if [ "$STATUS" = "PASS" ]; then STATUS="WARN"; fi
      fi

      if echo "$desc" | grep -qiE '\band\b'; then
        action_issue "Task contains 'and': $desc"
        if [ "$STATUS" = "PASS" ]; then STATUS="WARN"; fi
      fi
    fi
  done < "$PLAN_FILE"

  if [ "$TOTAL" -eq 0 ]; then
    action_issue "No tasks found in IMPLEMENTATION_PLAN.md"
    if [ "$STATUS" = "PASS" ]; then STATUS="WARN"; fi
  fi
fi

PENDING=$((TOTAL - COMPLETED))
if [ "$PENDING" -lt 0 ]; then
  PENDING=0
fi

python3 - "$ISSUES_FILE" "$STATUS" "$TOTAL" "$COMPLETED" "$PENDING" <<'PYEOF'
import json, sys
issues_path, status, total, completed, pending = sys.argv[1:]
with open(issues_path) as f:
    issues = [line.strip() for line in f if line.strip()]

data = {
    "status": status,
    "gate_result": status,
    "total_tasks": int(total),
    "completed": int(completed),
    "pending": int(pending),
    "issues": issues,
}
print(json.dumps(data))
PYEOF

rm -f "$ISSUES_FILE"
