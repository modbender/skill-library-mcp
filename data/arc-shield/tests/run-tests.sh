#!/usr/bin/env bash
# Test suite for arc-shield

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARC_SHIELD="${SCRIPT_DIR}/../scripts/arc-shield.sh"
OUTPUT_GUARD="${SCRIPT_DIR}/../scripts/output-guard.py"
TEST_SAMPLES="${SCRIPT_DIR}/test-samples.txt"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASSED=0
FAILED=0

echo "=== ARC-SHIELD TEST SUITE ==="
echo

test_detection() {
    local name=$1
    local input=$2
    local should_detect=$3
    
    # Test with arc-shield.sh
    set +e
    result=$(echo "$input" | "$ARC_SHIELD" --report 2>&1)
    exit_code=$?
    set -e
    
    detected=0
    if echo "$result" | grep -q "CRITICAL\|HIGH\|WARN"; then
        detected=1
    fi
    
    if [[ $should_detect -eq 1 && $detected -eq 1 ]]; then
        echo -e "${GREEN}✓${NC} PASS: $name (detected as expected)"
        ((PASSED++))
    elif [[ $should_detect -eq 0 && $detected -eq 0 ]]; then
        echo -e "${GREEN}✓${NC} PASS: $name (no false positive)"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} FAIL: $name"
        echo "  Expected detect=$should_detect, got detect=$detected"
        echo "  Input: $input"
        ((FAILED++))
    fi
}

# Parse test samples
echo "Testing arc-shield.sh..."
echo

while IFS= read -r line; do
    # Skip comments and empty lines
    if [[ "$line" =~ ^#.*$ ]] || [[ -z "$line" ]]; then
        continue
    fi
    
    # Parse format: [DETECT:CATEGORY] sample text
    if [[ "$line" =~ ^\[DETECT:([A-Z_]+)\]\ (.+)$ ]]; then
        category="${BASH_REMATCH[1]}"
        text="${BASH_REMATCH[2]}"
        test_detection "$category" "$text" 1
    elif [[ "$line" =~ ^\[IGNORE\]\ (.+)$ ]]; then
        text="${BASH_REMATCH[1]}"
        test_detection "IGNORE (${text:0:30}...)" "$text" 0
    fi
done < "$TEST_SAMPLES"

echo
echo "Testing output-guard.py..."
echo

# Test Python version with entropy detection
test_python() {
    local name=$1
    local input=$2
    local should_detect=$3
    
    set +e
    result=$(echo "$input" | python3 "$OUTPUT_GUARD" --report 2>&1)
    detected=0
    if echo "$result" | grep -q "CRITICAL\|HIGH\|WARN"; then
        detected=1
    fi
    set -e
    
    if [[ $should_detect -eq 1 && $detected -eq 1 ]]; then
        echo -e "${GREEN}✓${NC} PASS: $name (Python)"
        ((PASSED++))
    elif [[ $should_detect -eq 0 && $detected -eq 0 ]]; then
        echo -e "${GREEN}✓${NC} PASS: $name (Python)"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} FAIL: $name (Python)"
        ((FAILED++))
    fi
}

# Test high-entropy detection
test_python "High Entropy Detection" "Token: kJ8nM2pQ5rT9vWxY3zA6bC4dE7fG1hI0jK2lM4nO6p" 1
test_python "Normal Text" "This is just a regular sentence without any secrets" 0

# Test redaction
echo
echo "Testing redaction..."
echo

redacted=$(echo "My key is ghp_1234567890abcdefghijklmnopqrstuvwx" | "$ARC_SHIELD" --redact)
if echo "$redacted" | grep -q "\[REDACTED:GITHUB_PAT\]"; then
    echo -e "${GREEN}✓${NC} PASS: Redaction works"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} FAIL: Redaction failed"
    echo "  Output: $redacted"
    ((FAILED++))
fi

# Test strict mode
echo
echo "Testing strict mode..."
echo

set +e
echo "Safe message" | "$ARC_SHIELD" --strict > /dev/null 2>&1
exit_code=$?
set -e

if [[ $exit_code -eq 0 ]]; then
    echo -e "${GREEN}✓${NC} PASS: Strict mode allows safe messages"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} FAIL: Strict mode blocked safe message"
    ((FAILED++))
fi

set +e
echo "Leaked token: ghp_abc123def456ghi789jkl012mno345pqr" | "$ARC_SHIELD" --strict > /dev/null 2>&1
exit_code=$?
set -e

if [[ $exit_code -eq 1 ]]; then
    echo -e "${GREEN}✓${NC} PASS: Strict mode blocks critical secrets"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} FAIL: Strict mode allowed critical secret"
    ((FAILED++))
fi

# Summary
echo
echo "=== TEST SUMMARY ==="
echo -e "Passed: ${GREEN}${PASSED}${NC}"
echo -e "Failed: ${RED}${FAILED}${NC}"
echo

if [[ $FAILED -eq 0 ]]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi
