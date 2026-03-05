#!/bin/bash

# HookCatch Skill Test Script
# Tests the basic functionality of the OpenClaw skill

echo "🧪 Testing HookCatch OpenClaw Skill"
echo "=================================="
echo ""

# Check if hookcatch CLI is installed
echo "1. Checking HookCatch CLI installation..."
if ! command -v hookcatch &> /dev/null; then
    echo "❌ HookCatch CLI not found. Install with: npm install -g hookcatch"
    exit 1
fi
echo "✅ HookCatch CLI found: $(which hookcatch)"
echo ""

# Check if wrapper is installed
echo "2. Checking skill wrapper..."
if command -v hookcatch-skill &> /dev/null; then
    echo "✅ Skill wrapper found: $(which hookcatch-skill)"
else
    echo "⚠️  Skill wrapper not installed (optional)"
    echo "   Install with: npm install -g @hookcatch/openclaw-skill"
fi
echo ""

# Check authentication
echo "3. Checking authentication..."
if [ -z "$HOOKCATCH_API_KEY" ] && [ -z "$HOOKCATCH_TOKEN" ]; then
    echo "❌ No API key found in environment"
    echo "   Set HOOKCATCH_API_KEY or run: hookcatch login"
    exit 1
fi
echo "✅ API key found in environment"
echo ""

# Test bin list command
echo "4. Testing bin list command..."
if hookcatch bin list --format json > /dev/null 2>&1; then
    echo "✅ Bin list command works"
else
    echo "❌ Bin list command failed"
    exit 1
fi
echo ""

# Test token status
echo "5. Testing token status..."
if hookcatch token status > /dev/null 2>&1; then
    echo "✅ Token status command works"
else
    echo "⚠️  Token status command failed (may not have token)"
fi
echo ""

echo "=================================="
echo "✅ All tests passed! Skill is ready."
echo ""
echo "Try these commands:"
echo "  hookcatch bin create --name 'Test'"
echo "  hookcatch bin list"
echo "  hookcatch tunnel 3000"
