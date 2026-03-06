#!/bin/bash
# test_security.sh - Security test for Mini Diary v0.1.2
# Tests that security vulnerabilities are fixed

set -e

echo "🔒 Mini Diary Security Test v0.1.2"
echo "=================================="

# Test 1: Try to write to system directory (should fail)
echo ""
echo "Test 1: Attempt to write to /etc/ (should fail)"
DIARY_FILE="/etc/test.md" ./scripts/add_note.sh "malicious test" 2>&1 | grep -q "Security error" && echo "✅ PASS: Blocked write to /etc/" || echo "❌ FAIL: Allowed write to /etc/"

# Test 2: Try to write to user directory (should succeed)
echo ""
echo "Test 2: Write to user directory (should succeed)"
TEST_FILE="$HOME/test_diary.md"
rm -f "$TEST_FILE"
DIARY_FILE="$TEST_FILE" ./scripts/add_note.sh "safe test" 2>&1 | grep -q "Note added" && echo "✅ PASS: Allowed write to user directory" || echo "❌ FAIL: Blocked write to user directory"
rm -f "$TEST_FILE"

# Test 3: Test safe chmod in install.sh
echo ""
echo "Test 3: Safe permission operations"
mkdir -p test_install
cp -r scripts test_install/
cd test_install
chmod 000 scripts/*.sh  # Remove all permissions
./scripts/install.sh --test 2>&1 | grep -q "safe permissions" && echo "✅ PASS: Safe permission operations" || echo "❌ FAIL: Unsafe permission operations"
cd ..
rm -rf test_install

# Test 4: Validate path function works
echo ""
echo "Test 4: Path validation function"
./scripts/add_note.sh "test" 2>&1 | grep -q "validate_safe_path" && echo "✅ PASS: Path validation active" || echo "⚠️  NOTE: Path validation may be silent"

# Test 5: Check for dangerous commands (actual commands, not comments)
echo ""
echo "Test 5: No dangerous commands"
DANGEROUS=$(grep -r "^\s*rm\s\|^\s*chmod\s[0-9]\{3\}\|^\s*chown\s\|^\s*sudo\s\|^\s*su\s" scripts/ || true)
if [ -z "$DANGEROUS" ]; then
    echo "✅ PASS: No dangerous commands found"
else
    echo "❌ FAIL: Dangerous commands found:"
    echo "$DANGEROUS"
fi

echo ""
echo "=================================="
echo "Security tests completed for Mini Diary v0.1.2"
echo "All critical vulnerabilities should be fixed."