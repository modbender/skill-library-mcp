#!/usr/bin/env bash
# validate-trigger.sh — Check skill.yml trigger phrases against test-triggers.json
#
# Usage:
#   bash scripts/validate-trigger.sh skills/{skill-name}/
#   bash scripts/validate-trigger.sh /path/to/skill/
#
# Checks:
#   - skill.yml exists and has at least 3 trigger phrases
#   - tests/test-triggers.json exists
#   - Counts positive (shouldTrigger) and negative (shouldNotTrigger) test cases
#   - Checks for minimum coverage (≥3 positives, ≥3 negatives)
#   - Reports summary
#
# Exit codes:
#   0 — all checks passed
#   1 — one or more checks failed
set -euo pipefail

SKILL_DIR="${1:-}"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
pass() { echo "  ✓ $*"; }
fail() { echo "  ✗ $*"; ERRORS=$((ERRORS + 1)); }
warn() { echo "  ⚠ $*"; }
info() { echo "  · $*"; }

ERRORS=0

# ---------------------------------------------------------------------------
# 1. Validate argument
# ---------------------------------------------------------------------------
if [[ -z "$SKILL_DIR" ]]; then
    echo "Usage: bash scripts/validate-trigger.sh skills/{skill-name}/"
    exit 1
fi

if [[ ! -d "$SKILL_DIR" ]]; then
    echo "ERROR: Skill directory not found: $SKILL_DIR"
    exit 1
fi

SKILL_YML="$SKILL_DIR/skill.yml"
TRIGGERS_JSON="$SKILL_DIR/tests/test-triggers.json"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Trigger Validation: $(basename "$SKILL_DIR")"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ---------------------------------------------------------------------------
# 2. Check skill.yml exists
# ---------------------------------------------------------------------------
echo "── skill.yml checks ──────────────────────"
if [[ ! -f "$SKILL_YML" ]]; then
    fail "skill.yml not found: $SKILL_YML"
    echo ""
    echo "RESULT: FAIL ($ERRORS error(s))"
    exit 1
fi
pass "skill.yml found"

# ---------------------------------------------------------------------------
# 3. Extract trigger phrases from skill.yml
# ---------------------------------------------------------------------------
# Triggers are YAML list items under the 'triggers:' key, e.g.:
#   triggers:
#     - phrase one
#     - phrase two
TRIGGERS=()
in_triggers=false
while IFS= read -r line; do
    if echo "$line" | grep -qE "^triggers:"; then
        in_triggers=true
        continue
    fi
    if $in_triggers; then
        # List item line: "  - some phrase"
        if echo "$line" | grep -qE "^[[:space:]]+-[[:space:]]+"; then
            phrase=$(echo "$line" | sed 's/^[[:space:]]*-[[:space:]]*//' | tr -d '"'"'" | sed 's/[[:space:]]*$//')
            TRIGGERS+=("$phrase")
        elif echo "$line" | grep -qE "^[^[:space:]]"; then
            # New top-level key: end of triggers block
            in_triggers=false
        fi
    fi
done < "$SKILL_YML"

TRIGGER_COUNT=${#TRIGGERS[@]}
info "Trigger phrases found: $TRIGGER_COUNT"
for t in "${TRIGGERS[@]}"; do
    info "  → \"$t\""
done

if [[ $TRIGGER_COUNT -lt 3 ]]; then
    fail "Too few trigger phrases ($TRIGGER_COUNT). Minimum is 3."
else
    pass "Trigger count is sufficient ($TRIGGER_COUNT ≥ 3)"
fi

# ---------------------------------------------------------------------------
# 4. Check test-triggers.json exists
# ---------------------------------------------------------------------------
echo ""
echo "── test-triggers.json checks ─────────────"
if [[ ! -f "$TRIGGERS_JSON" ]]; then
    fail "tests/test-triggers.json not found: $TRIGGERS_JSON"
    echo ""
    echo "RESULT: FAIL ($ERRORS error(s))"
    exit 1
fi
pass "tests/test-triggers.json found"

# ---------------------------------------------------------------------------
# 5. Parse test-triggers.json using python3 (avoid jq dependency)
# ---------------------------------------------------------------------------
PARSE_RESULT=$(python3 - "$TRIGGERS_JSON" <<'PYEOF'
import sys, json
path = sys.argv[1]
with open(path) as f:
    data = json.load(f)

positives = data.get("shouldTrigger", [])
negatives = data.get("shouldNotTrigger", [])
print(f"positives={len(positives)}")
print(f"negatives={len(negatives)}")
for p in positives:
    print(f"pos:{p}")
for n in negatives:
    print(f"neg:{n}")
PYEOF
)

POSITIVE_COUNT=0
NEGATIVE_COUNT=0
POSITIVES=()
NEGATIVES=()
while IFS= read -r line; do
    if [[ "$line" == positives=* ]]; then
        POSITIVE_COUNT="${line#positives=}"
    elif [[ "$line" == negatives=* ]]; then
        NEGATIVE_COUNT="${line#negatives=}"
    elif [[ "$line" == pos:* ]]; then
        POSITIVES+=("${line#pos:}")
    elif [[ "$line" == neg:* ]]; then
        NEGATIVES+=("${line#neg:}")
    fi
done <<< "$PARSE_RESULT"

info "Positive test cases (shouldTrigger): $POSITIVE_COUNT"
info "Negative test cases (shouldNotTrigger): $NEGATIVE_COUNT"
TOTAL_CASES=$((POSITIVE_COUNT + NEGATIVE_COUNT))
info "Total test cases: $TOTAL_CASES"

if [[ $POSITIVE_COUNT -lt 3 ]]; then
    fail "Too few positive test cases ($POSITIVE_COUNT). Minimum is 3."
else
    pass "Positive test coverage sufficient ($POSITIVE_COUNT ≥ 3)"
fi

if [[ $NEGATIVE_COUNT -lt 3 ]]; then
    fail "Too few negative test cases ($NEGATIVE_COUNT). Minimum is 3."
else
    pass "Negative test coverage sufficient ($NEGATIVE_COUNT ≥ 3)"
fi

# ---------------------------------------------------------------------------
# 6. Coverage check: each trigger phrase should appear in at least one test
# ---------------------------------------------------------------------------
echo ""
echo "── Trigger coverage check ────────────────"
UNCOVERED=0
for trigger in "${TRIGGERS[@]}"; do
    trigger_lower=$(echo "$trigger" | tr '[:upper:]' '[:lower:]')
    covered=false
    for pos in "${POSITIVES[@]}"; do
        pos_lower=$(echo "$pos" | tr '[:upper:]' '[:lower:]')
        if echo "$pos_lower" | grep -qF "$trigger_lower" 2>/dev/null; then
            covered=true
            break
        fi
    done
    if ! $covered; then
        warn "Trigger phrase not covered by any positive test: \"$trigger\""
        UNCOVERED=$((UNCOVERED + 1))
    fi
done

if [[ $UNCOVERED -eq 0 ]]; then
    pass "All $TRIGGER_COUNT trigger phrases have matching positive tests"
else
    warn "$UNCOVERED trigger phrase(s) lack direct positive test coverage"
    info "(Warnings do not fail the check — exact phrase matches aren't required)"
fi

# ---------------------------------------------------------------------------
# 7. Balance check: ratio of positives to negatives
# ---------------------------------------------------------------------------
echo ""
echo "── Balance check ─────────────────────────"
if [[ $POSITIVE_COUNT -gt 0 && $NEGATIVE_COUNT -gt 0 ]]; then
    RATIO_PCT=$(python3 -c "print(round($POSITIVE_COUNT / $NEGATIVE_COUNT, 2))")
    info "Positive:Negative ratio: $POSITIVE_COUNT:$NEGATIVE_COUNT ($RATIO_PCT)"
    # Recommended: not more than 3:1 in either direction
    TOO_SKEWED=$(python3 -c "print('yes' if $POSITIVE_COUNT > 3 * $NEGATIVE_COUNT or $NEGATIVE_COUNT > 3 * $POSITIVE_COUNT else 'no')")
    if [[ "$TOO_SKEWED" == "yes" ]]; then
        warn "Test balance is skewed (>3:1 ratio). Consider adding more cases on the smaller side."
    else
        pass "Test balance is acceptable"
    fi
fi

# ---------------------------------------------------------------------------
# 8. Final summary
# ---------------------------------------------------------------------------
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Skill directory : $SKILL_DIR"
echo "  Trigger phrases : $TRIGGER_COUNT"
echo "  Positive tests  : $POSITIVE_COUNT"
echo "  Negative tests  : $NEGATIVE_COUNT"
echo "  Total tests     : $TOTAL_CASES"
echo ""

if [[ $ERRORS -eq 0 ]]; then
    echo "  RESULT: ✅ PASS"
    echo ""
    exit 0
else
    echo "  RESULT: ❌ FAIL ($ERRORS error(s))"
    echo ""
    exit 1
fi
