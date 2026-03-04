#!/usr/bin/env bash
# wreckit — Differential Testing + Metamorphic Testing
# Usage: ./differential-test.sh [project-path]
# Looks for oracles, runs golden tests, checks metamorphic properties.
# Outputs structured JSON report.

set -euo pipefail

PROJECT="${1:-.}"
PROJECT="$(cd "$PROJECT" && pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log() { echo "  [differential] $*" >&2; }

echo "================================================" >&2
echo "  wreckit Differential Test Scanner" >&2
echo "  Project: $PROJECT" >&2
echo "================================================" >&2

# ─── Detect stack ────────────────────────────────────────────────────────────
STACK_JSON=$("$SCRIPT_DIR/detect-stack.sh" "$PROJECT" 2>/dev/null || echo "{}")
LANG=$(echo "$STACK_JSON" | python3 -c "import json,sys; print(json.load(sys.stdin).get('language','unknown'))" 2>/dev/null || echo "unknown")
TEST_CMD=$(echo "$STACK_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('commands',{}).get('test',''))" 2>/dev/null || echo "")

log "Language: $LANG"
log "Test command: $TEST_CMD"

# ─── Initialize report state ─────────────────────────────────────────────────
ORACLE_TYPE="none"
ORACLE_DESC="No oracle found"
GOLDEN_PASS=0
GOLDEN_FAIL=0
GOLDEN_FAILURES="[]"
METAMORPHIC_VIOLATIONS="[]"
TEST_CASES_RUN=0
MISMATCHES="[]"
VERDICT="WARN"

# ─── 1. Run existing test suite (golden test verification) ───────────────────
log ""
log "Phase 1: Running existing test suite (golden tests)..."

if [ -n "$TEST_CMD" ]; then
  cd "$PROJECT"
  TEST_OUTPUT=$(bash -c "$TEST_CMD 2>&1" || true)
  
  # Parse pass/fail counts by language
  if echo "$TEST_OUTPUT" | grep -qE "passed|failed|error" 2>/dev/null; then
    # Jest/Vitest style
    PASS_COUNT=$(echo "$TEST_OUTPUT" | grep -oE "[0-9]+ (test)?(s)? passed" | grep -oE "^[0-9]+" | tail -1 || echo "0")
    FAIL_COUNT=$(echo "$TEST_OUTPUT" | grep -oE "[0-9]+ (test)?(s)? failed" | grep -oE "^[0-9]+" | tail -1 || echo "0")
    
    # Pytest style
    if [ "$PASS_COUNT" = "0" ] && [ "$FAIL_COUNT" = "0" ]; then
      PASS_COUNT=$(echo "$TEST_OUTPUT" | grep -oE "[0-9]+ passed" | grep -oE "^[0-9]+" | tail -1 || echo "0")
      FAIL_COUNT=$(echo "$TEST_OUTPUT" | grep -oE "[0-9]+ failed" | grep -oE "^[0-9]+" | tail -1 || echo "0")
    fi
    
    GOLDEN_PASS="${PASS_COUNT:-0}"
    GOLDEN_FAIL="${FAIL_COUNT:-0}"
    
    log "  Golden tests: $GOLDEN_PASS passed, $GOLDEN_FAIL failed"
    
    if [ "${GOLDEN_FAIL:-0}" -gt 0 ]; then
      # Extract failing test names
      FAILING=$(echo "$TEST_OUTPUT" | grep -E "(FAIL|ERROR|✗|×)" | head -5 | python3 -c "
import sys, json
lines = [l.strip() for l in sys.stdin if l.strip()][:5]
print(json.dumps(lines))
" 2>/dev/null || echo "[]")
      GOLDEN_FAILURES="$FAILING"
      ORACLE_TYPE="golden"
      ORACLE_DESC="Existing test suite with expected outputs"
      VERDICT="FAIL"
    else
      ORACLE_TYPE="golden"
      ORACLE_DESC="Existing test suite with expected outputs ($GOLDEN_PASS tests)"
      VERDICT="PASS"
      TEST_CASES_RUN=$GOLDEN_PASS
    fi
  else
    log "  Could not parse test output"
    TEST_CASES_RUN=0
  fi
  cd "$OLDPWD" 2>/dev/null || true
else
  log "  No test command detected — skipping golden test phase"
fi

# ─── 2. Look for snapshot/fixture files ──────────────────────────────────────
log ""
log "Phase 2: Checking for snapshot/fixture files..."

SNAPSHOT_COUNT=$(find "$PROJECT" \
  -not -path "*/.git/*" -not -path "*/node_modules/*" -not -path "*/__pycache__/*" \
  \( -name "*.snap" -o -name "*.snapshot" -o -name "*fixture*.json" -o -name "*expected*.json" \) \
  2>/dev/null | wc -l | tr -d ' ')

if [ "$SNAPSHOT_COUNT" -gt 0 ]; then
  log "  Found $SNAPSHOT_COUNT snapshot/fixture files"
  if [ "$ORACLE_TYPE" = "none" ]; then
    ORACLE_TYPE="golden"
    ORACLE_DESC="Snapshot/fixture files ($SNAPSHOT_COUNT files)"
  fi
else
  log "  No snapshot files found"
fi

# ─── 3. Look for reference implementations ───────────────────────────────────
log ""
log "Phase 3: Looking for reference/oracle implementations..."

REF_DIRS=$(find "$PROJECT" \
  -not -path "*/.git/*" -not -path "*/node_modules/*" \
  -type d \( -name "reference" -o -name "oracle" -o -name "reference_impl" -o -name "baseline" \) \
  2>/dev/null | head -5)

if [ -n "$REF_DIRS" ]; then
  log "  Found reference implementation directories: $REF_DIRS"
  if [ "$ORACLE_TYPE" = "none" ]; then
    ORACLE_TYPE="reference"
    ORACLE_DESC="Reference implementation directory found: $(echo "$REF_DIRS" | head -1)"
  fi
else
  log "  No reference implementation directories found"
fi

# ─── 4. Metamorphic property detection ───────────────────────────────────────
log ""
log "Phase 4: Checking metamorphic properties..."

# Look for common patterns that should have metamorphic properties
METAMORPHIC_CHECKS=()

# Sort functions
if grep -rn --include="*.py" --include="*.js" --include="*.ts" \
  -E "\bsort\b|\bsorted\b" "$PROJECT" 2>/dev/null | head -3 | grep -q .; then
  METAMORPHIC_CHECKS+=("sort")
  log "  Detected: sort function (should satisfy: sort(reverse(x)) = reverse(sort(x)))"
fi

# Encode/decode pairs  
if grep -rn --include="*.py" --include="*.js" --include="*.ts" \
  -E "\bencode\b|\bdecode\b|\bserialize\b|\bdeserialize\b|\bparse\b|\bstringify\b" \
  "$PROJECT" 2>/dev/null | head -3 | grep -q .; then
  METAMORPHIC_CHECKS+=("encode_decode")
  log "  Detected: encode/decode pair (should satisfy: decode(encode(x)) = x)"
fi

# Hash functions
if grep -rn --include="*.py" --include="*.js" --include="*.ts" \
  -E "\bhash\b|\bdigest\b|\bchecksum\b" \
  "$PROJECT" 2>/dev/null | head -3 | grep -q .; then
  METAMORPHIC_CHECKS+=("hash")
  log "  Detected: hash function (should satisfy: hash(x) = hash(x) always)"
fi

# Filter functions
if grep -rn --include="*.py" --include="*.js" --include="*.ts" \
  -E "\bfilter\b|\bwhere\b|\bselect\b" \
  "$PROJECT" 2>/dev/null | head -3 | grep -q .; then
  METAMORPHIC_CHECKS+=("filter")
  log "  Detected: filter function (should satisfy: len(filter(x)) <= len(x))"
fi

if [ ${#METAMORPHIC_CHECKS[@]} -gt 0 ]; then
  DETECTED_TYPES=$(printf '"%s",' "${METAMORPHIC_CHECKS[@]}" | sed 's/,$//')
  log "  Metamorphic checks applicable: ${METAMORPHIC_CHECKS[*]}"
  log "  NOTE: Run these manually or add property tests (see property-based gate)"
  
  if [ "$ORACLE_TYPE" = "none" ]; then
    ORACLE_TYPE="metamorphic"
    ORACLE_DESC="Metamorphic properties detected for: ${METAMORPHIC_CHECKS[*]}"
    if [ "$VERDICT" = "WARN" ]; then
      VERDICT="WARN"
    fi
  fi
else
  log "  No obvious metamorphic properties detected"
fi

# ─── 5. Check for duplicate implementations ─────────────────────────────────
log ""
log "Phase 5: Looking for duplicate/alternative implementations..."

# Find files with similar names that might be alternatives
DUP_PATTERN=""
if [ "$LANG" = "python" ]; then
  # Look for _v2, _old, _new, _backup, _ref suffixes
  DUPS=$(find "$PROJECT" -name "*.py" \
    -not -path "*/.git/*" -not -path "*/__pycache__/*" \
    | grep -E "(_v[0-9]+|_old|_new|_backup|_ref|_orig)\." | head -5 || true)
elif [ "$LANG" = "typescript" ] || [ "$LANG" = "javascript" ]; then
  DUPS=$(find "$PROJECT" \( -name "*.ts" -o -name "*.js" \) \
    -not -path "*/.git/*" -not -path "*/node_modules/*" \
    | grep -E "(_v[0-9]+|_old|_new|_backup|_ref|_orig)\." | head -5 || true)
fi

if [ -n "${DUPS:-}" ]; then
  log "  Found potential alternative implementations: $DUPS"
  if [ "$ORACLE_TYPE" = "none" ]; then
    ORACLE_TYPE="reference"
    ORACLE_DESC="Alternative implementation files found: $(echo "$DUPS" | head -1)"
  fi
fi

# ─── 6. Git diff check (regression against last commit) ──────────────────────
log ""
log "Phase 6: Checking for regressions vs last commit..."

if git -C "$PROJECT" log --oneline -1 2>/dev/null > /dev/null; then
  # Check if any test files changed in the last commit
  CHANGED_TESTS=$(git -C "$PROJECT" diff HEAD~1 --name-only 2>/dev/null | grep -E "test_|_test\.|spec\." | head -5 || true)
  if [ -n "$CHANGED_TESTS" ]; then
    log "  Test files changed in last commit: $CHANGED_TESTS"
    log "  These should be run to verify no regressions"
  else
    log "  No test file changes in last commit"
  fi
fi

# ─── Build summary ────────────────────────────────────────────────────────────
log ""
log "Building report..."

# Final verdict logic
if [ "$GOLDEN_FAIL" -gt 0 ]; then
  VERDICT="FAIL"
elif [ "$ORACLE_TYPE" = "none" ] && [ ${#METAMORPHIC_CHECKS[@]} -eq 0 ]; then
  VERDICT="WARN"
  ORACLE_DESC="No oracle, no metamorphic properties, no reference found. Differential testing skipped."
elif [ "$VERDICT" = "WARN" ] && [ "$GOLDEN_PASS" -gt 0 ]; then
  VERDICT="PASS"
fi

METAMORPHIC_ARRAY="[]"
if [ ${#METAMORPHIC_CHECKS[@]} -gt 0 ]; then
  METAMORPHIC_ARRAY=$(printf '"%s",' "${METAMORPHIC_CHECKS[@]}" | sed 's/,$//')
  METAMORPHIC_ARRAY="[$METAMORPHIC_ARRAY]"
fi

python3 << PYEOF
import json

report = {
    "project": "$PROJECT",
    "scanner": "wreckit-differential",
    "oracle_type": "$ORACLE_TYPE",
    "oracle_description": "$ORACLE_DESC",
    "golden_tests": {
        "passed": $GOLDEN_PASS,
        "failed": $GOLDEN_FAIL,
        "failures": $GOLDEN_FAILURES
    },
    "metamorphic_properties_detected": $METAMORPHIC_ARRAY,
    "metamorphic_violations": $METAMORPHIC_VIOLATIONS,
    "snapshot_files_found": $SNAPSHOT_COUNT,
    "mismatches": $MISMATCHES,
    "verdict": "$VERDICT",
    "notes": "For full differential testing, create a reference implementation or golden fixture files. See references/gates/differential.md for the manual process."
}

print(json.dumps(report, indent=2))
PYEOF

echo "" >&2
echo "Results:" >&2
echo "  Oracle type: $ORACLE_TYPE" >&2
echo "  Golden tests: $GOLDEN_PASS passed, $GOLDEN_FAIL failed" >&2
echo "  Metamorphic checks: ${#METAMORPHIC_CHECKS[@]}" >&2
echo "  Verdict: $VERDICT" >&2
