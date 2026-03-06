#!/usr/bin/env bash
# wreckit — automated mutation testing
# Usage: ./mutation-test.sh [project-path] [test-command]
# Generates mutations, runs tests, reports kill rate
# Exit 0 = results produced, check JSON for pass/fail

set -euo pipefail
# Capture SCRIPT_DIR before any cd (BASH_SOURCE may be relative)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="${1:-.}"
TEST_CMD="${2:-}"
PROJECT="$(cd "$PROJECT" && pwd)"
cd "$PROJECT"

verdict_from_rate() {
  local rate="$1"
  local rate_int
  rate_int=$(echo "$rate" | cut -d. -f1)
  if [ "$rate_int" -ge 95 ] 2>/dev/null; then
    echo "SHIP"
  elif [ "$rate_int" -ge 90 ] 2>/dev/null; then
    echo "CAUTION"
  else
    echo "BLOCKED"
  fi
}

# Auto-detect test command
if [ -z "$TEST_CMD" ]; then
  if [ -f "package.json" ]; then
    if grep -q '"vitest"' package.json 2>/dev/null; then TEST_CMD="npx vitest run"
    elif grep -q '"jest"' package.json 2>/dev/null; then TEST_CMD="npx jest"
    elif grep -q 'node --test' package.json 2>/dev/null; then TEST_CMD="npm test"
    fi
  elif [ -f "Cargo.toml" ]; then TEST_CMD="cargo test"
  elif [ -f "go.mod" ]; then TEST_CMD="go test ./..."
  elif [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then TEST_CMD="pytest"
  elif [ -f "tests/run_tests.sh" ]; then TEST_CMD="bash tests/run_tests.sh"
  elif [ -f "test/run_tests.sh" ]; then TEST_CMD="bash test/run_tests.sh"
  elif [ -f "run_tests.sh" ]; then TEST_CMD="bash run_tests.sh"
  elif find . -name "run_tests.sh" -not -path '*/.git/*' -maxdepth 3 2>/dev/null | head -1 | grep -q .; then
    TEST_CMD="bash $(find . -name 'run_tests.sh' -not -path '*/.git/*' -maxdepth 3 2>/dev/null | head -1)"
  fi
fi

if [ -z "$TEST_CMD" ]; then
  echo '{"error":"Could not detect test command. Pass as second argument."}'
  exit 1
fi

echo "Test command: $TEST_CMD" >&2
echo "Verifying baseline tests pass..." >&2
if ! eval "$TEST_CMD" >/dev/null 2>&1; then
  echo '{"error":"Baseline tests fail. Fix tests before mutation testing."}'
  exit 1
fi
echo "Baseline OK" >&2

# ─── Real mutation frameworks ──────────────────────────────────────────────

# JS/TS → Stryker
if ([ -f "tsconfig.json" ] || [ -f "package.json" ]) && ! [ -f "Cargo.toml" ]; then
  if npx stryker --version >/dev/null 2>&1 && [ -f "$SCRIPT_DIR/mutation-test-stryker.sh" ]; then
    echo "Using Stryker for mutation testing..." >&2
    OUTPUT=$("$SCRIPT_DIR/mutation-test-stryker.sh" "$PROJECT" 2>/dev/null || true)
    LAST_JSON=$(echo "$OUTPUT" | grep '^{' | tail -1)
    if [ -n "$LAST_JSON" ]; then
      echo "$LAST_JSON" | python3 -c "
import json,sys
d=json.load(sys.stdin)
d['tool']='stryker'
print(json.dumps(d))
" 2>/dev/null || echo "$LAST_JSON"
      exit 0
    fi
    echo "Stryker produced no JSON — falling back to AI mutations" >&2
  fi
fi

# Python → mutmut
if [ -f "pyproject.toml" ] || [ -f "requirements.txt" ] || [ -f "setup.py" ]; then
  if command -v mutmut >/dev/null 2>&1; then
    echo "Using mutmut for Python mutation testing..." >&2
    mutmut run >/dev/null 2>&1 || true
    RESULTS=$(mutmut results 2>/dev/null || true)
    # mutmut outputs "Killed: N" or "Killed N out of M" — use case-insensitive grep
    KILLED=$(echo "$RESULTS" | grep -iE "^[[:space:]]*killed" | grep -oE '[0-9]+' | head -1 || echo 0)
    SURVIVED=$(echo "$RESULTS" | grep -iE "^[[:space:]]*(survived|missed)" | grep -oE '[0-9]+' | head -1 || echo 0)
    # Fallback: count individual mutation status lines
    if [ -z "$KILLED" ] || [ "$KILLED" = "0" ]; then
      KILLED=$(echo "$RESULTS" | grep -icE "\bkilled\b" || echo 0)
      SURVIVED=$(echo "$RESULTS" | grep -icE "\b(survived|missed)\b" || echo 0)
    fi
    KILLED=${KILLED:-0}
    SURVIVED=${SURVIVED:-0}
    TOTAL=$((KILLED + SURVIVED))
    if [ "$TOTAL" -gt 0 ]; then
      KILL_RATE=$(echo "scale=1; $KILLED * 100 / $TOTAL" | bc 2>/dev/null || echo "0")
      VERDICT=$(verdict_from_rate "$KILL_RATE")
      echo "{\"total\":$TOTAL,\"killed\":$KILLED,\"survived\":$SURVIVED,\"killRate\":$KILL_RATE,\"language\":\"py\",\"tool\":\"mutmut\",\"verdict\":\"$VERDICT\"}"
      exit 0
    fi
    echo "mutmut returned no results — falling back to AI mutations" >&2
  else
    echo "mutmut not installed. Install with: pip install mutmut" >&2
    echo "Falling back to AI mutations..." >&2
  fi
fi

# Rust → cargo-mutants
if [ -f "Cargo.toml" ]; then
  if command -v cargo-mutants >/dev/null 2>&1; then
    echo "Using cargo-mutants for Rust mutation testing..." >&2
    MUTANTS_OUT=$(cargo mutants --json 2>/dev/null || true)
    if [ -n "$MUTANTS_OUT" ] && echo "$MUTANTS_OUT" | python3 -c "import json,sys; json.load(sys.stdin)" >/dev/null 2>&1; then
      echo "$MUTANTS_OUT" | python3 -c "
import json,sys
data=json.load(sys.stdin)
killed=sum(1 for m in data if m.get('outcome')=='Caught')
survived=sum(1 for m in data if m.get('outcome')=='Missed')
total=killed+survived
rate=round(killed*100/total,1) if total>0 else 0
verdict='SHIP' if rate>=95 else ('CAUTION' if rate>=90 else 'BLOCKED')
print(json.dumps({'total':total,'killed':killed,'survived':survived,'killRate':rate,'language':'rs','tool':'cargo-mutants','verdict':verdict}))
"
      exit 0
    fi
    echo "cargo-mutants returned no usable JSON — falling back to AI mutations" >&2
  else
    echo "cargo-mutants not installed. Install with: cargo install cargo-mutants" >&2
    echo "Falling back to AI mutations..." >&2
  fi
fi

# Find source files
if [ -f "tsconfig.json" ] || ([ -f "package.json" ] && ! [ -f "Cargo.toml" ]); then
  LANG="ts"
  SRC_FILES=$(find . -name '*.ts' -not -name '*.test.*' -not -name '*.spec.*' \
    -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/dist/*' \
    -not -name '*.d.ts' -not -path '*/tests/*' -not -path '*/__tests__/*' 2>/dev/null || true)
elif [ -f "Cargo.toml" ]; then
  LANG="rs"; SRC_FILES=$(find . -name '*.rs' -not -path '*/target/*' -not -path '*/.git/*' 2>/dev/null || true)
elif [ -f "go.mod" ]; then
  LANG="go"; SRC_FILES=$(find . -name '*.go' -not -name '*_test.go' -not -path '*/.git/*' 2>/dev/null || true)
elif [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then
  LANG="py"; SRC_FILES=$(find . -name '*.py' -not -name 'test_*' -not -name '*_test.py' -not -path '*/.git/*' -not -path '*/venv/*' 2>/dev/null || true)
else
  LANG="sh"; SRC_FILES=$(find . -name '*.sh' -not -path '*/.git/*' 2>/dev/null || true)
fi

FILE_COUNT=$(echo "$SRC_FILES" | grep -c '.' 2>/dev/null || echo 0)
echo "Found $FILE_COUNT source files ($LANG)" >&2

# Use temp files for counters (avoids subshell issues)
RESULTS_FILE=$(mktemp)
KILLED=0
SURVIVED=0
TOTAL=0
MAX_MUTATIONS=20

mutate_line() {
  local line="$1"
  if echo "$line" | grep -q '==='; then echo "$line" | sed 's/===/!==/'
  elif echo "$line" | grep -q '!=='; then echo "$line" | sed 's/!==/===/'
  elif echo "$line" | grep -q '>='; then echo "$line" | sed 's/>=/</'
  elif echo "$line" | grep -q '<='; then echo "$line" | sed 's/<=/>/g'
  elif echo "$line" | grep -q '&&'; then echo "$line" | sed 's/&&/||/'
  elif echo "$line" | grep -qF '||'; then echo "$line" | sed 's/||/\&\&/'
  elif echo "$line" | grep -q ' true'; then echo "$line" | sed 's/ true/ false/'
  elif echo "$line" | grep -q ' false'; then echo "$line" | sed 's/ false/ true/'
  elif echo "$line" | grep -q 'return '; then echo "$line" | sed 's/return /return undefined; \/\/ /'
  else echo "$line"
  fi
}

for file in $SRC_FILES; do
  [ "$TOTAL" -ge "$MAX_MUTATIONS" ] && break
  LINE_COUNT=$(wc -l < "$file" | tr -d ' ')
  [ "$LINE_COUNT" -lt 5 ] && continue

  CANDIDATES=$(grep -nE '(===|!==|>=|<=|&&|\|\|| true| false|return )' "$file" 2>/dev/null | head -5 || true)
  [ -z "$CANDIDATES" ] && continue

  cp "$file" "/tmp/wreckit-backup-$$"

  while IFS= read -r candidate; do
    [ "$TOTAL" -ge "$MAX_MUTATIONS" ] && break
    LINENUM=$(echo "$candidate" | cut -d: -f1)
    ORIGINAL=$(sed -n "${LINENUM}p" "$file")
    MUTATED=$(mutate_line "$ORIGINAL")
    [ "$ORIGINAL" = "$MUTATED" ] && continue

    # Apply mutation via awk
    awk -v ln="$LINENUM" -v rep="$MUTATED" 'NR==ln{print rep;next}{print}' "$file" > "/tmp/wreckit-mutated-$$"
    cp "/tmp/wreckit-mutated-$$" "$file"
    TOTAL=$((TOTAL + 1))

    if eval "$TEST_CMD" >/dev/null 2>&1; then
      SURVIVED=$((SURVIVED + 1))
      echo "  SURVIVED: ${file}:${LINENUM}" >> "$RESULTS_FILE"
    else
      KILLED=$((KILLED + 1))
      echo "  KILLED:   ${file}:${LINENUM}" >> "$RESULTS_FILE"
    fi

    cp "/tmp/wreckit-backup-$$" "$file"
  done <<< "$CANDIDATES"

  cp "/tmp/wreckit-backup-$$" "$file"
  rm -f "/tmp/wreckit-backup-$$" "/tmp/wreckit-mutated-$$"
done

if [ "$TOTAL" -eq 0 ]; then
  rm -f "$RESULTS_FILE"
  echo '{"error":"No mutatable lines found in source files."}'
  exit 1
fi

KILL_RATE=$(echo "scale=1; $KILLED * 100 / $TOTAL" | bc 2>/dev/null || echo "0")
VERDICT=$(verdict_from_rate "$KILL_RATE")

echo ""
echo "=== MUTATION TEST RESULTS ==="
cat "$RESULTS_FILE"
echo ""
echo "Total: $TOTAL | Killed: $KILLED | Survived: $SURVIVED"
echo "Kill rate: ${KILL_RATE}%"

cat <<EOF

{"total":$TOTAL,"killed":$KILLED,"survived":$SURVIVED,"killRate":$KILL_RATE,"language":"$LANG","tool":"ai-mutations","verdict":"$VERDICT"}
EOF

rm -f "$RESULTS_FILE"
