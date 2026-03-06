#!/usr/bin/env bash
# safe-merge-update: Pre-flight analysis
# Outputs divergence info and conflict analysis to /tmp/safe-merge/
set -euo pipefail

REPO_DIR="${REPO_DIR:?REPO_DIR must be set to your OpenClaw repo path}"
UPSTREAM_REMOTE="${UPSTREAM_REMOTE:-upstream}"
UPSTREAM_BRANCH="${UPSTREAM_BRANCH:-main}"
OUTPUT_DIR="/tmp/safe-merge"
MANIFEST="$(cd "$(dirname "$0")/.." && pwd)/MERGE_MANIFEST.json"

mkdir -p "$OUTPUT_DIR"
cd "$REPO_DIR"

# Use current branch (or main) as our reference
LOCAL_BRANCH="${LOCAL_BRANCH:-$(git branch --show-current)}"
echo "=== Safe Merge Pre-Flight ==="
echo "Repo: $REPO_DIR"
echo "Upstream: $UPSTREAM_REMOTE/$UPSTREAM_BRANCH"
echo "Local: $LOCAL_BRANCH"
echo ""

# Step 1: Fetch upstream
echo ">>> Fetching upstream..."
git fetch "$UPSTREAM_REMOTE" 2>&1 | tail -5

# Step 2: Compute divergence
echo ""
echo ">>> Computing divergence..."
DIVERGENCE=$(git rev-list --left-right --count "$LOCAL_BRANCH...$UPSTREAM_REMOTE/$UPSTREAM_BRANCH" 2>/dev/null || echo "0 0")
AHEAD=$(echo "$DIVERGENCE" | awk '{print $1}')
BEHIND=$(echo "$DIVERGENCE" | awk '{print $2}')
echo "Ahead: $AHEAD commits"
echo "Behind: $BEHIND commits"

if [ "$BEHIND" -eq 0 ]; then
  echo ""
  echo "✅ Already up to date with upstream. Nothing to merge."
  python3 -c "
import json
report = {'status':'up-to-date','ahead':$AHEAD,'behind':0,'conflicts':[],'timestamp':'$(date -Iseconds)'}
with open('$OUTPUT_DIR/preflight-report.json','w') as f: json.dump(report,f,indent=2)
print(json.dumps(report, indent=2))
"
  exit 0
fi

# Step 3: Find merge base and divergent files
MERGE_BASE=$(git merge-base "$LOCAL_BRANCH" "$UPSTREAM_REMOTE/$UPSTREAM_BRANCH")
echo "Merge base: $MERGE_BASE"

UPSTREAM_CHANGED_FILE="$OUTPUT_DIR/upstream-changed.txt"
OUR_CHANGED_FILE="$OUTPUT_DIR/our-changed.txt"
BOTH_CHANGED_FILE="$OUTPUT_DIR/both-changed.txt"

git diff --name-only "$MERGE_BASE" "$UPSTREAM_REMOTE/$UPSTREAM_BRANCH" | sort > "$UPSTREAM_CHANGED_FILE"
git diff --name-only "$MERGE_BASE" "$LOCAL_BRANCH" | sort > "$OUR_CHANGED_FILE"
comm -12 "$UPSTREAM_CHANGED_FILE" "$OUR_CHANGED_FILE" > "$BOTH_CHANGED_FILE"

UPSTREAM_COUNT=$(wc -l < "$UPSTREAM_CHANGED_FILE")
OUR_COUNT=$(wc -l < "$OUR_CHANGED_FILE")
CONFLICT_COUNT=$(wc -l < "$BOTH_CHANGED_FILE")

echo ""
echo "Upstream changed: $UPSTREAM_COUNT files"
echo "We changed: $OUR_COUNT files"
echo "Both changed (potential conflicts): $CONFLICT_COUNT files"

if [ "$CONFLICT_COUNT" -gt 0 ]; then
  echo ""
  echo "Conflicting files:"
  cat "$BOTH_CHANGED_FILE" | head -50
fi

# Step 4: Check protected files from manifest
echo ""
echo ">>> Checking protected files..."
PROTECTED_AT_RISK_FILE="$OUTPUT_DIR/protected-at-risk.txt"
> "$PROTECTED_AT_RISK_FILE"

if [ -f "$MANIFEST" ]; then
  python3 -c "
import json
with open('$MANIFEST') as f:
    m = json.load(f)
for path in m.get('protectedFiles', {}):
    print(path)
" 2>/dev/null | while IFS= read -r pf; do
    if grep -qF "$pf" "$BOTH_CHANGED_FILE" 2>/dev/null; then
      echo "$pf" >> "$PROTECTED_AT_RISK_FILE"
      echo "  ⚠️  PROTECTED AT RISK: $pf"
    fi
  done
fi

PROTECTED_RISK_COUNT=$(wc -l < "$PROTECTED_AT_RISK_FILE")

# Step 5: Dry-run merge using a temp worktree (avoids stash issues)
echo ""
echo ">>> Dry-run merge (using temp worktree)..."
REAL_CONFLICTS_FILE="$OUTPUT_DIR/real-conflicts.txt"
> "$REAL_CONFLICTS_FILE"

WORKTREE_DIR="/tmp/safe-merge/worktree-test"
rm -rf "$WORKTREE_DIR"

# Create a detached worktree from current branch for safe testing
git worktree add --detach "$WORKTREE_DIR" "$LOCAL_BRANCH" --quiet 2>/dev/null

pushd "$WORKTREE_DIR" > /dev/null
if git merge --no-commit --no-ff "$UPSTREAM_REMOTE/$UPSTREAM_BRANCH" 2>/dev/null; then
  echo "✅ Merge would apply cleanly"
else
  git diff --name-only --diff-filter=U > "$REAL_CONFLICTS_FILE" 2>/dev/null || true
  REAL_COUNT=$(wc -l < "$REAL_CONFLICTS_FILE")
  echo "❌ $REAL_COUNT real git conflicts"
  cat "$REAL_CONFLICTS_FILE" | head -30
  git merge --abort 2>/dev/null || true
fi
popd > /dev/null

# Clean up worktree
git worktree remove "$WORKTREE_DIR" --force 2>/dev/null || rm -rf "$WORKTREE_DIR"

REAL_CONFLICT_COUNT=$(wc -l < "$REAL_CONFLICTS_FILE")

# Step 6: Write report
echo ""
echo ">>> Writing report..."
python3 << PYEOF
import json
from datetime import datetime

def read_lines(path):
    try:
        with open(path) as f:
            return [l.strip() for l in f if l.strip()]
    except:
        return []

report = {
    "status": "needs-merge",
    "ahead": $AHEAD,
    "behind": $BEHIND,
    "mergeBase": "$MERGE_BASE",
    "upstreamChangedCount": $UPSTREAM_COUNT,
    "ourChangedCount": $OUR_COUNT,
    "bothChangedCount": $CONFLICT_COUNT,
    "bothChanged": read_lines("$BOTH_CHANGED_FILE"),
    "realConflicts": read_lines("$REAL_CONFLICTS_FILE"),
    "realConflictCount": $REAL_CONFLICT_COUNT,
    "protectedAtRisk": read_lines("$PROTECTED_AT_RISK_FILE"),
    "protectedAtRiskCount": $PROTECTED_RISK_COUNT,
    "timestamp": datetime.now().isoformat(),
    "recommendation": "proceed" if $REAL_CONFLICT_COUNT <= 50 else "manual-review"
}

with open("$OUTPUT_DIR/preflight-report.json", "w") as f:
    json.dump(report, f, indent=2)
print(json.dumps(report, indent=2))
PYEOF

echo ""
echo "=== Pre-Flight Complete ==="
