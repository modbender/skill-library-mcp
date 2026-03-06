#!/usr/bin/env bash
# Quick smoke test for arc-shield

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARC_SHIELD="${SCRIPT_DIR}/../scripts/arc-shield.sh"
OUTPUT_GUARD="${SCRIPT_DIR}/../scripts/output-guard.py"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "=== ARC-SHIELD QUICK TEST ==="
echo

# Test 1: Detect GitHub PAT
echo -n "Test 1: GitHub PAT detection... "
if echo "My token: ghp_1234567890abcdefghijklmnopqrstuvwx" | "$ARC_SHIELD" --report 2>&1 | grep -i "critical" > /dev/null; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
    echo "Output:"
    echo "My token: ghp_1234567890abcdefghijklmnopqrstuvwx" | "$ARC_SHIELD" --report 2>&1
    exit 1
fi

# Test 2: Detect 1Password token
echo -n "Test 2: 1Password token detection... "
if echo "ops_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9_abc123xyz" | "$ARC_SHIELD" --report 2>&1 | grep -i "critical" > /dev/null; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
    exit 1
fi

# Test 3: Detect password assignment
echo -n "Test 3: Password detection... "
if echo "password: mysecret123" | "$ARC_SHIELD" --report 2>&1 | grep -i "critical" > /dev/null; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
    exit 1
fi

# Test 4: Ignore normal text
echo -n "Test 4: Normal text (no false positive)... "
result=$(echo "This is just normal conversation" | "$ARC_SHIELD" --report 2>&1)
if echo "$result" | grep -E "CRITICAL: [1-9]" > /dev/null; then
    echo -e "${RED}FAIL (false positive)${NC}"
    echo "$result"
    exit 1
else
    echo -e "${GREEN}PASS${NC}"
fi

# Test 5: Redaction works
echo -n "Test 5: Redaction... "
redacted=$(echo "Token: ghp_abc123def456ghi789jkl012mno345pqr" | "$ARC_SHIELD" --redact)
if echo "$redacted" | grep -q "\[REDACTED:GITHUB_PAT\]"; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
    echo "Got: $redacted"
    exit 1
fi

# Test 6: Strict mode blocks
echo -n "Test 6: Strict mode blocks secrets... "
if echo "Secret: ghp_abc123def456ghi789jkl012mno345pqr" | "$ARC_SHIELD" --strict > /dev/null 2>&1; then
    echo -e "${RED}FAIL (should have blocked)${NC}"
    exit 1
else
    echo -e "${GREEN}PASS${NC}"
fi

# Test 7: Strict mode allows safe messages
echo -n "Test 7: Strict mode allows safe messages... "
if echo "This is a safe message" | "$ARC_SHIELD" --strict > /dev/null 2>&1; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL (blocked safe message)${NC}"
    exit 1
fi

# Test 8: Python version works
echo -n "Test 8: Python entropy detection... "
if echo "Token: kJ8nM2pQ5rT9vWxY3zA6bC4dE7fG1hI0jK2lM4nO6p" | python3 "$OUTPUT_GUARD" --report 2>&1 | grep -iE "high|critical" > /dev/null; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
    exit 1
fi

# Test 9: AWS key detection
echo -n "Test 9: AWS key detection... "
if echo "AWS_KEY=AKIAIOSFODNN7EXAMPLE" | "$ARC_SHIELD" --report 2>&1 | grep -i "critical" > /dev/null; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
    exit 1
fi

# Test 10: Secret path detection
echo -n "Test 10: Secret path detection... "
if echo "Check ~/.secrets/password.txt" | "$ARC_SHIELD" --report 2>&1 | grep -i "warn" > /dev/null; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
    exit 1
fi

echo
echo -e "${GREEN}All tests passed!${NC}"
echo
echo "Run full test suite with: ./run-tests.sh"
