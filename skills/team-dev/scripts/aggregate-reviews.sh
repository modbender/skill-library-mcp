#!/bin/bash
# aggregate-reviews.sh - Aggregate multi-reviewer outputs into a single decision
# Skill: dev-team

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

RESULT_FILE=""
PRINT_ONLY=0

usage() {
    echo "Usage: $0 --file <review-results.json> [--print-only]"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --file) RESULT_FILE="$2"; shift 2 ;;
        --print-only) PRINT_ONLY=1; shift 1 ;;
        -h|--help) usage ;;
        *) usage ;;
    esac
done

[[ -z "$RESULT_FILE" ]] && usage
[[ ! -f "$RESULT_FILE" ]] && { echo "Result file not found: $RESULT_FILE" >&2; exit 1; }

AGG_FILE="${RESULT_FILE%.json}.aggregate.json"

python3 - <<PYEOF
import json, os, re, sys
from pathlib import Path

result_file = Path("$RESULT_FILE")
agg_file = Path("$AGG_FILE")
print_only = bool($PRINT_ONLY)

d = json.loads(result_file.read_text(encoding="utf-8"))
weights = {"codex": 1.0, "gemini": 0.8, "claude": 0.3}
min_completed = 2
claude_critical_only = True

cfg = Path("$SKILL_DIR/config/user.json")
if cfg.exists():
    try:
        c = json.loads(cfg.read_text(encoding="utf-8"))
        r = c.get("review", {})
        if isinstance(r.get("weights"), dict):
            for k,v in r["weights"].items():
                try:
                    weights[str(k)] = float(v)
                except Exception:
                    pass
        if r.get("minCompleted") is not None:
            try:
                min_completed = max(1, int(r.get("minCompleted")))
            except Exception:
                pass
        br = r.get("blockRules") or {}
        if isinstance(br, dict) and "claudeCriticalOnly" in br:
            claude_critical_only = bool(br.get("claudeCriticalOnly"))
    except Exception:
        pass

sev_order = ["critical", "high", "medium", "low", "info"]
sev_rank = {s:i for i,s in enumerate(sev_order)}

def parse_output(path_str):
    p = Path(path_str) if path_str else None
    if not p or not p.exists():
        return {"verdict": "CONCERNS", "findings": [], "raw": "", "parseError": "missing output file"}
    text = p.read_text(encoding="utf-8", errors="replace")
    verdict = "CONCERNS"
    m = re.search(r"(?im)^Verdict:\s*(PASS|CONCERNS|BLOCK)\b", text)
    if m:
        verdict = m.group(1).upper()
    findings = []
    for line in text.splitlines():
        mm = re.match(r"\s*-\s*\[(critical|high|medium|low|info)\]\s*(.+)$", line, flags=re.I)
        if mm:
            findings.append({
                "severity": mm.group(1).lower(),
                "text": mm.group(2).strip()
            })
    return {"verdict": verdict, "findings": findings, "raw": text}

reviewers = []
severity_counts = {k: 0 for k in sev_order}
weighted_score = 0.0
critical_from = []
high_from = []
all_findings = []

for r in d.get("reviewers", []):
    name = (r.get("name") or "").strip()
    parsed = parse_output(r.get("outputFile"))
    findings = parsed["findings"]
    verdict = parsed["verdict"]
    weight = float(weights.get(name, 0.5))
    exit_code = int(r.get("exitCode", 0))

    reviewer_rec = {
        "name": name,
        "weight": weight,
        "exitCode": exit_code,
        "posted": bool(r.get("posted", False)),
        "verdict": verdict,
        "findings": findings,
        "parseError": parsed.get("parseError")
    }
    reviewers.append(reviewer_rec)

    if verdict == "PASS":
        weighted_score += 1.0 * weight
    elif verdict == "CONCERNS":
        weighted_score += 0.2 * weight
    elif verdict == "BLOCK":
        weighted_score -= 1.0 * weight

    for f in findings:
        sev = f["severity"]
        if sev in severity_counts:
            severity_counts[sev] += 1
        item = {"reviewer": name, **f}
        all_findings.append(item)
        if sev == "critical":
            critical_from.append(name)
        if sev == "high":
            high_from.append(name)

completed = [r for r in reviewers if r["exitCode"] == 0]
completed_names = [r["name"] for r in completed]

codex_or_gemini_critical = any(r in {"codex", "gemini"} for r in critical_from)
codex_or_gemini_high = any(r in {"codex", "gemini"} for r in high_from)
claude_only_critical = bool(critical_from) and all(r == "claude" for r in critical_from)
claude_only_high = bool(high_from) and all(r == "claude" for r in high_from)

decision = "pass"
status = "waiting_human_approve"
recommended_action = "human_approve_or_merge"
reason = "all_clear"

if len(completed) < min_completed:
    decision = "human_attention"
    status = "review_human_attention"
    recommended_action = "rerun_missing_reviewers_or_manual_review"
    reason = "insufficient_reviewers"
elif codex_or_gemini_critical:
    decision = "changes_requested"
    status = "review_changes_requested"
    recommended_action = "send_fixup_to_pr_owner_subagent"
    reason = "critical_from_codex_or_gemini"
elif codex_or_gemini_high:
    decision = "changes_requested"
    status = "review_changes_requested"
    recommended_action = "send_fixup_to_pr_owner_subagent"
    reason = "high_from_codex_or_gemini"
elif claude_only_critical and claude_critical_only:
    decision = "human_attention"
    status = "review_human_attention"
    recommended_action = "manual_triage_claude_critical"
    reason = "claude_critical_unconfirmed"
elif claude_only_high:
    decision = "human_attention"
    status = "review_human_attention"
    recommended_action = "manual_triage_claude_high"
    reason = "claude_high_unconfirmed"
elif severity_counts["medium"] > 0 or severity_counts["low"] > 0 or severity_counts["info"] > 0:
    decision = "pass_with_concerns"
    status = "waiting_human_approve"
    recommended_action = "optional_fix_before_human_approve"
    reason = "non_blocking_findings"

if any(r["verdict"] == "BLOCK" for r in completed) and any(r["verdict"] == "PASS" for r in completed):
    # Escalate conflicting strong signals (except where already blocked by codex/gemini high/critical)
    if decision not in {"changes_requested"}:
        decision = "human_attention"
        status = "review_human_attention"
        recommended_action = "manual_triage_conflicting_reviews"
        reason = "conflicting_verdicts"

aggregate = {
    "schemaVersion": 1,
    "sourceFile": str(result_file),
    "generatedAt": d.get("generatedAt"),
    "pr": d.get("pr", {}),
    "reviewers": reviewers,
    "summary": {
        "completedCount": len(completed),
        "expectedCount": len(d.get("reviewers", [])),
        "minCompleted": min_completed,
        "completedReviewers": completed_names,
        "weightedScore": round(weighted_score, 3),
        "severityCounts": severity_counts,
        "criticalFrom": critical_from,
        "highFrom": high_from
    },
    "decision": {
        "verdict": decision,
        "taskStatus": status,
        "recommendedAction": recommended_action,
        "reason": reason,
        "humanApproveRequired": True
    },
    "findings": all_findings
}

if not print_only:
    agg_file.write_text(json.dumps(aggregate, ensure_ascii=False, indent=2), encoding="utf-8")

print(json.dumps(aggregate, ensure_ascii=False, indent=2))
PYEOF
