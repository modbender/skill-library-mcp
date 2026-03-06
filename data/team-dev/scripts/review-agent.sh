#!/bin/bash
# review-agent.sh - Run subagent reviews for a PR and post comments to GitHub
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
REPOS_BASE_DIR="$(dirname "$SKILL_DIR")"
TASKS_FILE="$SKILL_DIR/assets/active-tasks.json"
TASKS_LOCK_DIR="$(get_tasks_lock_dir)"
REVIEW_LOG_DIR="$SKILL_DIR/assets/logs/reviews"
trap 'release_file_lock "$TASKS_LOCK_DIR"' EXIT

check_dependency "gh" "GitHub CLI" || exit 1
check_dependency "git" "Git" || exit 1
check_dependency "python3" "Python 3" || exit 1

usage() {
    echo "Usage: $0 --repo <owner/repo|repo> --branch <branch|pr-number> [--reviewers codex,gemini,claude] [--no-post]"
    echo ""
    echo "Options:"
    echo "  --repo       Repository name (owner/repo preferred; bare repo also supported if local path exists)"
    echo "  --branch     Branch name or PR number"
    echo "  --reviewers  Comma-separated reviewers (default: codex,gemini,claude)"
    echo "  --no-post    Do not post review comments to GitHub (only save local review outputs)"
    echo "  --timeout    Reviewer command timeout in seconds (default: 180)"
    exit 1
}

REPO=""
BRANCH=""
REVIEWERS="codex,gemini,claude"
POST_TO_GH=1
REVIEW_TIMEOUT_SECONDS=180
ALLOW_FEWER_REVIEWERS=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --repo) REPO="$2"; shift 2 ;;
        --branch) BRANCH="$2"; shift 2 ;;
        --reviewers) REVIEWERS="$2"; shift 2 ;;
        --no-post) POST_TO_GH=0; shift 1 ;;
        --timeout) REVIEW_TIMEOUT_SECONDS="$2"; shift 2 ;;
        --allow-fewer-reviewers) ALLOW_FEWER_REVIEWERS=1; shift 1 ;;
        -h|--help) usage ;;
        *) usage ;;
    esac
done

if [[ -z "$REPO" || -z "$BRANCH" ]]; then
    usage
fi

if [[ -f "$SKILL_DIR/config/user.json" ]]; then
    if [[ "$REVIEWERS" == "codex,gemini,claude" ]]; then
        CFG_REVIEWERS=$(python3 - <<PYEOF
import json
try:
    cfg = json.load(open("$SKILL_DIR/config/user.json", "r", encoding="utf-8"))
    v = (cfg.get("review") or {}).get("requiredReviewers")
    if isinstance(v, list) and v:
        print(",".join([str(x) for x in v if x]))
except Exception:
    pass
PYEOF
)
        [[ -n "$CFG_REVIEWERS" ]] && REVIEWERS="$CFG_REVIEWERS"
    fi
fi

mkdir -p "$REVIEW_LOG_DIR"

echo "Starting code review for $REPO / $BRANCH"

PR_JSON=""
if [[ "$BRANCH" =~ ^[0-9]+$ ]]; then
    PR_JSON=$(gh pr view "$BRANCH" --repo "$REPO" --json number,url,title,headRefName,baseRefName 2>/dev/null || true)
else
    PR_JSON=$(gh pr view "$BRANCH" --repo "$REPO" --json number,url,title,headRefName,baseRefName 2>/dev/null || true)
    if [[ -z "$PR_JSON" ]]; then
        PR_JSON=$(gh pr list --head "$BRANCH" --repo "$REPO" --json number,url,title,headRefName,baseRefName -L 1 2>/dev/null || true)
        if [[ -n "$PR_JSON" ]]; then
            PR_JSON=$(printf '%s' "$PR_JSON" | python3 - <<'PY'
import json,sys
arr=json.load(sys.stdin)
print(json.dumps(arr[0]) if arr else "")
PY
)
        fi
    fi
fi

if [[ -z "$PR_JSON" ]]; then
    echo -e "${RED}Error: PR not found for $REPO / $BRANCH${NC}"
    exit 1
fi

PR_NUM=$(printf '%s' "$PR_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['number'])")
PR_URL=$(printf '%s' "$PR_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin).get('url',''))")
PR_TITLE=$(printf '%s' "$PR_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin).get('title',''))")
HEAD_REF=$(printf '%s' "$PR_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin).get('headRefName',''))")
BASE_REF=$(printf '%s' "$PR_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin).get('baseRefName',''))")

echo -e "${GREEN}PR #$PR_NUM found${NC}: $PR_TITLE"

REPO_PATH=""
if [[ "$REPO" == */* ]]; then
    local_name="${REPO##*/}"
    if [[ -d "$REPOS_BASE_DIR/$local_name" ]]; then
        REPO_PATH="$REPOS_BASE_DIR/$local_name"
    fi
else
    if [[ -d "$REPOS_BASE_DIR/$REPO" ]]; then
        REPO_PATH="$REPOS_BASE_DIR/$REPO"
    fi
fi

if [[ -z "$REPO_PATH" && -f "$TASKS_FILE" ]]; then
    REPO_PATH=$(python3 - <<PYEOF
import json
from pathlib import Path
d = json.loads(Path("$TASKS_FILE").read_text(encoding="utf-8"))
want = {"$HEAD_REF", "$BRANCH"}
for a in d.get("agents", []):
    if a.get("branch") in want and a.get("repoPath"):
        print(a["repoPath"])
        break
PYEOF
)
fi

if [[ -z "$REPO_PATH" ]]; then
    echo -e "${YELLOW}Warning: local repo path not found, reviewers may produce generic output${NC}"
fi

IFS=',' read -ra REVIEWER_ARRAY <<< "$REVIEWERS"
REVIEWER_COUNT=0
VALID_REVIEWERS=()
POLICY_REJECTED=()

ENABLED_AGENTS_CSV=""
PHASE_ALLOWED_REVIEW_CSV=""
if [[ -f "$SKILL_DIR/config/user.json" ]]; then
    _policy_lines_raw="$(python3 - <<PYEOF
import json
try:
    cfg = json.load(open("$SKILL_DIR/config/user.json", "r", encoding="utf-8"))
    policy = cfg.get("agentPolicy") or {}
    enabled = policy.get("enabledAgents")
    phase_allowed = (policy.get("phaseAllowedAgents") or {}).get("review")
    if isinstance(enabled, list) and enabled:
        print("ENABLED=" + ",".join(str(x) for x in enabled if x))
    if isinstance(phase_allowed, list) and phase_allowed:
        print("PHASE_REVIEW=" + ",".join(str(x) for x in phase_allowed if x))
except Exception:
    pass
PYEOF
)"
    while IFS= read -r _line; do
        case "$_line" in
            ENABLED=*) ENABLED_AGENTS_CSV="${_line#ENABLED=}" ;;
            PHASE_REVIEW=*) PHASE_ALLOWED_REVIEW_CSV="${_line#PHASE_REVIEW=}" ;;
        esac
    done <<EOF
$_policy_lines_raw
EOF
fi

for reviewer in "${REVIEWER_ARRAY[@]}"; do
    reviewer="$(echo "$reviewer" | tr -d ' ')"
    [[ -z "$reviewer" ]] && continue
    if [[ -n "$ENABLED_AGENTS_CSV" && ",$ENABLED_AGENTS_CSV," != *",$reviewer,"* ]]; then
        POLICY_REJECTED+=("$reviewer(disabled)")
        continue
    fi
    if [[ -n "$PHASE_ALLOWED_REVIEW_CSV" && ",$PHASE_ALLOWED_REVIEW_CSV," != *",$reviewer,"* ]]; then
        POLICY_REJECTED+=("$reviewer(review-phase-disallowed)")
        continue
    fi
    VALID_REVIEWERS+=("$reviewer")
    REVIEWER_COUNT=$((REVIEWER_COUNT + 1))
done

if [[ ${#POLICY_REJECTED[@]} -gt 0 ]]; then
    echo -e "${YELLOW}Warning: reviewers filtered by agentPolicy: ${POLICY_REJECTED[*]}${NC}"
fi

REVIEWER_ARRAY=("${VALID_REVIEWERS[@]}")
if [[ "$ALLOW_FEWER_REVIEWERS" -ne 1 && "$REVIEWER_COUNT" -lt 3 ]]; then
    echo -e "${RED}Error: review requires at least 3 reviewers by default (got $REVIEWER_COUNT)${NC}"
    echo "Use --allow-fewer-reviewers only for debugging."
    exit 1
fi

TS="$(date +%s)"
RESULTS_JSON="$REVIEW_LOG_DIR/review-${PR_NUM}-${TS}.json"
TMP_RESULTS="$RESULTS_JSON.tmp"
AGGREGATE_JSON="$REVIEW_LOG_DIR/review-${PR_NUM}-${TS}.aggregate.json"
PR_DIFF_FILE="$REVIEW_LOG_DIR/pr-${PR_NUM}-${TS}.diff.txt"
PR_DIFF_EXCERPT_FILE="$REVIEW_LOG_DIR/pr-${PR_NUM}-${TS}.diff.excerpt.txt"

if gh pr diff "$PR_NUM" --repo "$REPO" > "$PR_DIFF_FILE" 2>/dev/null; then
    python3 - <<PYEOF
from pathlib import Path
p = Path("$PR_DIFF_FILE")
text = p.read_text(encoding="utf-8", errors="replace")
max_chars = 12000
max_lines = 220
lines = text.splitlines()
excerpt = "\n".join(lines[:max_lines])
if len(excerpt) > max_chars:
    excerpt = excerpt[:max_chars]
if len(lines) > max_lines or len(text) > len(excerpt):
    excerpt += "\n\n[... diff truncated by dev-team review-agent ...]\n"
Path("$PR_DIFF_EXCERPT_FILE").write_text(excerpt, encoding="utf-8")
PYEOF
else
    printf '%s\n' "Diff unavailable (gh pr diff failed)." > "$PR_DIFF_EXCERPT_FILE"
fi

python3 - <<PYEOF
import json
with open("$TMP_RESULTS", "w", encoding="utf-8") as f:
    json.dump({
        "pr": {
            "repo": "$REPO",
            "number": int("$PR_NUM"),
            "url": "$PR_URL",
            "title": "$PR_TITLE",
            "headRef": "$HEAD_REF",
            "baseRef": "$BASE_REF"
        },
        "generatedAt": int($TS) * 1000,
        "postToGitHub": bool($POST_TO_GH),
        "diffArtifactFile": "$PR_DIFF_FILE",
        "diffExcerptFile": "$PR_DIFF_EXCERPT_FILE",
        "reviewers": []
    }, f, ensure_ascii=False, indent=2)
PYEOF

run_reviewer() {
    local reviewer="$1"
    local body_file="$2"
    local output_file="$3"
    local snippet_file="${4:-}"
    local prompt
    local diff_context
    diff_context="$(cat "$PR_DIFF_EXCERPT_FILE" 2>/dev/null || echo 'Diff unavailable')"
    prompt=$(printf '%s\n' \
"You are a dev-team PR review subagent." \
"REVIEWER_NAME: $reviewer" \
"PR_NUMBER: $PR_NUM" \
"PR_URL: $PR_URL" \
"REPO: $REPO" \
"BASE_REF: $BASE_REF" \
"HEAD_REF: $HEAD_REF" \
"" \
"请基于下面提供的 PR 元数据与 diff 摘要进行代码审查，并输出结构化结论。" \
"不要说你无法识别 PR 编号；上方 PR_NUMBER 和 PR_URL 为准。" \
"" \
"=== DIFF_EXCERPT_BEGIN ===" \
"$diff_context" \
"=== DIFF_EXCERPT_END ===" \
"" \
"输出格式必须为以下 5 段（中文）：" \
"" \
"Verdict: <PASS|CONCERNS|BLOCK>" \
"Summary:" \
"- ..." \
"" \
"Findings:" \
"- [severity] 文件:行 - 问题描述（如果没有写“无”）" \
"" \
"Validation:" \
"- 你审查时依据了什么（代码、diff、风险推断）" \
"" \
"Next Steps:" \
"- 给作者的可执行建议（如果没有写“无”）" \
"" \
"要求：" \
"1) 先给结论，再给细节。" \
"2) 不要输出多余寒暄。" \
"3) 如果 diff 信息不足，明确写出“信息不足”，并说明还需要哪些信息。")

    local ok=0
    local cmd_desc=""
    : > "$output_file"
    _run_review_cmd() {
        local _out_file="$1"
        local _cwd="$2"
        shift 2
        local _timeout_marker="${_out_file}.timeout"
        local _rc=0
        rm -f "$_timeout_marker"
        if [[ -n "$_cwd" ]]; then
            (cd "$_cwd" && "$@") >"$_out_file" 2>&1 &
        else
            "$@" >"$_out_file" 2>&1 &
        fi
        local _cmd_pid=$!
        (
            sleep "$REVIEW_TIMEOUT_SECONDS"
            if kill -0 "$_cmd_pid" 2>/dev/null; then
                echo "timeout" > "$_timeout_marker"
                kill -TERM "$_cmd_pid" >/dev/null 2>&1 || true
                sleep 1
                kill -KILL "$_cmd_pid" >/dev/null 2>&1 || true
            fi
        ) &
        local _watch_pid=$!
        wait "$_cmd_pid" || _rc=$?
        kill "$_watch_pid" >/dev/null 2>&1 || true
        wait "$_watch_pid" >/dev/null 2>&1 || true
        if [[ -f "$_timeout_marker" ]]; then
            echo "" >>"$_out_file"
            echo "[dev-team] reviewer command timeout after ${REVIEW_TIMEOUT_SECONDS}s" >>"$_out_file"
            rm -f "$_timeout_marker"
            return 124
        fi
        return $_rc
    }

    case "$reviewer" in
        codex)
            if command -v codex >/dev/null 2>&1; then
                cmd_desc="codex exec"
                if [[ -n "$REPO_PATH" ]]; then
                    _run_review_cmd "$output_file" "$REPO_PATH" codex exec --dangerously-bypass-approvals-and-sandbox "$prompt" || ok=$?
                else
                    _run_review_cmd "$output_file" "" codex exec --dangerously-bypass-approvals-and-sandbox "$prompt" || ok=$?
                fi
            else
                echo "codex not installed" >"$output_file"
                ok=127
            fi
            ;;
        claude)
            if command -v claude >/dev/null 2>&1; then
                cmd_desc="claude -p"
                if [[ -n "$REPO_PATH" ]]; then
                    _run_review_cmd "$output_file" "$REPO_PATH" claude --dangerously-skip-permissions -p "$prompt" || ok=$?
                else
                    _run_review_cmd "$output_file" "" claude --dangerously-skip-permissions -p "$prompt" || ok=$?
                fi
            else
                echo "claude not installed" >"$output_file"
                ok=127
            fi
            ;;
        gemini)
            if command -v gemini >/dev/null 2>&1; then
                cmd_desc="gemini (config)"
                gemini_argv=()
                if [[ -f "$SKILL_DIR/config/agents.json" ]]; then
                    while IFS= read -r line; do
                        [[ -n "$line" ]] && gemini_argv+=("$line")
                    done < <(python3 -c "
import json
try:
    d = json.load(open('$SKILL_DIR/config/agents.json', encoding='utf-8'))
    args = d.get('agents', {}).get('gemini', {}).get('args', [])
    for a in args:
        print(a)
except Exception:
    print('-p')
" 2>/dev/null)
                fi
                [[ ${#gemini_argv[@]} -eq 0 ]] && gemini_argv=(-p)
                if [[ -n "$REPO_PATH" ]]; then
                    _run_review_cmd "$output_file" "$REPO_PATH" gemini "${gemini_argv[@]}" "$prompt" || ok=$?
                else
                    _run_review_cmd "$output_file" "" gemini "${gemini_argv[@]}" "$prompt" || ok=$?
                fi
            else
                echo "gemini not installed" >"$output_file"
                ok=127
            fi
            ;;
        *)
            echo "Unknown reviewer: $reviewer" >"$output_file"
            ok=2
            ;;
    esac

    local verdict="CONCERNS"
    if grep -qi '^Verdict:[[:space:]]*PASS' "$output_file"; then
        verdict="PASS"
    elif grep -qi '^Verdict:[[:space:]]*BLOCK' "$output_file"; then
        verdict="BLOCK"
    elif grep -qi '信息不足' "$output_file"; then
        verdict="CONCERNS"
    fi

    local comment_file="$body_file"
    REVIEWER_NAME="$reviewer" \
    REVIEWER_VERDICT="$verdict" \
    REVIEWER_EXIT_CODE="$ok" \
    REVIEW_PR_NUM="$PR_NUM" \
    REVIEW_PR_URL="$PR_URL" \
    REVIEW_OUTPUT_FILE="$output_file" \
    REVIEW_DIFF_EXCERPT_FILE="$PR_DIFF_EXCERPT_FILE" \
    python3 - <<'PYEOF' > "$comment_file"
import os
import re
from pathlib import Path

reviewer = os.environ["REVIEWER_NAME"]
verdict = os.environ["REVIEWER_VERDICT"]
exit_code = int(os.environ.get("REVIEWER_EXIT_CODE", "0") or 0)
pr_num = os.environ["REVIEW_PR_NUM"]
pr_url = os.environ["REVIEW_PR_URL"]
output_file = Path(os.environ["REVIEW_OUTPUT_FILE"])
diff_excerpt_file = os.environ["REVIEW_DIFF_EXCERPT_FILE"]

full = output_file.read_text(encoding="utf-8", errors="replace")
lines = full.splitlines()

def collect_section(title: str):
    out = []
    in_section = False
    pattern = re.compile(rf"^\s*{re.escape(title)}\s*:?\s*$", re.I)
    next_section = re.compile(r"^\s*(Summary|Findings|Validation|Next Steps|Verdict)\s*:?\s*$", re.I)
    for line in lines:
        if pattern.match(line):
            in_section = True
            continue
        if in_section and next_section.match(line):
            break
        if in_section:
            s = line.strip()
            if s:
                out.append(s)
    return out

summary_lines = collect_section("Summary")
finding_lines = []
for line in lines:
    m = re.match(r"\s*-\s*\[(critical|high|medium|low|info)\]\s*(.+)$", line, flags=re.I)
    if m:
        finding_lines.append((m.group(1).lower(), m.group(2).strip()))

sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
finding_lines.sort(key=lambda x: sev_order.get(x[0], 9))
top_findings = finding_lines[:3]
sev_counts = {}
for sev, _ in finding_lines:
    sev_counts[sev] = sev_counts.get(sev, 0) + 1

summary_bullets = []
for raw in summary_lines:
    text = raw.lstrip("-").strip()
    if not text:
        continue
    if text.lower().startswith("loaded cached credentials"):
        continue
    if text.lower().startswith("verdict:"):
        continue
    if text in {"...", "…"}:
        continue
    if text.lower().startswith("[dev-team] reviewer command timeout"):
        continue
    summary_bullets.append(text)
summary_bullets = summary_bullets[:2]

verdict_cn = {"PASS": "通过", "CONCERNS": "有关注项", "BLOCK": "阻塞"}.get(verdict, verdict)

print(f"[dev-team][reviewer={reviewer}]")
print()
print(f"**AI 审核摘要（{reviewer}）**")
print()
print(f"- 结论: `{verdict}`（{verdict_cn}）")
print(f"- PR: #{pr_num} ({pr_url})")
if exit_code == 124:
    print("- 执行状态: `timeout`（本次 reviewer 超时，以下为部分结果/保守结论）")
if sev_counts:
    sev_text = ", ".join(f"{k}:{v}" for k, v in sorted(sev_counts.items(), key=lambda kv: sev_order.get(kv[0], 9)))
    print(f"- 问题统计: `{sev_text}`")
else:
    print("- 问题统计: `无`")
if summary_bullets:
    print("- 摘要:")
    for item in summary_bullets:
        print(f"  - {item}")
if top_findings:
    print("- 重点问题（Top 3）:")
    for sev, text in top_findings:
        print(f"  - [{sev}] {text}")
else:
    print("- 重点问题（Top 3）: 无")
print("- 详细内容: 本地产物（不贴长文到 PR）")
print(f"  - review: `{output_file}`")
print(f"  - diff excerpt: `{diff_excerpt_file}`")
PYEOF

    # Write snippet for later merge (allows parallel run)
    if [[ -n "$4" ]]; then
        python3 - <<PYEOF
import json
from pathlib import Path
Path("$4").write_text(json.dumps({
  "name": "$reviewer",
  "command": "$cmd_desc",
  "exitCode": int("$ok"),
  "verdict": "$verdict",
  "outputFile": "$output_file",
  "commentFile": "$comment_file",
  "posted": False
}, ensure_ascii=False, indent=2), encoding="utf-8")
PYEOF
    fi
}

# Run all reviewers in parallel (each writes a snippet file)
for reviewer in "${REVIEWER_ARRAY[@]}"; do
    reviewer="$(echo "$reviewer" | tr -d ' ')"
    [[ -z "$reviewer" ]] && continue
    echo "=== Starting $reviewer review (parallel) ==="
    OUT_FILE="$REVIEW_LOG_DIR/pr-${PR_NUM}-${reviewer}-${TS}.out.txt"
    COMMENT_FILE="$REVIEW_LOG_DIR/pr-${PR_NUM}-${reviewer}-${TS}.comment.md"
    SNIPPET_FILE="$REVIEW_LOG_DIR/pr-${PR_NUM}-${reviewer}-${TS}.snippet.json"
    run_reviewer "$reviewer" "$COMMENT_FILE" "$OUT_FILE" "$SNIPPET_FILE" &
done
wait
echo ""

# Merge snippet files into TMP_RESULTS
python3 - <<PYEOF
import json
from pathlib import Path
tasks = Path("$TMP_RESULTS")
data = json.loads(tasks.read_text(encoding="utf-8"))
data["reviewers"] = []
for s in Path("$REVIEW_LOG_DIR").glob("pr-${PR_NUM}-*-${TS}.snippet.json"):
    try:
        r = json.loads(s.read_text(encoding="utf-8"))
        data["reviewers"].append(r)
    except Exception:
        pass
tasks.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
PYEOF

mv "$TMP_RESULTS" "$RESULTS_JSON"

# Post PR comments (serial to avoid rate limits)
for reviewer in "${REVIEWER_ARRAY[@]}"; do
    reviewer="$(echo "$reviewer" | tr -d ' ')"
    [[ -z "$reviewer" ]] && continue
    COMMENT_FILE="$REVIEW_LOG_DIR/pr-${PR_NUM}-${reviewer}-${TS}.comment.md"
    if [[ "$POST_TO_GH" -eq 1 ]]; then
        echo "Posting PR comment for reviewer=$reviewer ..."
        if gh pr comment "$PR_NUM" --repo "$REPO" --body-file "$COMMENT_FILE" >/dev/null 2>&1; then
            python3 - <<PYEOF
import json
from pathlib import Path
p = Path("$RESULTS_JSON")
d = json.loads(p.read_text(encoding="utf-8"))
for r in d.get("reviewers", []):
    if r.get("name") == "$reviewer":
        r["posted"] = True
p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
PYEOF
            echo -e "${GREEN}Posted PR comment for $reviewer${NC}"
        else
            echo -e "${YELLOW}Warning: Failed to post PR comment for $reviewer${NC}"
        fi
    fi
done

AGGREGATE_OUTPUT=$("$SCRIPT_DIR/aggregate-reviews.sh" --file "$RESULTS_JSON" 2>/dev/null || true)
if [[ -n "$AGGREGATE_OUTPUT" ]]; then
    printf '%s' "$AGGREGATE_OUTPUT" > "$AGGREGATE_JSON"
else
    AGGREGATE_OUTPUT="{}"
fi

if [[ "$POST_TO_GH" -eq 1 ]]; then
    AGG_SUMMARY_COMMENT="$REVIEW_LOG_DIR/pr-${PR_NUM}-aggregate-${TS}.comment.md"
    AGG_JSON_ENV="$AGGREGATE_JSON" python3 - <<'PYEOF' > "$AGG_SUMMARY_COMMENT"
import json, os
from pathlib import Path
p = Path(os.environ["AGG_JSON_ENV"])
agg = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
dec = agg.get("decision", {})
summ = agg.get("summary", {})
pr = agg.get("pr", {})
findings = agg.get("findings", [])

sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
top_findings = sorted(
    findings,
    key=lambda x: (sev_order.get(str(x.get("severity","")).lower(), 9), str(x.get("reviewer","")))
)[:3]

verdict = dec.get('verdict','unknown')
verdict_cn = {
    "pass": "通过",
    "pass_with_concerns": "通过（有关注项）",
    "changes_requested": "需要修改",
    "human_attention": "需人工判断",
}.get(verdict, verdict)

task_status = dec.get('taskStatus','unknown')
task_status_cn = {
    "waiting_human_approve": "等待人工批准",
    "review_changes_requested": "建议返工修改",
    "review_human_attention": "需要人工判断",
}.get(task_status, task_status)

need_fix = task_status == "review_changes_requested"
optional_fix = verdict == "pass_with_concerns"

reviewers = agg.get("reviewers", [])
reviewer_line = []
for r in reviewers:
    reviewer_line.append(f"{r.get('name')}={r.get('verdict')}({r.get('exitCode')})")

sev_counts = summ.get('severityCounts', {}) or {}
sev_counts_text = ", ".join(
    f"{k}:{sev_counts.get(k,0)}"
    for k in ["critical","high","medium","low","info"]
    if sev_counts.get(k,0)
) or "无"

print("[dev-team][review-aggregate]")
print()
print("**AI 审核聚合结论（给人类决策）**")
print()
print(f"- PR: #{pr.get('number','?')} ({pr.get('url','')})")
print(f"- 聚合结论: `{verdict}`（{verdict_cn}）")
print(f"- 状态建议: `{task_status}`（{task_status_cn}）")
print(f"- 是否建议作者修改: {'是（必须）' if need_fix else ('可选' if optional_fix else '否')}")
print(f"- 你现在可执行: {'要求修改 / 触发 fixup' if need_fix else ('人工判断后决定' if task_status == 'review_human_attention' else '人工 approve（如认可可直接继续）')}")
print(f"- Reviewer 摘要: `{', '.join(reviewer_line)}`")
print(f"- 问题统计: `{sev_counts_text}`")
if top_findings:
    print("- 重点问题（Top 3）:")
    for f in top_findings:
        print(f"  - [{f.get('severity')}] {f.get('reviewer')}: {f.get('text')}")
else:
    print("- 重点问题（Top 3）: 无")
print("- 详细聚合产物（本地）:")
print(f"  - `{p}`")
PYEOF
    gh pr comment "$PR_NUM" --repo "$REPO" --body-file "$AGG_SUMMARY_COMMENT" >/dev/null 2>&1 || \
        echo -e "${YELLOW}Warning: Failed to post aggregate review comment${NC}"
fi

echo ""
echo "=== All reviews completed ==="
echo "Reviewers used: ${REVIEWER_ARRAY[*]}"
echo "Saved results: $RESULTS_JSON"
echo "Saved aggregate: $AGGREGATE_JSON"
[[ "$POST_TO_GH" -eq 1 ]] && echo "Posted comments to: $PR_URL"

if [[ -f "$TASKS_FILE" ]]; then
    acquire_file_lock "$TASKS_LOCK_DIR" 60 || exit 1
    python3 <<PYEOF
import json
from pathlib import Path
tasks = Path("$TASKS_FILE")
data = json.loads(tasks.read_text(encoding="utf-8"))
results = json.loads(Path("$RESULTS_JSON").read_text(encoding="utf-8"))
aggregate = json.loads(Path("$AGGREGATE_JSON").read_text(encoding="utf-8")) if Path("$AGGREGATE_JSON").exists() else {}
target_branch = "$HEAD_REF" or "$BRANCH"
for agent in data.get("agents", []):
    if agent.get("branch") == target_branch or agent.get("branch") == "$BRANCH":
        checks = agent.setdefault("checks", {})
        checks["codeReviewDone"] = True
        checks["reviewArtifactsFile"] = "$RESULTS_JSON"
        checks["reviewAggregateFile"] = "$AGGREGATE_JSON"
        checks["reviewPostedToGitHub"] = bool($POST_TO_GH)
        checks["reviewSummary"] = [
            {
                "name": r.get("name"),
                "verdict": r.get("verdict"),
                "exitCode": r.get("exitCode"),
                "posted": r.get("posted", False)
            }
            for r in results.get("reviewers", [])
        ]
        checks["reviewAggregate"] = aggregate.get("decision")
        checks["reviewAggregateSummary"] = aggregate.get("summary")

        decision = (aggregate.get("decision") or {})
        suggested_status = decision.get("taskStatus")
        reason = decision.get("reason")
        checks["fixupSuggested"] = suggested_status == "review_changes_requested"
        checks["fixupRecommendation"] = decision.get("recommendedAction")
        checks["fixupTarget"] = {
            "branch": target_branch,
            "agent": agent.get("agent"),
            "repoPath": agent.get("repoPath"),
        }

        # review-agent 负责“多 reviewer 结论生成与回写”；approve 仍由人手动完成
        terminal_statuses = {"cleaned", "merged", "done", "failed", "cancelled"}
        if agent.get("status") in terminal_statuses:
            pass
        elif suggested_status in {"review_changes_requested", "review_human_attention", "waiting_human_approve"}:
            old_status = agent.get("status")
            if old_status != suggested_status:
                agent["status"] = suggested_status
                agent.setdefault("statusHistory", []).append({
                    "from": old_status,
                    "to": suggested_status,
                    "at": int("$TS") * 1000,
                    "reason": f"review_aggregate:{reason}"
                })
        elif agent.get("status") == "waiting_review":
            agent["status"] = "review_commented"

data["activeCount"] = len([a for a in data.get("agents", []) if a.get("status") == "running"])
tasks.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
PYEOF
fi
