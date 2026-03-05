#!/bin/bash

# Test script for Twitter/X Reader skill
# Demonstrates the functionality and validates the installation

echo "🐦 Testing Twitter/X Reader Skill"
echo "=================================="
echo

# Test 1: Check dependencies
echo "📋 Checking dependencies..."
missing_deps=()

if ! command -v curl >/dev/null 2>&1; then
    missing_deps+=("curl")
fi

if ! command -v jq >/dev/null 2>&1; then
    missing_deps+=("jq")
fi

if ! command -v bash >/dev/null 2>&1; then
    missing_deps+=("bash")
fi

if [ ${#missing_deps[@]} -eq 0 ]; then
    echo "✅ All dependencies found: curl, jq, bash"
else
    echo "❌ Missing dependencies: ${missing_deps[*]}"
    echo "Please install missing tools before using this skill."
    exit 1
fi

echo

# Test 2: Validate script permissions
echo "🔐 Checking script permissions..."
if [ -x "./scripts/read_tweet.sh" ] && [ -x "./scripts/read_thread.sh" ] && [ -x "./scripts/read_tweet_nitter.sh" ]; then
    echo "✅ Scripts are executable"
else
    echo "❌ Scripts are not executable"
    echo "Run: chmod +x scripts/*.sh"
    exit 1
fi

echo

# Test 3: Test invalid URL handling
echo "🔍 Testing URL validation..."
result=$(./scripts/read_tweet.sh "https://invalid-url.com" 2>&1)
if echo "$result" | grep -q "Invalid Twitter/X URL format"; then
    echo "✅ URL validation works correctly"
else
    echo "❌ URL validation failed"
    echo "Result: $result"
fi

echo

# Test 4: Test API connectivity
echo "🌐 Testing FxTwitter API connectivity..."
api_test=$(curl -s -m 5 "https://api.fxtwitter.com" || echo "FAILED")
if [ "$api_test" != "FAILED" ]; then
    echo "✅ FxTwitter API is accessible"
else
    echo "⚠️  FxTwitter API may be unreachable (check internet connection)"
fi

echo

# Test 5: Test with a known non-existent tweet
echo "🚫 Testing error handling..."
error_result=$(./scripts/read_tweet.sh "https://x.com/test/status/123456789" 2>/dev/null)
if echo "$error_result" | jq -e '.error' >/dev/null 2>&1; then
    echo "✅ Error handling works correctly"
    echo "   Sample error: $(echo "$error_result" | jq -r '.error')"
else
    echo "❌ Error handling failed"
    echo "Result: $error_result"
fi

echo

# Summary
echo "📊 Test Summary"
echo "==============="
echo "The Twitter/X Reader skill appears to be properly installed and configured."
echo
echo "💡 Usage Examples:"
echo "   ./scripts/read_tweet.sh \"https://x.com/username/status/1234567890\""
echo "   ./scripts/read_tweet_nitter.sh \"https://x.com/username/status/1234567890\""
echo
echo "🔗 Try with a real tweet URL to see full functionality!"
echo "   Example: ./scripts/read_tweet.sh \"https://x.com/twitter/status/[real_tweet_id]\""
echo

echo "🎉 Installation test complete!"