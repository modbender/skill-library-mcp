#!/usr/bin/env bash
# wreckit — Property-Based Testing Scanner
# Usage: ./property-test.sh [project-path]
# Detects and runs property-based tests, generates stubs if none found.
# Outputs structured JSON report.

set -euo pipefail

PROJECT="${1:-.}"
PROJECT="$(cd "$PROJECT" && pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log() { echo "  [property-test] $*" >&2; }

echo "================================================" >&2
echo "  wreckit Property-Based Test Scanner" >&2
echo "  Project: $PROJECT" >&2
echo "================================================" >&2

# ─── Detect stack ─────────────────────────────────────────────────────────────
STACK_JSON=$("$SCRIPT_DIR/detect-stack.sh" "$PROJECT" 2>/dev/null || echo "{}")
LANG=$(echo "$STACK_JSON" | python3 -c "import json,sys; print(json.load(sys.stdin).get('language','unknown'))" 2>/dev/null || echo "unknown")
TEST_CMD=$(echo "$STACK_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('commands',{}).get('test',''))" 2>/dev/null || echo "")

log "Language: $LANG"

# ─── State ────────────────────────────────────────────────────────────────────
FRAMEWORK="none"
PROP_TESTS_FOUND=0
PROP_TESTS_RUN=0
FAILURES="[]"
CRASH_INPUTS="[]"
STUBS_PATH=""
VERDICT="WARN"
NOTES=""

# ─── Phase 1: Detect property-based testing framework ─────────────────────────
log ""
log "Phase 1: Detecting property-based testing framework..."

case "$LANG" in
  python)
    # Check for hypothesis
    if grep -rn --include="*.py" \
      -E "from hypothesis|import hypothesis|@given|@settings" \
      "$PROJECT" 2>/dev/null | grep -q .; then
      FRAMEWORK="hypothesis"
      log "  Found: hypothesis (@given decorators)"
    elif python3 -c "import hypothesis" 2>/dev/null; then
      FRAMEWORK="hypothesis_available"
      log "  Hypothesis installed but no @given tests found"
    else
      log "  No property testing framework found (hypothesis not installed)"
    fi
    ;;
  typescript|javascript)
    # Check for fast-check
    if grep -rn --include="*.ts" --include="*.js" --include="*.tsx" --include="*.jsx" \
      -E "from 'fast-check'|require\('fast-check'\)|fc\.property|fc\.assert" \
      "$PROJECT" 2>/dev/null | grep -q .; then
      FRAMEWORK="fast-check"
      log "  Found: fast-check (fc.property)"
    elif [ -f "$PROJECT/node_modules/fast-check/package.json" ]; then
      FRAMEWORK="fast-check_available"
      log "  fast-check installed but no fc.property tests found"
    else
      log "  No property testing framework found (fast-check not installed)"
    fi
    ;;
  rust)
    # Check for proptest or quickcheck
    if grep -rn --include="*.rs" \
      -E "proptest!|#\[proptest\]|quickcheck!|#\[quickcheck\]" \
      "$PROJECT" 2>/dev/null | grep -q .; then
      FRAMEWORK="proptest"
      log "  Found: proptest/quickcheck macros"
    elif grep -r "proptest\|quickcheck" "$PROJECT/Cargo.toml" 2>/dev/null | grep -q .; then
      FRAMEWORK="proptest_available"
      log "  proptest/quickcheck in Cargo.toml but no macros found"
    else
      log "  No property testing framework detected"
    fi
    ;;
  go)
    # Check for native go fuzz (1.18+) or gopter
    if grep -rn --include="*.go" -E "func Fuzz" "$PROJECT" 2>/dev/null | grep -q .; then
      FRAMEWORK="go-fuzz-native"
      log "  Found: native Go fuzz functions"
    elif grep -rn --include="*.go" -E "gopter|gocheck" "$PROJECT" 2>/dev/null | grep -q .; then
      FRAMEWORK="gopter"
      log "  Found: gopter/gocheck"
    else
      log "  No property testing framework detected"
    fi
    ;;
  *)
    log "  Language not supported for automated property test detection: $LANG"
    ;;
esac

# ─── Phase 2: Count existing property tests ───────────────────────────────────
log ""
log "Phase 2: Counting property tests..."

case "$FRAMEWORK" in
  hypothesis)
    PROP_TESTS_FOUND=$(grep -rn --include="*.py" -E "@given" "$PROJECT" 2>/dev/null | wc -l | tr -d ' ')
    log "  Found $PROP_TESTS_FOUND @given test cases"
    ;;
  fast-check)
    PROP_TESTS_FOUND=$(grep -rn --include="*.ts" --include="*.js" -E "fc\.property|fc\.assert" "$PROJECT" 2>/dev/null | wc -l | tr -d ' ')
    log "  Found $PROP_TESTS_FOUND fc.property() calls"
    ;;
  proptest)
    PROP_TESTS_FOUND=$(grep -rn --include="*.rs" -E "proptest!\s*\{|#\[proptest\]" "$PROJECT" 2>/dev/null | wc -l | tr -d ' ')
    log "  Found $PROP_TESTS_FOUND proptest cases"
    ;;
  go-fuzz-native)
    PROP_TESTS_FOUND=$(grep -rn --include="*.go" -E "func Fuzz" "$PROJECT" 2>/dev/null | wc -l | tr -d ' ')
    log "  Found $PROP_TESTS_FOUND fuzz functions"
    ;;
  *)
    PROP_TESTS_FOUND=0
    log "  0 property tests found"
    ;;
esac

# ─── Phase 3: Run property tests if found ────────────────────────────────────
log ""
log "Phase 3: Running property tests..."

if [ "$PROP_TESTS_FOUND" -gt 0 ]; then
  cd "$PROJECT"
  PROP_TEST_OUTPUT=""
  PROP_EXIT=0
  
  case "$FRAMEWORK" in
    hypothesis)
      log "  Running: $TEST_CMD (hypothesis tests)"
      PROP_TEST_OUTPUT=$(bash -c "$TEST_CMD 2>&1" || true)
      ;;
    fast-check)
      log "  Running: $TEST_CMD (fast-check tests)"
      PROP_TEST_OUTPUT=$(bash -c "$TEST_CMD 2>&1" || true)
      ;;
    proptest)
      log "  Running: cargo test (proptest)"
      PROP_TEST_OUTPUT=$(cargo test 2>&1 || true)
      ;;
    go-fuzz-native)
      log "  Running: go test (fuzz functions — short mode, 10s)"
      PROP_TEST_OUTPUT=$(go test -fuzz=. -fuzztime=10s ./... 2>&1 || true)
      ;;
  esac
  
  # Parse failures
  FAIL_LINES=$(echo "$PROP_TEST_OUTPUT" | grep -E "(FAILED|Falsifying|counterexample|panic|Error)" | head -5 || true)
  
  if [ -n "$FAIL_LINES" ]; then
    VERDICT="FAIL"
    FAILURES=$(echo "$FAIL_LINES" | python3 -c "
import sys, json
lines = [l.strip() for l in sys.stdin if l.strip()][:5]
print(json.dumps(lines))
" 2>/dev/null || echo '["Property test failed"]')
    log "  FAILURES detected: $FAIL_LINES"
  else
    VERDICT="PASS"
    PROP_TESTS_RUN=$PROP_TESTS_FOUND
    log "  All $PROP_TESTS_FOUND property tests passed"
  fi
  
  cd "$OLDPWD" 2>/dev/null || true
else
  log "  No property tests to run"
fi

# ─── Phase 4: Generate stubs if no property tests ────────────────────────────
log ""
log "Phase 4: Generating property test stubs..."

if [ "$PROP_TESTS_FOUND" -eq 0 ] && [ "$FRAMEWORK" != "none" ]; then
  STUBS_DIR="$PROJECT/.wreckit/property-stubs"
  mkdir -p "$STUBS_DIR"
  
  case "$LANG" in
    python)
      # Find public functions
      PUBLIC_FUNCS=$(grep -rn --include="*.py" \
        -E "^def [a-z][a-zA-Z0-9_]+\s*\(" \
        "$PROJECT" 2>/dev/null | grep -v "test_\|_test\|__" | head -5 || true)
      
      STUB_FILE="$STUBS_DIR/property_stubs.py"
      cat > "$STUB_FILE" << 'PYEOF'
"""
wreckit-generated property test stubs.
Move these into your actual test suite and expand them.
"""
from hypothesis import given, settings
import hypothesis.strategies as st

# TODO: Import the functions you want to test
# from mymodule import my_function


@given(st.lists(st.integers()))
def test_sort_is_ordered(lst):
    """Sort output should always be ordered."""
    # result = sorted(lst)  # Replace with your sort function
    # assert all(result[i] <= result[i+1] for i in range(len(result)-1))
    pass


@given(st.text())
def test_encode_decode_roundtrip(s):
    """Encode then decode should return original."""
    # encoded = encode(s)
    # assert decode(encoded) == s
    pass


@given(st.lists(st.integers()), st.lists(st.integers()))
def test_merge_length(a, b):
    """Merged result length should equal sum of inputs."""
    # result = merge(a, b)
    # assert len(result) == len(a) + len(b)
    pass
PYEOF
      log "  Generated: $STUB_FILE"
      STUBS_PATH="$STUBS_DIR"
      VERDICT="WARN"
      NOTES="No property tests found. Stubs generated at $STUBS_DIR — move to test suite."
      ;;
      
    typescript|javascript)
      STUB_FILE="$STUBS_DIR/property.spec.ts"
      cat > "$STUB_FILE" << 'TSEOF'
/**
 * wreckit-generated property test stubs.
 * Move these into your actual test suite and expand them.
 * Requires: npm install fast-check
 */
import * as fc from 'fast-check';

// TODO: Import your functions
// import { myFunction } from '../src/myModule';

describe('Property tests', () => {
  it('sort output is always ordered', () => {
    fc.assert(
      fc.property(fc.array(fc.integer()), (arr) => {
        // const result = arr.slice().sort((a, b) => a - b);
        // for (let i = 0; i < result.length - 1; i++) {
        //   if (result[i] > result[i + 1]) return false;
        // }
        return true;  // Replace with your assertion
      })
    );
  });

  it('encode/decode roundtrip', () => {
    fc.assert(
      fc.property(fc.string(), (s) => {
        // const encoded = encode(s);
        // return decode(encoded) === s;
        return true;  // Replace with your assertion
      })
    );
  });

  it('filter output is a subset of input', () => {
    fc.assert(
      fc.property(fc.array(fc.integer()), fc.func(fc.boolean()), (arr, predicate) => {
        // const result = arr.filter(predicate);
        // return result.every(item => arr.includes(item));
        return true;  // Replace with your assertion
      })
    );
  });
});
TSEOF
      log "  Generated: $STUB_FILE"
      STUBS_PATH="$STUBS_DIR"
      VERDICT="WARN"
      NOTES="No property tests found. Stubs generated at $STUBS_DIR"
      ;;
      
    rust)
      STUB_FILE="$STUBS_DIR/property_tests.rs"
      cat > "$STUB_FILE" << 'RSEOF'
// wreckit-generated property test stubs.
// Add to your test module and expand.
// Requires: cargo add proptest

#[cfg(test)]
mod property_tests {
    use proptest::prelude::*;
    // use crate::my_module::my_function;

    proptest! {
        #[test]
        fn sort_is_ordered(mut v: Vec<i32>) {
            // let sorted = my_sort(v.clone());
            // prop_assert!(sorted.windows(2).all(|w| w[0] <= w[1]));
        }

        #[test]
        fn encode_decode_roundtrip(s: String) {
            // let encoded = encode(&s);
            // prop_assert_eq!(decode(&encoded), s);
        }
    }
}
RSEOF
      log "  Generated: $STUB_FILE"
      STUBS_PATH="$STUBS_DIR"
      VERDICT="WARN"
      NOTES="No property tests found. Stubs generated at $STUBS_DIR"
      ;;
  esac
elif [ "$FRAMEWORK" = "none" ]; then
  log "  No framework available — skipping stub generation"
  VERDICT="WARN"
  NOTES="No property testing framework installed. Consider: hypothesis (Python), fast-check (JS/TS), proptest (Rust), go test -fuzz (Go)"
fi

# ─── Output report ────────────────────────────────────────────────────────────
log ""
log "Building report..."

python3 << PYEOF
import json

report = {
    "project": "$PROJECT",
    "scanner": "wreckit-property-test",
    "language": "$LANG",
    "framework_detected": "$FRAMEWORK",
    "property_tests_found": $PROP_TESTS_FOUND,
    "property_tests_run": $PROP_TESTS_RUN,
    "failures": $FAILURES,
    "crash_inputs": $CRASH_INPUTS,
    "stubs_generated": "${STUBS_PATH:-null}" if "${STUBS_PATH:-}" else None,
    "verdict": "$VERDICT",
    "notes": "${NOTES:-}"
}

print(json.dumps(report, indent=2))
PYEOF

echo "" >&2
echo "Results:" >&2
echo "  Framework: $FRAMEWORK" >&2
echo "  Property tests found: $PROP_TESTS_FOUND" >&2
echo "  Tests run: $PROP_TESTS_RUN" >&2
echo "  Verdict: $VERDICT" >&2
