#!/usr/bin/env bash
# daily-ops.sh — GitHub daily health check for Zero2Ai-hub
# Runs: Dependabot auto-merge, CI failure check, open PR/issue review, workspace push
# Output: /tmp/github-daily-ops-report.md

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT="/tmp/github-daily-ops-report.md"
WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
TODAY=$(date -u +"%Y-%m-%d %H:%M UTC")

REPOS=(
  "Zero2Ai-hub/Jarvis-Ops"
  "Zero2Ai-hub/Zeerotoai.com"
  "Zero2Ai-hub/openclaw-skills"
)

# ── Auth ──────────────────────────────────────────────────────────────────────
export GH_TOKEN="${GH_TOKEN:-$(cat ~/.github_token 2>/dev/null || echo '')}"
if [[ -z "$GH_TOKEN" ]]; then
  echo "❌ GH_TOKEN not set and ~/.github_token not found" >&2
  exit 1
fi

echo "⚡ Jarvis GitHub Daily Ops — ${TODAY}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── Report init ───────────────────────────────────────────────────────────────
cat > "$REPORT" <<EOF
# ⚡ GitHub Daily Ops Report
**Generated:** ${TODAY}
**Repos:** ${REPOS[*]}

---
EOF

# ── Section helpers ───────────────────────────────────────────────────────────
report_section() {
  echo "" >> "$REPORT"
  echo "## $1" >> "$REPORT"
}

report_line() {
  echo "$1" >> "$REPORT"
}

# ── 1. Dependabot Auto-merge ──────────────────────────────────────────────────
echo ""
echo "🤖 STEP 1: Dependabot Auto-merge"
echo "─────────────────────────────────"
report_section "🤖 Dependabot Auto-merge"

MERGED_PRS=()
SKIPPED_PRS=()
FAILED_MERGE=()

for REPO in "${REPOS[@]}"; do
  echo "  📦 ${REPO}"
  report_line ""
  report_line "### ${REPO}"

  prs_json=$(gh pr list \
    --repo "${REPO}" \
    --author "app/dependabot" \
    --state open \
    --json number,title,headRefOid,url \
    2>/dev/null || echo "[]")

  pr_count=$(echo "$prs_json" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo 0)

  if [[ "$pr_count" -eq 0 ]]; then
    echo "  ✓ No open Dependabot PRs"
    report_line "✓ No open Dependabot PRs"
    continue
  fi

  echo "  Found ${pr_count} Dependabot PR(s)"

  while IFS='|' read -r number title sha url; do
    echo "  🔍 PR #${number}: ${title}"

    # Get check runs
    checks_json=$(gh api "repos/${REPO}/commits/${sha}/check-runs" 2>/dev/null || echo '{"check_runs":[]}')

    total=$(echo "$checks_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('check_runs',[])))")
    pending=$(echo "$checks_json" | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(sum(1 for r in d.get('check_runs',[]) if r['status'] in ('in_progress','queued')))
")
    failed=$(echo "$checks_json" | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(sum(1 for r in d.get('check_runs',[]) if r.get('conclusion') in ('failure','cancelled','timed_out')))
")

    if [[ "$total" -eq 0 ]]; then
      echo "    ⚠️  No CI checks — skipping"
      report_line "- ⚠️ PR #${number} [${title}](${url}) — no CI checks, skipped"
      SKIPPED_PRS+=("${REPO}#${number}")
    elif [[ "$pending" -gt 0 ]]; then
      echo "    ⏳ CI pending (${pending}/${total}) — skipping"
      report_line "- ⏳ PR #${number} [${title}](${url}) — CI pending (${pending}/${total})"
      SKIPPED_PRS+=("${REPO}#${number}")
    elif [[ "$failed" -gt 0 ]]; then
      echo "    ❌ CI failed (${failed} failure(s)) — skipping"
      report_line "- ❌ PR #${number} [${title}](${url}) — CI failed, skipped"
      SKIPPED_PRS+=("${REPO}#${number}")
    else
      echo "    ✅ CI green — merging..."
      if gh pr merge "${number}" --repo "${REPO}" --squash --delete-branch 2>/dev/null; then
        echo "    🎉 Merged!"
        report_line "- ✅ PR #${number} [${title}](${url}) — **MERGED** 🎉"
        MERGED_PRS+=("${REPO}#${number}: ${title}")
      else
        echo "    ⚠️  Merge failed (branch protection?)"
        report_line "- ⚠️ PR #${number} [${title}](${url}) — merge failed (branch protection?)"
        FAILED_MERGE+=("${REPO}#${number}: ${title}")
      fi
    fi
  done < <(echo "$prs_json" | python3 -c "
import sys, json
for pr in json.load(sys.stdin):
    print(f\"{pr['number']}|{pr['title']}|{pr['headRefOid']}|{pr['url']}\")
")
done

# ── 2. Failed CI Runs ─────────────────────────────────────────────────────────
echo ""
echo "🚨 STEP 2: Failed CI Runs (last 24h)"
echo "─────────────────────────────────────"
report_section "🚨 Failed CI Runs (last 24h)"

FAILED_CI=()

for REPO in "${REPOS[@]}"; do
  echo "  📦 ${REPO}"
  report_line ""
  report_line "### ${REPO}"

  # Get workflow runs that failed in last 24h
  since=$(date -u -d '24 hours ago' +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u -v-24H +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || echo "")

  failed_runs=$(gh run list \
    --repo "${REPO}" \
    --status failure \
    --limit 10 \
    --json databaseId,name,headBranch,createdAt,url \
    2>/dev/null || echo "[]")

  run_count=$(echo "$failed_runs" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo 0)

  if [[ "$run_count" -eq 0 ]]; then
    echo "  ✓ No failed runs"
    report_line "✓ No failed CI runs"
  else
    echo "  ⚠️  ${run_count} failed run(s):"
    echo "$failed_runs" | python3 -c "
import sys, json
for r in json.load(sys.stdin):
    print(f\"    ❌ [{r['name']}] branch: {r['headBranch']} — {r['url']}\")
" | while read -r line; do
      echo "$line"
      report_line "- $line"
      FAILED_CI+=("$line")
    done
  fi
done

# ── 3. Open Issues & PRs needing review ───────────────────────────────────────
echo ""
echo "📋 STEP 3: Open Issues & PRs Needing Review"
echo "─────────────────────────────────────────────"
report_section "📋 Open Issues & PRs Needing Review"

for REPO in "${REPOS[@]}"; do
  echo "  📦 ${REPO}"
  report_line ""
  report_line "### ${REPO}"

  # Open PRs (non-Dependabot)
  open_prs=$(gh pr list \
    --repo "${REPO}" \
    --state open \
    --json number,title,author,url,reviewDecision,isDraft \
    2>/dev/null || echo "[]")

  human_prs=$(echo "$open_prs" | python3 -c "
import sys, json
prs = [p for p in json.load(sys.stdin) if p['author']['login'] != 'dependabot[bot]' and not p.get('isDraft')]
for p in prs:
    decision = p.get('reviewDecision') or 'NEEDS_REVIEW'
    print(f\"PR #{p['number']}: {p['title']} [{decision}] — {p['url']}\")
print(f'__COUNT__{len(prs)}')
" 2>/dev/null || echo "__COUNT__0")

  pr_count=$(echo "$human_prs" | grep '__COUNT__' | sed 's/__COUNT__//')
  pr_lines=$(echo "$human_prs" | grep -v '__COUNT__')

  if [[ "$pr_count" -gt 0 ]]; then
    echo "  📝 ${pr_count} open PR(s):"
    while IFS= read -r line; do
      [[ -z "$line" ]] && continue
      echo "    • ${line}"
      report_line "- 📝 ${line}"
    done <<< "$pr_lines"
  else
    report_line "✓ No open human PRs"
  fi

  # Open Issues
  open_issues=$(gh issue list \
    --repo "${REPO}" \
    --state open \
    --limit 10 \
    --json number,title,author,url,labels \
    2>/dev/null || echo "[]")

  issue_count=$(echo "$open_issues" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo 0)

  if [[ "$issue_count" -gt 0 ]]; then
    echo "  🐛 ${issue_count} open issue(s):"
    echo "$open_issues" | python3 -c "
import sys, json
for i in json.load(sys.stdin):
    labels = ', '.join(l['name'] for l in i.get('labels', []))
    label_str = f' [{labels}]' if labels else ''
    print(f\"    • Issue #{i['number']}: {i['title']}{label_str} — {i['url']}\")
" | while IFS= read -r line; do
      echo "$line"
      report_line "- 🐛 ${line}"
    done
  else
    report_line "✓ No open issues"
  fi

  if [[ "$pr_count" -eq 0 ]] && [[ "$issue_count" -eq 0 ]]; then
    echo "  ✓ All clear"
  fi
done

# ── 4. Push workspace commits ─────────────────────────────────────────────────
echo ""
echo "📤 STEP 4: Push Workspace Commits"
echo "──────────────────────────────────"
report_section "📤 Workspace Push"

if [[ -d "${WORKSPACE}/.git" ]]; then
  cd "${WORKSPACE}"

  # Check for unpushed commits
  unpushed=$(git log @{u}..HEAD --oneline 2>/dev/null || echo "")
  uncommitted=$(git status --porcelain 2>/dev/null || echo "")

  if [[ -n "$uncommitted" ]]; then
    echo "  ⚠️  Uncommitted changes in workspace (not auto-committing)"
    report_line "⚠️ Uncommitted changes present — manual commit required"
    git status --short
  fi

  if [[ -n "$unpushed" ]]; then
    commit_count=$(echo "$unpushed" | wc -l)
    echo "  📤 Pushing ${commit_count} unpushed commit(s)..."
    echo "$unpushed" | while read -r line; do echo "    • $line"; done

    if git push 2>&1; then
      echo "  ✅ Push successful"
      report_line "✅ Pushed ${commit_count} commit(s):"
      echo "$unpushed" | while IFS= read -r line; do
        report_line "- \`${line}\`"
      done
    else
      echo "  ❌ Push failed"
      report_line "❌ Push failed — check remote/auth"
    fi
  else
    echo "  ✓ Workspace is up to date"
    report_line "✓ No unpushed commits"
  fi
else
  echo "  ⚠️  Workspace is not a git repo"
  report_line "⚠️ Workspace at ${WORKSPACE} is not a git repo"
fi

# ── 5. Summary ────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 DAILY OPS SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Dependabot PRs merged : ${#MERGED_PRS[@]}"
echo "⏭️  PRs skipped           : ${#SKIPPED_PRS[@]}"
echo "⚠️  Merge failures        : ${#FAILED_MERGE[@]}"
echo "🚨 Failed CI runs        : ${#FAILED_CI[@]}"
echo ""
echo "📄 Full report: ${REPORT}"

report_section "📊 Summary"
report_line ""
report_line "| Metric | Count |"
report_line "|--------|-------|"
report_line "| Dependabot PRs merged | ${#MERGED_PRS[@]} |"
report_line "| PRs skipped (CI not ready) | ${#SKIPPED_PRS[@]} |"
report_line "| Merge failures | ${#FAILED_MERGE[@]} |"
report_line "| Failed CI runs | ${#FAILED_CI[@]} |"
report_line ""
report_line "---"
report_line "*Generated by skill-github-daily-ops · Jarvis ⚡*"

echo ""
cat "$REPORT"
