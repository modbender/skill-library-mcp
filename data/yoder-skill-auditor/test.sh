#!/bin/bash
# Skill Auditor v3.0.0 - Test Suite
# Runs the auditor against known-good and known-bad test skills
# Usage: bash test.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AUDIT="$SCRIPT_DIR/audit.sh"
TEST_DIR="$SCRIPT_DIR/tests"
PASSED=0
FAILED=0
TOTAL=0

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

assert_verdict() {
    local skill="$1" expected="$2"
    ((TOTAL++))
    
    RESULT=$(bash "$AUDIT" "$TEST_DIR/$skill" --json 2>/dev/null)
    VERDICT=$(echo "$RESULT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('verdict','error'))" 2>/dev/null)
    
    if [ "$VERDICT" = "$expected" ]; then
        echo -e "${GREEN}PASS${NC} $skill: expected=$expected got=$VERDICT"
        ((PASSED++))
    else
        echo -e "${RED}FAIL${NC} $skill: expected=$expected got=$VERDICT"
        ((FAILED++))
    fi
}

assert_has_check() {
    local skill="$1" check_name="$2" severity="$3"
    ((TOTAL++))
    
    RESULT=$(bash "$AUDIT" "$TEST_DIR/$skill" --json 2>/dev/null)
    HAS_CHECK=$(echo "$RESULT" | python3 -c "
import json,sys
data = json.load(sys.stdin)
items = data.get('items',[])
found = any(i['check'] == '$check_name' and i['severity'] == '$severity' for i in items)
print('yes' if found else 'no')
" 2>/dev/null)
    
    if [ "$HAS_CHECK" = "yes" ]; then
        echo -e "${GREEN}PASS${NC} $skill: has $severity '$check_name'"
        ((PASSED++))
    else
        echo -e "${RED}FAIL${NC} $skill: missing $severity '$check_name'"
        echo "$RESULT" | python3 -c "
import json,sys
data = json.load(sys.stdin)
for i in data.get('items',[]):
    if i['severity'] not in ('pass','info'):
        print(f\"    got: [{i['severity']}] {i['check']}: {i['message']}\")
" 2>/dev/null
        ((FAILED++))
    fi
}

assert_no_criticals() {
    local skill="$1"
    ((TOTAL++))
    
    RESULT=$(bash "$AUDIT" "$TEST_DIR/$skill" --json 2>/dev/null)
    CRITS=$(echo "$RESULT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('criticals',0))" 2>/dev/null)
    
    if [ "$CRITS" = "0" ]; then
        echo -e "${GREEN}PASS${NC} $skill: zero criticals"
        ((PASSED++))
    else
        echo -e "${RED}FAIL${NC} $skill: expected 0 criticals, got $CRITS"
        ((FAILED++))
    fi
}

echo "========================================="
echo "  Skill Auditor v3.0.0 - Test Suite"
echo "========================================="
echo ""

# ─── MALICIOUS SKILLS (should FAIL) ───
echo "--- Malicious Skills (expect FAIL) ---"

# Original tests
assert_verdict "malicious-basic" "fail"
assert_has_check "malicious-basic" "credential-harvest" "critical"
assert_has_check "malicious-basic" "exfiltration-url" "critical"

assert_verdict "malicious-obfuscated" "fail"
assert_has_check "malicious-obfuscated" "obfuscated-payload" "critical"

assert_verdict "malicious-sysread" "fail"
assert_has_check "malicious-sysread" "sensitive-fs" "critical"

# New v2.0 tests
assert_verdict "malicious-crypto" "fail"
assert_has_check "malicious-crypto" "crypto-wallet" "critical"

assert_verdict "malicious-timebomb" "fail"
assert_has_check "malicious-timebomb" "time-bomb" "warning"

assert_verdict "malicious-symlink" "fail"
assert_has_check "malicious-symlink" "symlink-attack" "critical"

assert_verdict "malicious-prompt-injection" "fail"
assert_has_check "malicious-prompt-injection" "prompt-injection" "critical"

assert_verdict "malicious-download-exec" "fail"
assert_has_check "malicious-download-exec" "download-execute" "critical"

assert_verdict "malicious-privilege-escalation" "fail"
assert_has_check "malicious-privilege-escalation" "privilege-escalation" "critical"

echo ""

# ─── CLEAN SKILLS (should PASS) ───
echo "--- Clean Skills (expect PASS) ---"

assert_verdict "clean-basic" "pass"
assert_no_criticals "clean-basic"

assert_verdict "clean-with-creds-docs" "pass"
assert_no_criticals "clean-with-creds-docs"
assert_has_check "clean-with-creds-docs" "doc-credentials" "info"

assert_verdict "clean-with-network" "pass"
assert_no_criticals "clean-with-network"

assert_verdict "clean-with-dotfiles" "pass"
assert_no_criticals "clean-with-dotfiles"

echo ""

# ─── SUMMARY ───
echo "========================================="
echo "  TEST RESULTS"
echo "========================================="
echo -e "  Total:  $TOTAL"
echo -e "  Passed: ${GREEN}$PASSED${NC}"
echo -e "  Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}ALL TESTS PASSED${NC}"
    exit 0
else
    echo -e "${RED}$FAILED TEST(S) FAILED${NC}"
    exit 1
fi
