#!/bin/bash
# Test script for xai-image-gen skill

set -e

echo "🧪 Testing xai-image-gen skill..."
echo

# Check for API key
if [ -z "$XAI_API_KEY" ]; then
    echo "❌ Error: XAI_API_KEY not set"
    echo "   Export your API key: export XAI_API_KEY='xai-...'"
    exit 1
fi

# Check for Python and requests
if ! python3 -c "import requests" 2>/dev/null; then
    echo "❌ Error: requests library not found"
    echo "   Install with: pip3 install requests"
    exit 1
fi

echo "✅ API key found"
echo "✅ Dependencies installed"
echo

# Test 1: Basic generation
echo "Test 1: Basic generation"
./xai-gen "test image of a blue cube" --filename test1.png --verbose
if [ -f test1.png ]; then
    echo "✅ Test 1 passed"
    rm test1.png
else
    echo "❌ Test 1 failed"
    exit 1
fi
echo

# Test 2: Multiple images
echo "Test 2: Multiple images (n=2)"
./xai-gen "red circle" --filename test2.png --n 2 --verbose
if [ -f test2_1.png ] && [ -f test2_2.png ]; then
    echo "✅ Test 2 passed"
    rm test2_*.png
else
    echo "❌ Test 2 failed"
    exit 1
fi
echo

# Test 3: Base64 format
echo "Test 3: Base64 format"
./xai-gen "green square" --filename test3.png --format b64
if [ -f test3.png ]; then
    echo "✅ Test 3 passed"
    rm test3.png
else
    echo "❌ Test 3 failed"
    exit 1
fi
echo

echo "🎉 All tests passed!"
echo
echo "Skill is ready for ClawHub publication."
