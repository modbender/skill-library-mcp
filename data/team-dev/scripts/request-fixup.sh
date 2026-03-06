#!/bin/bash
# request-fixup.sh - Send aggregated review findings back to the PR owner subagent
# Skill: dev-team

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/utils.sh" ]]; then
    source "$SCRIPT_DIR/utils.sh"
else
    get_root_dir() { echo "$(dirname "$(dirname "$SCRIPT_DIR")")"; }
    RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
fi

SKILL_DIR="$(cd "$(dirname "$SCRIPT_DIR")" && pwd)"
TASKS_FILE="$SKILL_DIR/assets/active-tasks.json"
TASKS_LOCK_DIR="$(get_tasks_lock_dir)"
trap 'release_file_lock "$TASKS_LOCK_DIR"' EXIT

TARGET_BRANCH=""
TARGET_PR=""
REPO_ARG=""
SEND_TO_LIVE=1
SPAWN_IF_DEAD=0
DRY_RUN=0

usage() {
    echo "Usage: $0 (--branch <branch> | --pr <number>) [--repo <owner/repo>] [--no-send-live] [--spawn-if-dead] [--dry-run]"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --branch) TARGET_BRANCH="$2"; shift 2 ;;
        --pr) TARGET_PR="$2"; shift 2 ;;
        --repo) REPO_ARG="$2"; shift 2 ;;
        --no-send-live) SEND_TO_LIVE=0; shift 1 ;;
        --spawn-if-dead) SPAWN_IF_DEAD=1; shift 1 ;;
        --dry-run) DRY_RUN=1; shift 1 ;;
        -h|--help) usage ;;
        *) usage ;;
    esac
done

if [[ -z "$TARGET_BRANCH" && -z "$TARGET_PR" ]]; then
    usage
fi
if [[ ! -f "$TASKS_FILE" ]]; then
    echo -e "${RED}Error: active-tasks.json not found${NC}"
    exit 1
fi

TMP_JSON="$(mktemp)"
python3 - <<PYEOF > "$TMP_JSON"
import json, sys
from pathlib import Path

data = json.loads(Path("$TASKS_FILE").read_text(encoding="utf-8"))
target_branch = "$TARGET_BRANCH"
target_pr = "$TARGET_PR"
repo_arg = "$REPO_ARG"

match = None
for a in data.get("agents", []):
    checks = a.get("checks") or {}
    if target_branch and a.get("branch") == target_branch:
        match = a; break
    if target_pr and str(checks.get("prNumber") or "") == target_pr:
        if repo_arg and (checks.get("ghRepo") or a.get("repo")) not in {repo_arg, repo_arg.split("/")[-1]}:
            continue
        match = a; break

if not match:
    print(json.dumps({"ok": False, "error": "task_not_found"}, ensure_ascii=False))
    sys.exit(0)

checks = match.get("checks") or {}
agg = checks.get("reviewAggregate") or {}
agg_file = checks.get("reviewAggregateFile")

out = {
    "ok": True,
    "task": {
        "id": match.get("id"),
        "branch": match.get("branch"),
        "status": match.get("status"),
        "repo": match.get("repo"),
        "repoPath": match.get("repoPath"),
        "agent": match.get("agent"),
        "tmuxSession": match.get("tmuxSession"),
        "description": match.get("description"),
        "completionMode": match.get("completionMode"),
        "autoMerge": match.get("autoMerge"),
        "mergeMethod": match.get("mergeMethod"),
        "worktree": match.get("worktree"),
        "commandShell": match.get("commandShell"),
    },
    "checks": {
        "fixupSuggested": checks.get("fixupSuggested"),
        "fixupRecommendation": checks.get("fixupRecommendation"),
        "fixupTarget": checks.get("fixupTarget"),
        "reviewAggregate": agg,
        "reviewAggregateFile": agg_file,
        "reviewSummary": checks.get("reviewSummary"),
    }
}
print(json.dumps(out, ensure_ascii=False, indent=2))
PYEOF

INFO_JSON="$(cat "$TMP_JSON")"
OK=$(printf '%s' "$INFO_JSON" | python3 -c 'import sys,json; print(1 if json.load(sys.stdin).get("ok") else 0)')
if [[ "$OK" != "1" ]]; then
    echo -e "${RED}Error: task not found${NC}"
    rm -f "$TMP_JSON"
    exit 1
fi

BRANCH=$(printf '%s' "$INFO_JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["task"]["branch"])')
STATUS=$(printf '%s' "$INFO_JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["task"]["status"])')
REPO=$(printf '%s' "$INFO_JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["task"]["repo"])')
REPO_PATH=$(printf '%s' "$INFO_JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["task"]["repoPath"] or "")')
AGENT=$(printf '%s' "$INFO_JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["task"]["agent"])')
SESSION=$(printf '%s' "$INFO_JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["task"]["tmuxSession"] or "")')
DESC=$(printf '%s' "$INFO_JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["task"]["description"] or "")')
FIXUP_SUGGESTED=$(printf '%s' "$INFO_JSON" | python3 -c 'import sys,json; print(1 if json.load(sys.stdin)["checks"].get("fixupSuggested") else 0)')
FIXUP_RECOMMENDATION=$(printf '%s' "$INFO_JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["checks"].get("fixupRecommendation") or "")')
AGG_FILE=$(printf '%s' "$INFO_JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["checks"].get("reviewAggregateFile") or "")')

if [[ "$FIXUP_SUGGESTED" != "1" ]]; then
    echo -e "${YELLOW}No automatic fixup suggested for branch: $BRANCH${NC}"
    echo "Current status: $STATUS"
    echo "Recommendation: ${FIXUP_RECOMMENDATION:-none}"
    rm -f "$TMP_JSON"
    exit 0
fi

if [[ -z "$AGG_FILE" || ! -f "$AGG_FILE" ]]; then
    echo -e "${RED}Error: review aggregate file missing${NC}"
    rm -f "$TMP_JSON"
    exit 1
fi

FIXUP_PROMPT_FILE="$(mktemp "/tmp/dev-team-fixup-${AGENT}-XXXXXX.txt")"
python3 - <<PYEOF > "$FIXUP_PROMPT_FILE"
import json
from pathlib import Path

agg = json.loads(Path("$AGG_FILE").read_text(encoding="utf-8"))
task = json.loads('''$INFO_JSON''')["task"]
decision = agg.get("decision", {})
findings = agg.get("findings", [])

def bucket_priority(sev):
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    return order.get((sev or "").lower(), 9)

findings = sorted(findings, key=lambda x: (bucket_priority(x.get("severity")), x.get("reviewer","")))

print("你是该 PR 的负责 subagent，需要根据多 reviewer 聚合结果进行返工。")
print(f"分支: {task.get('branch')}")
print(f"仓库: {task.get('repoPath') or task.get('repo')}")
print(f"原任务: {task.get('description')}")
print()
print("目标：修复 reviewer 标出的阻塞问题；完成后提交 commit、push 同一分支，并更新现有 PR（不要新建 PR）。")
print()
print("聚合决策：")
print(f"- Verdict: {decision.get('verdict')}")
print(f"- Reason: {decision.get('reason')}")
print(f"- RecommendedAction: {decision.get('recommendedAction')}")
print()
print("需要优先处理的 Findings（按严重度排序）：")
if findings:
    for f in findings[:20]:
        print(f"- [{f.get('severity')}] reviewer={f.get('reviewer')} {f.get('text')}")
else:
    print("- 无结构化 findings；请查看 review comments 和 review 产物文件人工判断")
print()
print("执行要求：")
print("1. 先复现/确认问题，再修改代码，避免过度修复。")
print("2. 修复后运行最小必要验证（至少与问题相关的检查）。")
print("3. git commit 并 git push 到同一分支。")
print("4. 在输出中说明：修了什么 / 如何验证 / 剩余风险。")
print("5. 不要创建新 PR。")
PYEOF

echo "Fixup target branch: $BRANCH"
echo "Owner agent: $AGENT"
echo "Current status: $STATUS"
echo "Fixup recommendation: $FIXUP_RECOMMENDATION"
echo "Generated fixup prompt: $FIXUP_PROMPT_FILE"

LIVE=0
if [[ -n "$SESSION" ]] && tmux has-session -t "$SESSION" >/dev/null 2>&1; then
    LIVE=1
fi

if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "Dry-run only. Prompt file kept at: $FIXUP_PROMPT_FILE"
    rm -f "$TMP_JSON"
    exit 0
fi

if [[ "$SEND_TO_LIVE" -eq 1 && "$LIVE" -eq 1 ]]; then
    echo "Sending fixup prompt to live session: $SESSION"
    tmux load-buffer "$FIXUP_PROMPT_FILE"
    tmux paste-buffer -t "$SESSION"
    tmux send-keys -t "$SESSION" Enter
    SENT_MODE="live_session"
elif [[ "$SPAWN_IF_DEAD" -eq 1 ]]; then
    echo "Owner session is not live; spawning follow-up subagent on same branch..."
    if [[ -z "$REPO_PATH" || ! -d "$REPO_PATH" ]]; then
        echo -e "${RED}Error: repoPath not found for respawn${NC}"
        rm -f "$TMP_JSON"
        exit 1
    fi
    SPAWN_ARGS=(--agent "$AGENT" --repo-path "$REPO_PATH" --branch "$BRANCH" --description "fixup: $DESC" --completion-mode pr --prompt-file "$FIXUP_PROMPT_FILE")
    # preserve merge prefs if available
    AUTO_MERGE=$(printf '%s' "$INFO_JSON" | python3 -c 'import sys,json; print(1 if json.load(sys.stdin)["task"].get("autoMerge") else 0)')
    MERGE_METHOD=$(printf '%s' "$INFO_JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["task"].get("mergeMethod") or "")')
    [[ "$AUTO_MERGE" == "1" ]] && SPAWN_ARGS+=(--auto-merge)
    [[ -n "$MERGE_METHOD" ]] && SPAWN_ARGS+=(--merge-method "$MERGE_METHOD")
    "$SCRIPT_DIR/spawn-agent.sh" "${SPAWN_ARGS[@]}"
    SENT_MODE="respawned_subagent"
else
    echo -e "${YELLOW}Owner session not live. No action taken.${NC}"
    echo "Use --spawn-if-dead to respawn same branch owner agent."
    SENT_MODE="none"
fi

acquire_file_lock "$TASKS_LOCK_DIR" 60 || exit 1
python3 - <<PYEOF
import json, time
from pathlib import Path
p = Path("$TASKS_FILE")
d = json.loads(p.read_text(encoding="utf-8"))
for a in d.get("agents", []):
    if a.get("branch") == "$BRANCH":
        c = a.setdefault("checks", {})
        c["fixupRequestedAt"] = int(time.time() * 1000)
        c["fixupRequestMode"] = "$SENT_MODE"
        c["fixupPromptFile"] = "$FIXUP_PROMPT_FILE"
        c["fixupRequestedBy"] = "request-fixup.sh"
        break
p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
PYEOF

echo -e "${GREEN}Fixup request processed (${SENT_MODE})${NC}"
rm -f "$TMP_JSON"

