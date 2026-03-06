#!/bin/bash
#
# test.sh - Validate Telnyx Voice skill setup
#

echo "🧪 Telnyx Voice - Tests"
echo "======================="
echo ""

PASS=0
FAIL=0

pass() {
    echo "  ✅ $1"
    ((PASS++))
}

fail() {
    echo "  ❌ $1"
    ((FAIL++))
}

# Check Node.js
echo "1. Checking Node.js..."
if command -v node &> /dev/null; then
    pass "Node.js installed"
    
    NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -ge 18 ]; then
        pass "Node.js 18+ (have v$NODE_VERSION)"
    else
        fail "Node.js 18+ required (have v$NODE_VERSION)"
    fi
else
    fail "Node.js not found"
fi

# Check npm
echo ""
echo "2. Checking npm..."
if command -v npm &> /dev/null; then
    pass "npm installed"
else
    fail "npm not found"
fi

# Check dependencies
echo ""
echo "3. Checking dependencies..."
if [ -d "node_modules" ]; then
    pass "node_modules exists"
else
    fail "node_modules missing (run: npm install)"
fi

# Check config
echo ""
echo "4. Checking configuration..."
if [ -f ".env" ]; then
    pass ".env exists"
    if grep -q "TELNYX_API_KEY=KEY" .env 2>/dev/null; then
        pass "TELNYX_API_KEY configured"
    elif grep -q "TELNYX_API_KEY=" .env 2>/dev/null; then
        echo "  ⚠️  TELNYX_API_KEY present but may need value"
    else
        fail "TELNYX_API_KEY not in .env"
    fi
elif [ -f ".env.example" ]; then
    echo "  ⚠️  .env not created (copy from .env.example)"
else
    fail "No .env or .env.example"
fi

# Check source files
echo ""
echo "5. Checking source files..."
if [ -f "src/dev.ts" ]; then
    pass "src/dev.ts exists"
else
    fail "src/dev.ts missing"
fi

if [ -f "src/tunnel.ts" ]; then
    pass "src/tunnel.ts exists"
else
    fail "src/tunnel.ts missing"
fi

# Summary
echo ""
echo "======================="
echo "Results: $PASS passed, $FAIL failed"

if [ $FAIL -gt 0 ]; then
    exit 1
fi
