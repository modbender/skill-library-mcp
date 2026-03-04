#!/bin/bash
# Test that skill description contains appropriate trigger words

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_FILE="$SCRIPT_DIR/SKILL.md"
PASS=0
FAIL=0

test_trigger() {
    local word="$1"
    if grep -qi "$word" "$SKILL_FILE"; then
        echo "✓ Contains trigger: $word"
        ((PASS++))
    else
        echo "✗ Missing trigger: $word"
        ((FAIL++))
    fi
}

echo "=== Skill Selection Trigger Tests ==="
echo ""

# English triggers
test_trigger "restaurant"
test_trigger "reservation"
test_trigger "table"
test_trigger "booking"
test_trigger "ontopo"
test_trigger "menu"
test_trigger "availability"
test_trigger "dining"

# Hebrew triggers
test_trigger "מסעדה"
test_trigger "הזמנה"
test_trigger "שולחן"
test_trigger "תפריט"

# Required metadata
echo ""
echo "Checking metadata..."
test_trigger "python3"
test_trigger "emoji"

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
exit $FAIL
