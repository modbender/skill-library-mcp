#!/usr/bin/env bash
# wreckit — Performance Benchmark Runner
# Usage: ./perf-benchmark.sh [project-path]
# Detects and runs benchmarks, compares vs baseline, flags regressions.
# Outputs structured JSON report.

set -euo pipefail

PROJECT="${1:-.}"
PROJECT="$(cd "$PROJECT" && pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WRECKIT_DIR="$PROJECT/.wreckit"
BASELINE_FILE="$WRECKIT_DIR/perf-baseline.json"

log() { echo "  [perf-benchmark] $*" >&2; }

echo "================================================" >&2
echo "  wreckit Performance Benchmark Runner" >&2
echo "  Project: $PROJECT" >&2
echo "================================================" >&2

# ─── Detect stack ─────────────────────────────────────────────────────────────
STACK_JSON=$("$SCRIPT_DIR/detect-stack.sh" "$PROJECT" 2>/dev/null || echo "{}")
LANG=$(echo "$STACK_JSON" | python3 -c "import json,sys; print(json.load(sys.stdin).get('language','unknown'))" 2>/dev/null || echo "unknown")

log "Language: $LANG"

# ─── State ─────────────────────────────────────────────────────────────────────
FRAMEWORK="none"
BENCHMARKS="[]"
REGRESSIONS="[]"
BASELINE_CREATED=false
VERDICT="WARN"
REGRESSION_COUNT=0
BENCH_COUNT=0

mkdir -p "$WRECKIT_DIR"

# ─── Phase 1: Detect benchmark framework ──────────────────────────────────────
log ""
log "Phase 1: Detecting benchmark framework..."

case "$LANG" in
  typescript|javascript)
    # Vitest bench
    if grep -rn --include="*.ts" --include="*.js" --include="*.bench.ts" \
      -E "^\s*bench\s*\(" "$PROJECT" 2>/dev/null \
      --exclude-dir=node_modules --exclude-dir=dist | grep -q .; then
      FRAMEWORK="vitest-bench"
      log "  Found: vitest bench() calls"
    # Jest bench
    elif grep -rn --include="*.ts" --include="*.js" \
      -E "describe\.bench|it\.bench" "$PROJECT" 2>/dev/null \
      --exclude-dir=node_modules | grep -q .; then
      FRAMEWORK="jest-bench"
      log "  Found: jest bench"
    fi
    ;;
  python)
    # pytest-benchmark
    if grep -rn --include="*.py" \
      -E "def test_.*\(.*benchmark\|benchmark\.pedantic\|benchmark\.calibrate" \
      "$PROJECT" 2>/dev/null | grep -q .; then
      FRAMEWORK="pytest-benchmark"
      log "  Found: pytest-benchmark"
    # timeit-based
    elif grep -rn --include="*.py" \
      -E "import timeit|from timeit" "$PROJECT" 2>/dev/null | grep -q .; then
      FRAMEWORK="timeit"
      log "  Found: timeit usage"
    fi
    ;;
  rust)
    if grep -rn --include="*.rs" -E "#\[bench\]|test::Bencher" "$PROJECT" 2>/dev/null | grep -q .; then
      FRAMEWORK="cargo-bench"
      log "  Found: cargo bench (#[bench])"
    fi
    ;;
  go)
    if grep -rn --include="*.go" -E "func Benchmark" "$PROJECT" 2>/dev/null | grep -q .; then
      FRAMEWORK="go-bench"
      log "  Found: go test -bench"
    fi
    ;;
  *)
    log "  Unknown language: $LANG"
    ;;
esac

# Check for k6 load test
if [ -f "$PROJECT/k6.js" ] || [ -f "$PROJECT/load-test.js" ] || \
   find "$PROJECT" -name "*.k6.js" 2>/dev/null | head -1 | grep -q .; then
  FRAMEWORK="k6"
  log "  Found: k6 load test scripts"
fi

if [ "$FRAMEWORK" = "none" ]; then
  log "  No benchmark framework detected"
fi

# ─── Phase 2: Run benchmarks ──────────────────────────────────────────────────
log ""
log "Phase 2: Running benchmarks..."

cd "$PROJECT"

BENCH_OUTPUT=""
BENCH_EXIT=0

case "$FRAMEWORK" in
  vitest-bench)
    if command -v npx >/dev/null 2>&1; then
      log "  Running: npx vitest bench --reporter=json"
      BENCH_OUTPUT=$(npx vitest bench --reporter=json 2>&1 || true)
      BENCH_COUNT=$(echo "$BENCH_OUTPUT" | python3 -c "
import json,sys
try:
    d = json.load(sys.stdin)
    print(sum(len(s.get('benchmarks',[])) for s in d.get('testSuites',[])))
except:
    print(0)
" 2>/dev/null || echo "0")
      log "  Ran $BENCH_COUNT benchmarks"
    else
      log "  npx not available"
    fi
    ;;
    
  pytest-benchmark)
    if command -v pytest >/dev/null 2>&1 || command -v python3 >/dev/null 2>&1; then
      log "  Running: pytest --benchmark-only --benchmark-json=/tmp/wreckit-bench.json"
      pytest --benchmark-only --benchmark-json=/tmp/wreckit-bench.json 2>&1 || true
      
      if [ -f /tmp/wreckit-bench.json ]; then
        BENCH_OUTPUT=$(cat /tmp/wreckit-bench.json)
        BENCHMARKS=$(python3 -c "
import json,sys
d=json.load(open('/tmp/wreckit-bench.json'))
results = []
for b in d.get('benchmarks', []):
    results.append({
        'name': b['name'],
        'mean_ms': round(b['stats']['mean'] * 1000, 4),
        'min_ms': round(b['stats']['min'] * 1000, 4),
        'max_ms': round(b['stats']['max'] * 1000, 4),
        'rounds': b['stats']['rounds']
    })
print(json.dumps(results))
" 2>/dev/null || echo "[]")
        BENCH_COUNT=$(echo "$BENCHMARKS" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")
        log "  Ran $BENCH_COUNT benchmarks"
        rm -f /tmp/wreckit-bench.json
      fi
    fi
    ;;
    
  cargo-bench)
    if command -v cargo >/dev/null 2>&1; then
      log "  Running: cargo bench"
      BENCH_OUTPUT=$(cargo bench 2>&1 || true)
      
      # Parse cargo bench output: "test bench_name ... bench: NNN ns/iter (+/- N)"
      BENCHMARKS=$(echo "$BENCH_OUTPUT" | python3 -c "
import sys, re, json
output = sys.stdin.read()
pattern = r'test (\S+)\s+\.\.\. bench:\s+([\d,]+) ns/iter'
results = []
for m in re.finditer(pattern, output):
    ns = int(m.group(2).replace(',',''))
    results.append({
        'name': m.group(1),
        'mean_ms': round(ns / 1000000, 4),
        'unit': 'ns/iter'
    })
print(json.dumps(results))
" 2>/dev/null || echo "[]")
      BENCH_COUNT=$(echo "$BENCHMARKS" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))" || echo "0")
      log "  Ran $BENCH_COUNT benchmarks"
    fi
    ;;
    
  go-bench)
    if command -v go >/dev/null 2>&1; then
      log "  Running: go test -bench=. -benchmem -count=3"
      BENCH_OUTPUT=$(go test -bench=. -benchmem -count=3 ./... 2>&1 || true)
      
      # Parse go bench output: "BenchmarkName-N   NNN   NNN ns/op   NNN B/op   N allocs/op"
      BENCHMARKS=$(echo "$BENCH_OUTPUT" | python3 -c "
import sys, re, json
output = sys.stdin.read()
# Go bench: BenchmarkFoo-8   100   12345 ns/op   1234 B/op   12 allocs/op
pattern = r'(Benchmark\S+)\s+\d+\s+([\d]+)\s+ns/op(?:\s+([\d]+)\s+B/op)?'
results = {}
for m in re.finditer(pattern, output):
    name = m.group(1)
    ns = int(m.group(2))
    bop = int(m.group(3)) if m.group(3) else 0
    if name not in results:
        results[name] = []
    results[name].append(ns)

output_list = []
for name, times in results.items():
    mean_ns = sum(times) / len(times)
    output_list.append({
        'name': name,
        'mean_ms': round(mean_ns / 1000000, 4),
        'runs': len(times)
    })
print(json.dumps(output_list))
" 2>/dev/null || echo "[]")
      BENCH_COUNT=$(echo "$BENCHMARKS" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))" || echo "0")
      log "  Ran $BENCH_COUNT benchmarks"
    fi
    ;;
    
  none)
    log "  No benchmark framework — running basic timing test"
    
    # Time the test suite itself as a proxy
    if [ -n "$(echo "$STACK_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('commands',{}).get('test',''))" 2>/dev/null)" ]; then
      TEST_CMD=$(echo "$STACK_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('commands',{}).get('test',''))" 2>/dev/null)
      
      log "  Timing test suite: $TEST_CMD"
      START=$(python3 -c "import time; print(time.time())")
      bash -c "$TEST_CMD" > /dev/null 2>&1 || true
      END=$(python3 -c "import time; print(time.time())")
      DURATION=$(python3 -c "print(round($END - $START, 2))")
      
      log "  Test suite duration: ${DURATION}s"
      BENCHMARKS=$(python3 -c "
import json
print(json.dumps([{
    'name': 'full_test_suite',
    'mean_ms': float('$DURATION') * 1000,
    'note': 'Total test suite duration (no granular benchmarks available)'
}]))
")
      BENCH_COUNT=1
    fi
    ;;
esac

cd "$OLDPWD" 2>/dev/null || true

# ─── Phase 3: Compare vs baseline ─────────────────────────────────────────────
log ""
log "Phase 3: Comparing vs baseline..."

if [ -f "$BASELINE_FILE" ] && [ "$BENCH_COUNT" -gt 0 ]; then
  log "  Baseline found: $BASELINE_FILE"
  
  COMPARISON=$(python3 << PYEOF
import json

current = json.loads('$BENCHMARKS') if '$BENCHMARKS' != '[]' else []
with open('$BASELINE_FILE') as f:
    baseline_data = json.load(f)
baseline_list = baseline_data.get('benchmarks', [])
baseline_map = {b['name']: b['mean_ms'] for b in baseline_list}

regressions = []
updated = []

for bench in current:
    name = bench['name']
    current_ms = bench['mean_ms']
    
    if name in baseline_map:
        baseline_ms = baseline_map[name]
        if baseline_ms > 0:
            delta_pct = ((current_ms - baseline_ms) / baseline_ms) * 100
        else:
            delta_pct = 0
        
        regression = delta_pct > 20
        severe = delta_pct > 50
        
        bench_with_comparison = {
            **bench,
            'baseline_ms': baseline_ms,
            'delta_pct': round(delta_pct, 1),
            'regression': regression,
            'severe_regression': severe
        }
        updated.append(bench_with_comparison)
        
        if regression:
            regressions.append({
                'name': name,
                'delta_pct': round(delta_pct, 1),
                'current_ms': current_ms,
                'baseline_ms': baseline_ms,
                'severe': severe
            })
    else:
        bench['baseline_ms'] = None
        bench['delta_pct'] = None
        bench['regression'] = False
        updated.append(bench)

print(json.dumps({'benchmarks': updated, 'regressions': regressions}))
PYEOF
)
  
  BENCHMARKS=$(echo "$COMPARISON" | python3 -c "import json,sys; print(json.dumps(json.load(sys.stdin)['benchmarks']))" || echo "$BENCHMARKS")
  REGRESSIONS=$(echo "$COMPARISON" | python3 -c "import json,sys; print(json.dumps(json.load(sys.stdin)['regressions']))" || echo "[]")
  REGRESSION_COUNT=$(echo "$REGRESSIONS" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))" || echo "0")
  
  if [ "$REGRESSION_COUNT" -gt 0 ]; then
    SEVERE=$(echo "$REGRESSIONS" | python3 -c "import json,sys; d=json.load(sys.stdin); print(any(r['severe'] for r in d))" || echo "False")
    if [ "$SEVERE" = "True" ]; then
      VERDICT="FAIL"
    else
      VERDICT="WARN"
    fi
    log "  ⚠️ $REGRESSION_COUNT regressions detected"
  else
    VERDICT="PASS"
    log "  ✅ No regressions vs baseline"
  fi
else
  log "  No baseline found — creating new baseline"
  BASELINE_CREATED=true
  
  if [ "$BENCH_COUNT" -gt 0 ]; then
    python3 << PYEOF
import json
data = {
    "benchmarks": json.loads('$BENCHMARKS') if '$BENCHMARKS' != '[]' else []
}
with open('$BASELINE_FILE', 'w') as f:
    json.dump(data, f, indent=2)
print(f"Baseline written: $BASELINE_FILE")
PYEOF
    VERDICT="PASS"
    log "  Baseline saved to $BASELINE_FILE"
  else
    VERDICT="WARN"
    log "  No benchmarks to save as baseline"
  fi
fi

# ─── Output report ─────────────────────────────────────────────────────────────
log ""
log "Building report..."

python3 << PYEOF
import json

baseline_created = "$BASELINE_CREATED" == "true"
benchmarks = json.loads('$BENCHMARKS') if '$BENCHMARKS' not in ('', '[]') else []
regressions = json.loads('$REGRESSIONS') if '$REGRESSIONS' not in ('', '[]') else []

report = {
    "project": "$PROJECT",
    "scanner": "wreckit-perf-benchmark",
    "language": "$LANG",
    "framework": "$FRAMEWORK",
    "benchmarks_run": $BENCH_COUNT,
    "benchmarks": benchmarks,
    "regressions": regressions,
    "regression_count": $REGRESSION_COUNT,
    "baseline_created": baseline_created,
    "baseline_path": "$BASELINE_FILE" if $BENCH_COUNT > 0 else None,
    "verdict": "$VERDICT"
}

print(json.dumps(report, indent=2))
PYEOF

echo "" >&2
echo "Results:" >&2
echo "  Framework: $FRAMEWORK" >&2
echo "  Benchmarks: $BENCH_COUNT" >&2
echo "  Regressions: $REGRESSION_COUNT" >&2
echo "  Verdict: $VERDICT" >&2
