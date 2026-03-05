#!/usr/bin/env bash
# wreckit — Dynamic Analysis Scanner
# Usage: ./dynamic-analysis.sh [project-path]
# Runs memory leak checks, race detectors, and sanitizers per language.
# Outputs structured JSON report.

set -euo pipefail

PROJECT="${1:-.}"
PROJECT="$(cd "$PROJECT" && pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log() { echo "  [dynamic-analysis] $*" >&2; }

echo "================================================" >&2
echo "  wreckit Dynamic Analysis Scanner" >&2
echo "  Project: $PROJECT" >&2
echo "================================================" >&2

# ─── Detect stack ─────────────────────────────────────────────────────────────
STACK_JSON=$("$SCRIPT_DIR/detect-stack.sh" "$PROJECT" 2>/dev/null || echo "{}")
LANG=$(echo "$STACK_JSON" | python3 -c "import json,sys; print(json.load(sys.stdin).get('language','unknown'))" 2>/dev/null || echo "unknown")
TEST_CMD=$(echo "$STACK_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('commands',{}).get('test',''))" 2>/dev/null || echo "")

log "Language: $LANG"
log "Test command: $TEST_CMD"

# ─── State ─────────────────────────────────────────────────────────────────────
TOOLS_AVAILABLE="[]"
FINDINGS="[]"
RACE_DETECTED=false
LEAK_DETECTED=false
BLOCKER_COUNT=0
WARNING_COUNT=0
VERDICT="WARN"
NOTES=""

add_finding() {
  local severity="$1" category="$2" description="$3" evidence="$4"
  case "$severity" in
    blocker) BLOCKER_COUNT=$((BLOCKER_COUNT+1)) ;;
    warning) WARNING_COUNT=$((WARNING_COUNT+1)) ;;
  esac
  NEW_FINDING=$(python3 -c "
import json
print(json.dumps({
    'severity': '$severity',
    'category': '$category',
    'description': '$3',
    'evidence': '$4'[:200]
}))
" 2>/dev/null || echo "{}")
  FINDINGS=$(python3 -c "
import json,sys
findings = json.loads('$FINDINGS') if '$FINDINGS' != '[]' else []
findings.append(json.loads('''$NEW_FINDING'''))
print(json.dumps(findings))
" 2>/dev/null || echo "$FINDINGS")
}

# ─── Phase 1: Language-specific dynamic analysis ──────────────────────────────
log ""
log "Phase 1: Running language-specific dynamic analysis..."

case "$LANG" in

  go)
    log "  Running: go test -race"
    cd "$PROJECT"
    
    # Check if go is available
    if command -v go >/dev/null 2>&1; then
      TOOLS_AVAILABLE='["go-race", "go-pprof"]'
      
      # Race detector
      RACE_OUTPUT=$(go test -race ./... 2>&1 || true)
      if echo "$RACE_OUTPUT" | grep -q "DATA RACE\|WARNING: DATA RACE"; then
        RACE_DETECTED=true
        BLOCKER_COUNT=$((BLOCKER_COUNT+1))
        RACE_EVIDENCE=$(echo "$RACE_OUTPUT" | grep -A3 "DATA RACE" | head -5 | tr '\n' '|')
        log "  ❌ RACE CONDITION DETECTED: $RACE_EVIDENCE"
        FINDINGS=$(python3 -c "
import json
print(json.dumps([{
    'severity': 'blocker',
    'category': 'race_condition',
    'description': 'Data race detected by go -race',
    'evidence': '''${RACE_EVIDENCE:0:200}'''
}]))
")
      else
        log "  ✅ No race conditions detected"
      fi
      
      # Memory profile (if tests pass)
      MEM_OUTPUT=$(go test -memprofile=/tmp/wreckit-mem.out ./... 2>&1 | tail -3 || true)
      log "  Memory profile: $MEM_OUTPUT"
      rm -f /tmp/wreckit-mem.out
    else
      log "  go not found — skipping"
      NOTES="go not installed"
    fi
    cd "$OLDPWD" 2>/dev/null || true
    ;;

  python)
    log "  Running: Python memory + async leak checks"
    cd "$PROJECT"
    
    TOOLS_FOUND="[]"
    
    # Check what's available
    if python3 -c "import tracemalloc" 2>/dev/null; then
      TOOLS_FOUND='["tracemalloc"]'
      log "  tracemalloc: available (built-in)"
    fi
    
    if python3 -c "import memory_profiler" 2>/dev/null; then
      TOOLS_FOUND='["tracemalloc","memory_profiler"]'
      log "  memory_profiler: available"
    fi
    
    if python3 -c "import objgraph" 2>/dev/null; then
      log "  objgraph: available"
    fi
    
    TOOLS_AVAILABLE="$TOOLS_FOUND"
    
    # Run tests with tracemalloc
    if [ -n "$TEST_CMD" ]; then
      log "  Running test suite with memory tracking..."
      
      PYTHON_MEM_SCRIPT=$(cat << 'PYEOF'
import tracemalloc
import subprocess
import sys

tracemalloc.start()
snapshot1 = tracemalloc.take_snapshot()

# Run tests
result = subprocess.run(sys.argv[1:], capture_output=True, text=True)
print(result.stdout[-2000:] if result.stdout else "")
if result.stderr:
    print(result.stderr[-1000:], file=sys.stderr)

snapshot2 = tracemalloc.take_snapshot()
stats = snapshot2.compare_to(snapshot1, 'lineno')

total_added = sum(s.size_diff for s in stats if s.size_diff > 0)
total_mb = total_added / 1024 / 1024

print(f"\n[wreckit-tracemalloc] Net memory added: {total_mb:.2f} MB", file=sys.stderr)

if total_mb > 10:
    print(f"[wreckit-tracemalloc] WARNING: >10MB memory growth", file=sys.stderr)
    top5 = "\n".join(str(s) for s in stats[:5])
    print(f"[wreckit-tracemalloc] Top allocations:\n{top5}", file=sys.stderr)
    sys.exit(2)  # Signal high memory growth
PYEOF
)
      MEM_OUTPUT=$(python3 -c "$PYTHON_MEM_SCRIPT" $TEST_CMD 2>&1 | tail -10 || true)
      
      if echo "$MEM_OUTPUT" | grep -q "WARNING: >10MB"; then
        WARNING_COUNT=$((WARNING_COUNT+1))
        log "  ⚠️ Memory growth >10MB detected"
        FINDINGS=$(python3 -c "
import json
print(json.dumps([{
    'severity': 'warning',
    'category': 'memory_leak',
    'description': 'Test suite causes >10MB memory growth',
    'evidence': '${MEM_OUTPUT//\'/}'[:200]
}]))
")
      else
        MEM_MB=$(echo "$MEM_OUTPUT" | grep "Net memory" | grep -oE "[0-9]+\.[0-9]+" || echo "unknown")
        log "  ✅ Memory growth: ${MEM_MB}MB (acceptable)"
      fi
    fi
    
    # Check for common async leak patterns
    log "  Scanning for async leak patterns..."
    ASYNC_LEAKS=$(grep -rn --include="*.py" \
      -E "asyncio\.create_task\|loop\.call_soon\|threading\.Thread" \
      "$PROJECT" 2>/dev/null | grep -v "test_\|#" | head -5 || true)
    
    if [ -n "$ASYNC_LEAKS" ]; then
      log "  Note: Async task creation found — verify cleanup on exit"
    fi
    
    cd "$OLDPWD" 2>/dev/null || true
    ;;

  typescript|javascript)
    log "  Running: Node.js heap + async leak checks"
    cd "$PROJECT"
    
    # Check available tools
    TOOLS_FOUND="[]"
    
    if [ -f "node_modules/.bin/clinic" ] || command -v clinic >/dev/null 2>&1; then
      TOOLS_FOUND='["clinic"]'
      log "  clinic.js: available"
    fi
    
    if [ -f "node_modules/leakage/package.json" ]; then
      TOOLS_FOUND='["leakage"]'
      log "  leakage: available"
    fi
    
    TOOLS_AVAILABLE="$TOOLS_FOUND"
    
    # Check for common Node.js leak patterns in source
    log "  Scanning for common memory leak patterns..."
    
    # Event listener leaks
    LISTENER_LEAKS=$(grep -rn --include="*.ts" --include="*.js" \
      -E "\.on\([\"']|addEventListener\(" \
      "$PROJECT" 2>/dev/null \
      --exclude-dir=node_modules --exclude-dir=dist | head -10 || true)
    
    LISTENER_COUNT=$(echo "$LISTENER_LEAKS" | grep -c "." || echo "0")
    LISTENER_REMOVE=$(grep -rn --include="*.ts" --include="*.js" \
      -E "\.off\([\"']|removeEventListener\(|removeAllListeners\(" \
      "$PROJECT" 2>/dev/null \
      --exclude-dir=node_modules --exclude-dir=dist | wc -l | tr -d ' ' || echo "0")
    
    if [ "$LISTENER_COUNT" -gt 0 ] && [ "$LISTENER_REMOVE" -eq 0 ]; then
      WARNING_COUNT=$((WARNING_COUNT+1))
      log "  ⚠️ $LISTENER_COUNT event listeners added, 0 removed — possible leak"
      FINDINGS=$(python3 -c "
import json
print(json.dumps([{
    'severity': 'warning',
    'category': 'async_leak',
    'description': '$LISTENER_COUNT event listeners added but none removed',
    'evidence': 'No .off() or removeEventListener() calls found'
}]))
")
    else
      log "  ✅ Event listener cleanup looks ok ($LISTENER_COUNT adds, $LISTENER_REMOVE removes)"
    fi
    
    # Check for setInterval without clearInterval
    INTERVALS=$(grep -rn --include="*.ts" --include="*.js" \
      -E "setInterval\(" \
      "$PROJECT" 2>/dev/null --exclude-dir=node_modules | wc -l | tr -d ' ' || echo "0")
    CLEAR_INTERVALS=$(grep -rn --include="*.ts" --include="*.js" \
      -E "clearInterval\(" \
      "$PROJECT" 2>/dev/null --exclude-dir=node_modules | wc -l | tr -d ' ' || echo "0")
    
    if [ "$INTERVALS" -gt 0 ] && [ "$CLEAR_INTERVALS" -eq 0 ]; then
      WARNING_COUNT=$((WARNING_COUNT+1))
      log "  ⚠️ $INTERVALS setInterval calls with 0 clearInterval — possible timer leak"
    fi
    
    cd "$OLDPWD" 2>/dev/null || true
    ;;

  rust)
    log "  Running: cargo test + Miri check"
    cd "$PROJECT"
    TOOLS_AVAILABLE='["cargo-test"]'
    
    if command -v cargo >/dev/null 2>&1; then
      # Regular tests first
      TEST_OUT=$(cargo test 2>&1 | tail -5 || true)
      log "  Test output: $TEST_OUT"
      
      # Check if Miri is available
      if cargo miri --version >/dev/null 2>&1; then
        TOOLS_AVAILABLE='["cargo-test", "miri"]'
        log "  Running Miri (undefined behavior detector)..."
        MIRI_OUT=$(cargo miri test 2>&1 | tail -10 || true)
        
        if echo "$MIRI_OUT" | grep -q "Undefined Behavior\|error\[E"; then
          BLOCKER_COUNT=$((BLOCKER_COUNT+1))
          log "  ❌ Miri found undefined behavior"
          FINDINGS=$(python3 -c "
import json
print(json.dumps([{
    'severity': 'blocker',
    'category': 'undefined_behavior',
    'description': 'Miri detected undefined behavior',
    'evidence': '''${MIRI_OUT:0:300}'''
}]))
")
        else
          log "  ✅ Miri: no undefined behavior detected"
        fi
      else
        log "  Miri not installed (optional: rustup component add miri)"
      fi
    fi
    cd "$OLDPWD" 2>/dev/null || true
    ;;

  *)
    log "  No specific dynamic analysis for language: $LANG"
    NOTES="No dynamic analysis tooling for $LANG. See references/gates/dynamic-analysis.md for manual steps."
    ;;
esac

# ─── Phase 2: Static file descriptor leak scan ─────────────────────────────────
log ""
log "Phase 2: Static file handle leak scan..."

# Look for opened files/streams without close() in the same scope
cd "$PROJECT"

# Python: open() without close() or context manager
PY_OPEN_NO_CLOSE=$(grep -rn --include="*.py" \
  -E "^\s*\w+\s*=\s*open\s*\(" \
  . 2>/dev/null | grep -v '.git/' | grep -v 'test_' || true)
PY_WITH_OPEN=$(grep -rn --include="*.py" \
  -E "with open\s*\(" \
  . 2>/dev/null | grep -v '.git/' | wc -l | tr -d ' ' || echo "0")
PY_RAW_OPEN=$(echo "$PY_OPEN_NO_CLOSE" | grep -c '.' 2>/dev/null || true)
PY_RAW_OPEN="${PY_RAW_OPEN:-0}"

if [ "$PY_RAW_OPEN" -gt 0 ] && [ "$PY_RAW_OPEN" -gt "$PY_WITH_OPEN" ]; then
  WARNING_COUNT=$((WARNING_COUNT+1))
  log "  ⚠️ $PY_RAW_OPEN raw open() calls found (prefer 'with open()' context manager)"
else
  log "  ✅ File handle patterns look safe ($PY_RAW_OPEN raw opens, $PY_WITH_OPEN context managers)"
fi

# JS/TS: fs.open/createReadStream without .close() or .destroy()
JS_OPEN=$(grep -rn --include="*.ts" --include="*.js" \
  -E "fs\.(open|createReadStream|createWriteStream)\s*\(" \
  . 2>/dev/null --exclude-dir=node_modules --exclude-dir=dist | wc -l | tr -d ' ' || echo "0")
JS_CLOSE=$(grep -rn --include="*.ts" --include="*.js" \
  -E "\.(close|destroy)\s*\(\s*\)" \
  . 2>/dev/null --exclude-dir=node_modules --exclude-dir=dist | wc -l | tr -d ' ' || echo "0")

if [ "$JS_OPEN" -gt 0 ] && [ "$JS_CLOSE" -eq 0 ]; then
  WARNING_COUNT=$((WARNING_COUNT+1))
  log "  ⚠️ $JS_OPEN fs.open/stream calls with 0 .close()/.destroy() calls"
else
  log "  ✅ Stream/FD cleanup looks ok ($JS_OPEN opens, $JS_CLOSE closes)"
fi

cd "$OLDPWD" 2>/dev/null || true

# ─── Determine verdict ─────────────────────────────────────────────────────────
if [ "$BLOCKER_COUNT" -gt 0 ]; then
  VERDICT="FAIL"
elif [ "$WARNING_COUNT" -gt 0 ]; then
  VERDICT="WARN"
elif [ "$LANG" = "unknown" ]; then
  VERDICT="WARN"
else
  VERDICT="PASS"
fi

# ─── Output report ─────────────────────────────────────────────────────────────
log ""
log "Building report..."

python3 << PYEOF
import json

race_detected = "$RACE_DETECTED" == "true"
leak_detected = "$LEAK_DETECTED" == "true"

tools = $TOOLS_AVAILABLE if '$TOOLS_AVAILABLE' != '' else []
findings = $FINDINGS if '$FINDINGS' != '' else []

report = {
    "project": "$PROJECT",
    "scanner": "wreckit-dynamic-analysis",
    "language": "$LANG",
    "tools_used": tools,
    "findings": findings,
    "summary": {
        "blockers": $BLOCKER_COUNT,
        "warnings": $WARNING_COUNT,
        "race_detected": race_detected,
        "leak_detected": leak_detected
    },
    "verdict": "$VERDICT",
    "notes": "${NOTES:-}"
}

print(json.dumps(report, indent=2))
PYEOF

echo "" >&2
echo "Results:" >&2
echo "  Blockers: $BLOCKER_COUNT, Warnings: $WARNING_COUNT" >&2
echo "  Race detected: $RACE_DETECTED" >&2
echo "  Verdict: $VERDICT" >&2
