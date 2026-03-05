#!/bin/bash
# Edge case and error handling tests

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLI="$SCRIPT_DIR/scripts/ontopo-cli.py"
PASS=0
FAIL=0

test_error() {
    local name="$1"
    local cmd="$2"
    local expected="$3"

    output=$(python3 "$CLI" $cmd 2>&1)
    if echo "$output" | grep -qi "$expected"; then
        echo "✓ $name"
        ((PASS++))
    else
        echo "✗ $name"
        echo "  Expected error containing: $expected"
        echo "  Got: ${output:0:150}..."
        ((FAIL++))
    fi
}

echo "=== Ontopo CLI Edge Case Tests ==="
echo ""

# Invalid inputs
test_error "invalid date format" "check 12345 invalid-date" "Invalid date"
test_error "invalid time format" "check 12345 tomorrow invalid-time" "Invalid time"
test_error "missing venue_id" "info" "required"
test_error "missing search query" "search" "required"

# Non-existent resources (may return empty or error)
test_error "non-existent venue" "info 99999999999" "not found\|error\|No"

# Invalid commands
test_error "unknown command" "foobar" "invalid choice\|unrecognized"

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
exit $FAIL
