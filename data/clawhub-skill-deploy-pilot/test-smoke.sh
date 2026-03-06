#!/bin/bash
# Smoke test for deploy-pilot

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/deploy-pilot.py"

echo "Testing deploy-pilot smoke tests..."
echo ""

# Test 1: Help text
echo "✓ Test 1: Help text"
python3 "$PYTHON_SCRIPT" --help > /dev/null
echo "  PASS: Help text displays correctly"
echo ""

# Test 2: Init
echo "✓ Test 2: Init"
TEST_WORKSPACE=$(mktemp -d)
HOME=$TEST_WORKSPACE python3 "$PYTHON_SCRIPT" init > /dev/null 2>&1
if [ -f "$TEST_WORKSPACE/.openclaw/workspace/deploy-pilot/stacks.json" ]; then
  echo "  PASS: Config files created"
else
  echo "  FAIL: Config files not created"
  exit 1
fi
rm -rf "$TEST_WORKSPACE"
echo ""

# Test 3: Version output
echo "✓ Test 3: Version in skill.json"
if grep -q '"version": "1.0.0"' "$SCRIPT_DIR/skill.json"; then
  echo "  PASS: skill.json has version 1.0.0"
else
  echo "  FAIL: skill.json missing version"
  exit 1
fi
echo ""

# Test 4: Verify executables
echo "✓ Test 4: Verify executables"
if [ -x "$PYTHON_SCRIPT" ]; then
  echo "  PASS: deploy-pilot.py is executable"
else
  echo "  FAIL: deploy-pilot.py is not executable"
  exit 1
fi

if [ -x "$SCRIPT_DIR/deploy-pilot.sh" ]; then
  echo "  PASS: deploy-pilot.sh is executable"
else
  echo "  FAIL: deploy-pilot.sh is not executable"
  exit 1
fi
echo ""

# Test 5: SKILL.md exists and is readable
echo "✓ Test 5: Documentation"
if [ -f "$SCRIPT_DIR/SKILL.md" ] && [ -s "$SCRIPT_DIR/SKILL.md" ]; then
  echo "  PASS: SKILL.md exists and is not empty ($(wc -l < "$SCRIPT_DIR/SKILL.md") lines)"
else
  echo "  FAIL: SKILL.md missing or empty"
  exit 1
fi
echo ""

# Test 6: skill.json is valid JSON
echo "✓ Test 6: skill.json validity"
if python3 -c "import json; json.load(open('$SCRIPT_DIR/skill.json'))" 2>/dev/null; then
  echo "  PASS: skill.json is valid JSON"
else
  echo "  FAIL: skill.json has invalid JSON"
  exit 1
fi
echo ""

echo "=================================="
echo "All smoke tests passed! ✓"
echo "=================================="
