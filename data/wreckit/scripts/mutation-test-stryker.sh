#!/usr/bin/env bash
# wreckit — Stryker-based mutation testing for JS/TS projects
# Usage: ./mutation-test-stryker.sh [project-path]
# Output: JSON to stdout with kill rate and verdict
# Exit 0 = results produced (check JSON verdict), Exit 1 = cannot run

set -euo pipefail
PROJECT="${1:-.}"
PROJECT="$(cd "$PROJECT" && pwd)"
cd "$PROJECT"

echo "=== Stryker Mutation Testing ===" >&2
echo "Project: $(pwd)" >&2

# ─── Prerequisites ────────────────────────────────────────────────────────────

if ! command -v npx >/dev/null 2>&1; then
  echo '{"error":"npx required but not found. Install Node.js and npm first.","tool":"stryker"}' >&2
  echo '{"error":"npx required but not found. Install Node.js and npm first.","tool":"stryker"}'
  exit 1
fi

if [ ! -f "package.json" ]; then
  echo '{"error":"No package.json found. Stryker requires a Node.js/JS/TS project.","tool":"stryker"}' >&2
  echo '{"error":"No package.json found. Stryker requires a Node.js/JS/TS project.","tool":"stryker"}'
  exit 1
fi

# ─── Check Stryker installed ──────────────────────────────────────────────────

STRYKER_INSTALLED=false
if [ -d "node_modules/@stryker-mutator/core" ]; then
  STRYKER_INSTALLED=true
elif npx --no-install stryker --version >/dev/null 2>&1; then
  STRYKER_INSTALLED=true
fi

if [ "$STRYKER_INSTALLED" = false ]; then
  echo "Stryker not installed in this project." >&2
  echo "To install Stryker, run one of:" >&2
  echo "  npm install --save-dev @stryker-mutator/core @stryker-mutator/jest-runner" >&2
  echo "  npm install --save-dev @stryker-mutator/core @stryker-mutator/vitest-runner" >&2
  echo "  npm install --save-dev @stryker-mutator/core @stryker-mutator/mocha-runner" >&2
  echo "" >&2
  echo "Then create stryker.config.json or stryker.config.mjs in your project root." >&2
  echo "Fallback: run scripts/mutation-test.sh for AI-based mutation testing." >&2
  cat <<EOF
{
  "error": "Stryker not installed",
  "tool": "stryker",
  "install_commands": [
    "npm install --save-dev @stryker-mutator/core @stryker-mutator/jest-runner",
    "npm install --save-dev @stryker-mutator/core @stryker-mutator/vitest-runner"
  ],
  "fallback": "Run scripts/mutation-test.sh for AI-based mutation testing",
  "verdict": "BLOCKED"
}
EOF
  exit 1
fi

# ─── Run Stryker ──────────────────────────────────────────────────────────────

echo "Running Stryker mutation testing..." >&2
STRYKER_EXIT=0
npx stryker run --reporters json 2>&1 | tee /tmp/wreckit-stryker-output-$$ >&2 || STRYKER_EXIT=$?

# ─── Find and parse mutation report ───────────────────────────────────────────

REPORT_PATH=""
for candidate in \
  "reports/mutation/mutation.json" \
  "reports/mutation.json" \
  ".stryker-tmp/reports/mutation.json"; do
  if [ -f "$candidate" ]; then
    REPORT_PATH="$candidate"
    break
  fi
done

if [ -z "$REPORT_PATH" ]; then
  echo "Stryker ran but mutation report not found." >&2
  echo "Expected at: reports/mutation/mutation.json" >&2
  echo "Fallback: run scripts/mutation-test.sh instead." >&2
  cat <<EOF
{
  "error": "Mutation report not found after stryker run",
  "tool": "stryker",
  "stryker_exit_code": $STRYKER_EXIT,
  "fallback": "Run scripts/mutation-test.sh for AI-based mutation testing",
  "verdict": "BLOCKED"
}
EOF
  rm -f "/tmp/wreckit-stryker-output-$$"
  exit 1
fi

echo "Parsing report: $REPORT_PATH" >&2

# ─── Extract metrics from JSON report ─────────────────────────────────────────
# Stryker JSON report format: { "files": {...}, "schemaVersion": "...", ... }
# Counts come from iterating mutant statuses

KILLED=0
SURVIVED=0
TIMEOUT_COUNT=0
TOTAL=0

# Parse using basic shell tools (no jq dependency)
if command -v python3 >/dev/null 2>&1; then
  METRICS=$(python3 - "$REPORT_PATH" <<'PYEOF'
import json, sys

with open(sys.argv[1]) as f:
    report = json.load(f)

killed = survived = timeout = total = 0

# Stryker report has "files" key with file entries containing "mutants"
files = report.get("files", {})
for fname, fdata in files.items():
    for mutant in fdata.get("mutants", []):
        status = mutant.get("status", "").lower()
        total += 1
        if status == "killed":
            killed += 1
        elif status == "survived":
            survived += 1
        elif status in ("timeout", "timedout"):
            timeout += 1
            killed += 1  # timeouts count as killed

print(f"{killed} {survived} {timeout} {total}")
PYEOF
  ) || METRICS="0 0 0 0"

  KILLED=$(echo "$METRICS" | awk '{print $1}')
  SURVIVED=$(echo "$METRICS" | awk '{print $2}')
  TIMEOUT_COUNT=$(echo "$METRICS" | awk '{print $3}')
  TOTAL=$(echo "$METRICS" | awk '{print $4}')

elif command -v node >/dev/null 2>&1; then
  METRICS=$(node -e "
const r = require('$(pwd)/$REPORT_PATH');
let killed=0,survived=0,timeout=0,total=0;
for(const f of Object.values(r.files||{})){
  for(const m of (f.mutants||[])){
    total++;
    const s=(m.status||'').toLowerCase();
    if(s==='killed') killed++;
    else if(s==='survived') survived++;
    else if(s==='timeout'||s==='timedout'){timeout++;killed++;}
  }
}
console.log(killed+' '+survived+' '+timeout+' '+total);
" 2>/dev/null) || METRICS="0 0 0 0"

  KILLED=$(echo "$METRICS" | awk '{print $1}')
  SURVIVED=$(echo "$METRICS" | awk '{print $2}')
  TIMEOUT_COUNT=$(echo "$METRICS" | awk '{print $3}')
  TOTAL=$(echo "$METRICS" | awk '{print $4}')
else
  # Fallback: count occurrences of status strings in raw JSON
  KILLED=$(grep -o '"status":"Killed"' "$REPORT_PATH" 2>/dev/null | wc -l | tr -d ' ' || echo 0)
  SURVIVED=$(grep -o '"status":"Survived"' "$REPORT_PATH" 2>/dev/null | wc -l | tr -d ' ' || echo 0)
  TIMEOUT_COUNT=$(grep -o '"status":"Timeout"' "$REPORT_PATH" 2>/dev/null | wc -l | tr -d ' ' || echo 0)
  KILLED=$((KILLED + TIMEOUT_COUNT))
  TOTAL=$((KILLED + SURVIVED))
fi

# ─── Compute kill rate ────────────────────────────────────────────────────────

KILL_RATE="0.0"
if [ "$TOTAL" -gt 0 ] && command -v bc >/dev/null 2>&1; then
  KILL_RATE=$(echo "scale=1; $KILLED * 100 / $TOTAL" | bc 2>/dev/null || echo "0.0")
elif [ "$TOTAL" -gt 0 ] && command -v python3 >/dev/null 2>&1; then
  KILL_RATE=$(python3 -c "print(round($KILLED*100/$TOTAL,1))" 2>/dev/null || echo "0.0")
fi

# ─── Determine verdict ────────────────────────────────────────────────────────

VERDICT="BLOCKED"
KILL_INT=$(echo "$KILL_RATE" | cut -d. -f1)

if [ "$KILL_INT" -ge 95 ] 2>/dev/null; then
  VERDICT="SHIP"
elif [ "$KILL_INT" -ge 90 ] 2>/dev/null; then
  VERDICT="CAUTION"
else
  VERDICT="BLOCKED"
fi

# ─── Output ───────────────────────────────────────────────────────────────────

echo "" >&2
echo "Total mutations: $TOTAL" >&2
echo "Killed: $KILLED  |  Survived: $SURVIVED  |  Timeout: $TIMEOUT_COUNT" >&2
echo "Kill rate: ${KILL_RATE}%" >&2
echo "Verdict: $VERDICT" >&2

if [ "$VERDICT" = "BLOCKED" ]; then
  echo "" >&2
  echo "Kill rate below 90%. Tests are not catching enough mutations." >&2
  echo "Consider: adding edge-case tests, boundary value tests, error-path tests." >&2
fi

cat <<EOF
{
  "tool": "stryker",
  "kill_rate": $KILL_RATE,
  "killed": $KILLED,
  "survived": $SURVIVED,
  "timeout": $TIMEOUT_COUNT,
  "total": $TOTAL,
  "report_path": "$REPORT_PATH",
  "verdict": "$VERDICT"
}
EOF

rm -f "/tmp/wreckit-stryker-output-$$"
