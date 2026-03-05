#!/usr/bin/env bash
# memory-bench submit — Create a PR with benchmark data to the research fork.
#
# Usage: submit.sh <report.json> [--contributor GITHUB_USER]
#
# Prerequisites: gh CLI authenticated, git configured.

set -euo pipefail

FORK_REPO="globalcaos/clawdbot-moltbot-openclaw"
BENCH_DIR="benchmarks/memory-bench"

REPORT="$1"
CONTRIBUTOR="${2:-}"

if [ -z "$REPORT" ] || [ ! -f "$REPORT" ]; then
    echo "❌ Usage: submit.sh <report.json> [github-username]"
    exit 1
fi

# Validate JSON
if ! python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$REPORT" 2>/dev/null; then
    echo "❌ Invalid JSON file: $REPORT"
    exit 1
fi

# Extract contributor from report if not provided
if [ -z "$CONTRIBUTOR" ]; then
    CONTRIBUTOR=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['contributor'])" "$REPORT" 2>/dev/null || echo "anonymous")
fi

# Validate contributor username
if [[ ! "$CONTRIBUTOR" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    echo "❌ Invalid GitHub username: $CONTRIBUTOR"
    exit 1
fi

INSTANCE_ID=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['instance_id'])" "$REPORT" 2>/dev/null || echo "unknown")
TIMESTAMP=$(date -u +%Y%m%d-%H%M%S)
BRANCH="bench/${CONTRIBUTOR}-${TIMESTAMP}"
FILENAME="${CONTRIBUTOR}-${INSTANCE_ID}-${TIMESTAMP}.json"

echo "📊 Memory Bench Submission"
echo "   Contributor: $CONTRIBUTOR"
echo "   Instance:    $INSTANCE_ID"
echo "   Branch:      $BRANCH"
echo ""

# Verify gh auth
if ! gh auth status &>/dev/null; then
    echo "❌ GitHub CLI not authenticated. Run: gh auth login"
    exit 1
fi

# Fork if needed (idempotent)
echo "🔄 Ensuring fork exists..."
gh repo fork "$FORK_REPO" --clone=false 2>/dev/null || true

# Create a temp workdir to avoid touching the user's repo
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

echo "📥 Cloning (shallow)..."
gh repo clone "$CONTRIBUTOR/$( echo $FORK_REPO | cut -d/ -f2 )" "$TMPDIR/repo" -- --depth=1 -q 2>/dev/null || \
    gh repo clone "$FORK_REPO" "$TMPDIR/repo" -- --depth=1 -q

cd "$TMPDIR/repo"

# Set upstream
git remote add upstream "https://github.com/$FORK_REPO.git" 2>/dev/null || true
git fetch upstream main --depth=1 -q

# Branch from upstream/main
git checkout -b "$BRANCH" upstream/main

# Place report
mkdir -p "$BENCH_DIR/reports"
cp "$REPORT" "$BENCH_DIR/reports/$FILENAME"

# Update aggregate index
python3 -c "
import json, glob, os

reports_dir = '$BENCH_DIR/reports'
reports = []
for f in sorted(glob.glob(os.path.join(reports_dir, '*.json'))):
    try:
        r = json.load(open(f))
        reports.append({
            'file': os.path.basename(f),
            'contributor': r.get('contributor', 'anonymous'),
            'instance_id': r.get('instance_id', ''),
            'collected_at': r.get('collected_at', ''),
            'memories': r.get('memory_stats', {}).get('memories', {}).get('total_active', 0),
            'period_days': r.get('collection_period_days', 0),
            'retrieval_available': r.get('retrieval_stats', {}).get('available', False),
        })
    except Exception:
        pass

index = {
    'updated_at': '$(date -u +%Y-%m-%dT%H:%M:%SZ)',
    'total_reports': len(reports),
    'unique_instances': len(set(r['instance_id'] for r in reports)),
    'unique_contributors': len(set(r['contributor'] for r in reports)),
    'reports': reports,
}
with open('$BENCH_DIR/INDEX.json', 'w') as f:
    json.dump(index, f, indent=2)
print(f'✅ Index updated: {len(reports)} reports, {index[\"unique_instances\"]} instances')
"

# Commit
git add "$BENCH_DIR/"
git commit -m "bench: add memory-bench report from $CONTRIBUTOR ($INSTANCE_ID)

Automated submission via memory-bench skill.
Collection period: $(python3 -c "import json; print(json.load(open('$REPORT'))['collection_period_days'])" 2>/dev/null || echo '?') days
Active memories: $(python3 -c "import json; print(json.load(open('$REPORT'))['memory_stats']['memories']['total_active'])" 2>/dev/null || echo '?')
"

# Push to contributor's fork
echo "📤 Pushing to your fork..."
git push origin "$BRANCH" -q

# Create PR
echo "📝 Creating pull request..."
PR_URL=$(gh pr create \
    --repo "$FORK_REPO" \
    --head "$CONTRIBUTOR:$BRANCH" \
    --title "bench: memory-bench report from $CONTRIBUTOR" \
    --body "## Memory Bench Report

**Contributor:** @$CONTRIBUTOR
**Instance ID:** \`$INSTANCE_ID\`
**Collection period:** $(python3 -c "import json; print(json.load(open('$REPORT'))['collection_period_days'])" 2>/dev/null || echo '?') days

### Summary
$(python3 -c "
import json
r = json.load(open('$REPORT'))
m = r['memory_stats']['memories']
ret = r['retrieval_stats']
print(f\"- **Active memories:** {m['total_active']}\")
print(f\"- **Deleted memories:** {m['total_deleted']}\")
print(f\"- **Embedding coverage:** {m['embedding_coverage']*100:.1f}%\")
print(f\"- **Type distribution:** {m['type_distribution']}\")
print(f\"- **Association count:** {r['memory_stats']['associations']['total']}\")
if ret.get('available'):
    print(f\"- **Retrieval queries logged:** {ret['total_queries']}\")
    for strat, data in ret.get('by_strategy', {}).items():
        print(f\"  - {strat}: avg_score={data.get('avg_score','N/A')}, avg_latency={data.get('avg_latency_ms','N/A')}ms\")
else:
    print('- **Retrieval stats:** Not available (retrieval_log table not found)')
print(f\"- **Consolidation runs:** {r['memory_stats']['consolidation']['total_runs_in_period']}\")
" 2>/dev/null || echo '(see report JSON for details)')

### Co-authorship

This data contributes to the research papers at:
- [ENGRAM (Context Compaction)](https://github.com/globalcaos/clawdbot-moltbot-openclaw/blob/main/docs/papers/context-compaction.md)
- [CORTEX (Agent Memory)](https://github.com/globalcaos/clawdbot-moltbot-openclaw/blob/main/docs/papers/agent-memory.md)

By submitting benchmark data, you are eligible for co-authorship per [#13991](https://github.com/openclaw/openclaw/issues/13991).

---
*Automated submission via \`memory-bench\` skill.*" \
    2>&1)

echo ""
echo "✅ PR created: $PR_URL"
echo ""
echo "Thank you for contributing to the research! 🧠"
