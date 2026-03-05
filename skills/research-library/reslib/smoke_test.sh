#!/bin/bash
#
# Research Library Smoke Test
# Quick validation that the system works (<30 seconds)
#
# Usage: ./smoke_test.sh
#
# This script tests the core workflow:
#   1. Init database
#   2. Add a file
#   3. Search for content
#   4. Status check
#   5. Export document
#   6. Cleanup
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test directory
TEST_DIR=$(mktemp -d)
DATA_DIR="$TEST_DIR/data"
mkdir -p "$DATA_DIR"

# Cleanup function
cleanup() {
    rm -rf "$TEST_DIR"
}
trap cleanup EXIT

echo "╔════════════════════════════════════════════════════════════╗"
echo "║           Research Library Smoke Test                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Test directory: $TEST_DIR"
echo ""

# Track test results
TESTS_PASSED=0
TESTS_FAILED=0

pass() {
    echo -e "  ${GREEN}✓${NC} $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

fail() {
    echo -e "  ${RED}✗${NC} $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

# ============================================================================
# Test 1: Create test file
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 1: Create test file"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

TEST_FILE="$TEST_DIR/test_document.txt"
cat > "$TEST_FILE" << 'EOF'
# PID Controller Theory

A PID controller continuously calculates an error value as the difference
between a desired setpoint and a measured process variable and applies a
correction based on proportional, integral, and derivative terms.

## Proportional Term
The proportional term produces an output value that is proportional to the
current error value. Kp determines the ratio of output response to error.

## Integral Term  
The integral term is concerned with the accumulation of past errors. If the
error has been present for a long time, the integral term accumulates.

## Derivative Term
The derivative term is a best estimate of the future trend of the error,
based on its current rate of change.

Keywords: control systems, feedback loop, tuning, automation
EOF

if [ -f "$TEST_FILE" ]; then
    pass "Test file created"
else
    fail "Test file creation failed"
    exit 1
fi

# ============================================================================
# Test 2: Initialize database and add document
# ============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 2: Add document to library"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if python3 -m reslib --data-dir "$DATA_DIR" add "$TEST_FILE" \
    --project "smoke-test" \
    --material-type "reference" \
    --confidence "0.9" \
    --title "PID Controller Theory" \
    --tags "control,pid,theory" 2>/dev/null | grep -q "Saved as research"; then
    pass "Document added successfully"
else
    fail "Document add failed"
fi

# ============================================================================
# Test 3: Search for content
# ============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 3: Search for content"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

SEARCH_RESULT=$(python3 -m reslib --data-dir "$DATA_DIR" --json-output search "PID controller" 2>/dev/null)

if echo "$SEARCH_RESULT" | grep -q '"count"'; then
    COUNT=$(echo "$SEARCH_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['count'])")
    if [ "$COUNT" -gt 0 ]; then
        pass "Search returned $COUNT result(s)"
    else
        fail "Search returned no results"
    fi
else
    fail "Search command failed"
fi

# ============================================================================
# Test 4: Check status
# ============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 4: Check library status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

STATUS=$(python3 -m reslib --data-dir "$DATA_DIR" --json-output status 2>/dev/null)

if echo "$STATUS" | grep -q '"total_documents"'; then
    DOCS=$(echo "$STATUS" | python3 -c "import sys,json; print(json.load(sys.stdin)['total_documents'])")
    REFS=$(echo "$STATUS" | python3 -c "import sys,json; print(json.load(sys.stdin)['reference_count'])")
    pass "Status: $DOCS documents ($REFS references)"
else
    fail "Status command failed"
fi

# ============================================================================
# Test 5: Export document
# ============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 5: Export document"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

EXPORT_FILE="$TEST_DIR/export.json"
if python3 -m reslib --data-dir "$DATA_DIR" export 1 --format json -o "$EXPORT_FILE" 2>/dev/null; then
    if [ -f "$EXPORT_FILE" ] && grep -q "PID Controller" "$EXPORT_FILE"; then
        pass "Document exported successfully"
    else
        fail "Export file invalid"
    fi
else
    fail "Export command failed"
fi

# ============================================================================
# Test 6: Create backup
# ============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 6: Create backup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if python3 -m reslib --data-dir "$DATA_DIR" backup --name "smoke-test" 2>/dev/null | grep -q "Created backup"; then
    if [ -f "$DATA_DIR/backups/research_smoke-test.db" ]; then
        pass "Backup created successfully"
    else
        fail "Backup file not found"
    fi
else
    fail "Backup command failed"
fi

# ============================================================================
# Test 7: Verify database integrity
# ============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 7: Database integrity check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

INTEGRITY=$(python3 -c "
import sqlite3
conn = sqlite3.connect('$DATA_DIR/research.db')
result = conn.execute('PRAGMA integrity_check;').fetchone()[0]
print(result)
conn.close()
" 2>/dev/null)

if [ "$INTEGRITY" = "ok" ]; then
    pass "Database integrity OK"
else
    fail "Database integrity check failed"
fi

# ============================================================================
# Summary
# ============================================================================
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    Test Summary                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

if [ "$TESTS_FAILED" -eq 0 ]; then
    echo -e "${GREEN}All $TESTS_PASSED tests passed!${NC}"
    echo ""
    echo "✅ SMOKE TEST PASSED"
    echo ""
    exit 0
else
    echo -e "${RED}$TESTS_FAILED test(s) failed${NC}, ${GREEN}$TESTS_PASSED passed${NC}"
    echo ""
    echo "❌ SMOKE TEST FAILED"
    echo ""
    exit 1
fi
