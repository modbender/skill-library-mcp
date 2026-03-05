#!/bin/bash
# Self-Healing System v2.0.1 — Automated Test Suite

set -euo pipefail

echo "🧪 Self-Healing v2.0.1 Test Suite"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

PASS=0
FAIL=0

test_extract_learning() {
  echo "1. extract_learning() function test:"
  
  # Sourcing the function (simplified)
  TEST_DIR="/tmp/self-healing-test-$$"
  mkdir -p "$TEST_DIR"
  
  # Mock files
  echo "### Symptom\n- Test symptom" > "$TEST_DIR/report.md"
  echo "### Decision Making\n- Test decision" > "$TEST_DIR/reasoning.md"
  
  # Simple test: check if function exists
  if grep -q "extract_learning()" ../scripts/emergency-recovery-v2.sh; then
    echo "  ✅ Function exists"
    PASS=$((PASS + 1))
  else
    echo "  ❌ Function not found"
    FAIL=$((FAIL + 1))
  fi
  
  # Test reasoning_file usage
  if grep -A 30 "extract_learning()" ../scripts/emergency-recovery-v2.sh | grep -q "\$reasoning_file"; then
    echo "  ✅ reasoning_file parameter used"
    PASS=$((PASS + 1))
  else
    echo "  ❌ reasoning_file parameter unused"
    FAIL=$((FAIL + 1))
  fi
  
  rm -rf "$TEST_DIR"
  echo ""
}

test_dependencies() {
  echo "2. Dependency check:"
  
  for dep in tmux claude jq; do
    if command -v "$dep" &>/dev/null; then
      echo "  ✅ $dep installed"
      PASS=$((PASS + 1))
    else
      echo "  ❌ $dep missing"
      FAIL=$((FAIL + 1))
    fi
  done
  echo ""
}

test_file_structure() {
  echo "3. File structure test:"
  
  required_files=(
    "scripts/emergency-recovery-v2.sh"
    "scripts/metrics-dashboard.sh"
    "scripts/gateway-healthcheck.sh"
    ".env.example"
    "SKILL.md"
    "README.md"
    "CHANGELOG.md"
  )
  
  for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
      echo "  ✅ $file exists"
      PASS=$((PASS + 1))
    else
      echo "  ❌ $file missing"
      FAIL=$((FAIL + 1))
    fi
  done
  echo ""
}

test_version_consistency() {
  echo "4. Version consistency test:"
  
  readme_v=$(grep -m1 "version-" ../README.md | grep -oE "[0-9]+\.[0-9]+\.[0-9]+" | head -1)
  skill_v=$(grep -m1 "version:" ../SKILL.md | awk '{print $2}')
  
  if [ "$readme_v" = "2.0.1" ] && [ "$skill_v" = "2.0.1" ]; then
    echo "  ✅ Versions match (v2.0.1)"
    PASS=$((PASS + 1))
  else
    echo "  ❌ Version mismatch: README=$readme_v, SKILL=$skill_v"
    FAIL=$((FAIL + 1))
  fi
  echo ""
}

# Run tests
test_extract_learning
test_dependencies
test_file_structure
test_version_consistency

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test Results:"
echo "  ✅ PASS: $PASS"
echo "  ❌ FAIL: $FAIL"
echo "  Total: $((PASS + FAIL))"
echo ""

if [ $FAIL -eq 0 ]; then
  echo "  🎉 All tests passed!"
  exit 0
else
  echo "  ⚠️ Some tests failed"
  exit 1
fi
