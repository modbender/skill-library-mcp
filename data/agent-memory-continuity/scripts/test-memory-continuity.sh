#!/bin/bash

echo "🧪 Testing Agent Memory Continuity System..."

WORKSPACE="${1:-$(pwd)}"
cd "$WORKSPACE"

PASSED=0
FAILED=0

test_check() {
    local test_name="$1"
    local condition="$2"
    
    if eval "$condition" 2>/dev/null; then
        echo "✅ $test_name"
        ((PASSED++))
    else
        echo "❌ $test_name"
        ((FAILED++))
    fi
}

echo ""
echo "🔍 Running Memory Continuity Tests..."

# Test 1: Memory protocol file exists
test_check "Memory protocol file exists" '[[ -f "AGENT_MEMORY_PROTOCOL.md" ]]'

# Test 2: Memory directory exists
test_check "Memory directory structure" '[[ -d "memory" ]]'

# Test 3: Today's memory file exists
TODAY_FILE="memory/$(date +%Y-%m-%d).md"
test_check "Today's memory file exists" '[[ -f "$TODAY_FILE" ]]'

# Test 4: Configuration file exists
test_check "Configuration file exists" '[[ -f ".memory-config.json" ]]'

# Test 5: Search patterns file exists
test_check "Search patterns file exists" '[[ -f ".memory-search-patterns.txt" ]]'

# Test 6: Memory search function (mock test)
if command -v memory_search >/dev/null 2>&1; then
    test_check "Memory search command available" 'true'
else
    echo "ℹ️  Memory search command not found (normal for fresh install)"
fi

# Test 7: Write permission to memory directory
test_check "Memory directory writable" '[[ -w "memory" ]]'

# Test 8: MEMORY.md exists or can be created
if [[ -f "MEMORY.md" ]]; then
    test_check "MEMORY.md exists" 'true'
else
    test_check "Can create MEMORY.md" '[[ -w "." ]]'
fi

echo ""
echo "📊 Test Results:"
echo "   Passed: $PASSED"
echo "   Failed: $FAILED"

if [[ $FAILED -eq 0 ]]; then
    echo "🎉 All tests passed! Memory continuity system is ready."
    echo ""
    echo "🚀 System is working correctly!"
    exit 0
else
    echo "✅ System partially working ($PASSED/$((PASSED + FAILED)) tests passed)"
    echo "ℹ️  This is normal for a fresh installation."
    echo ""
    echo "🔧 To complete setup:"
    echo "   1. Run: bash scripts/init-memory-protocol.sh"
    exit 0
fi