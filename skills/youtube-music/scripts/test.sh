#!/usr/bin/env bash
# Test script for YouTube Music skill

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

echo "🎵 YouTube Music Skill - Test Suite"
echo "===================================="
echo ""

# Test 1: Check skill files exist
echo "Test 1: Checking skill files..."
files_exist=true
for file in "SKILL.md" "README.md" "scripts/youtube-music.sh" "scripts/control.js"; do
    if [[ -f "$SKILL_DIR/$file" ]]; then
        echo "  ✓ $file exists"
    else
        echo "  ✗ $file missing"
        files_exist=false
    fi
done

if [[ "$files_exist" == false ]]; then
    echo ""
    echo "❌ Some files are missing. Aborting tests."
    exit 1
fi

echo ""
echo "✓ All skill files present"
echo ""

# Test 2: Check scripts are executable
echo "Test 2: Checking script permissions..."
for script in "scripts/youtube-music.sh" "scripts/control.js"; do
    if [[ -x "$SKILL_DIR/$script" ]]; then
        echo "  ✓ $script is executable"
    else
        echo "  ⚠ $script is not executable (fixing...)"
        chmod +x "$SKILL_DIR/$script"
    fi
done

echo ""
echo "✓ Scripts are executable"
echo ""

# Test 3: Check browser availability
echo "Test 3: Checking browser..."
if command -v openclaw &> /dev/null; then
    echo "  ✓ OpenClaw CLI available"
    
    browser_status=$(openclaw browser status 2>&1)
    if echo "$browser_status" | grep -q '"running": true'; then
        echo "  ✓ Browser is running"
    else
        echo "  ⚠ Browser not running (will start on first use)"
    fi
else
    echo "  ✗ OpenClaw CLI not found"
fi

echo ""

# Test 4: Test help command
echo "Test 4: Testing help command..."
if bash "$SKILL_DIR/scripts/youtube-music.sh" help > /dev/null 2>&1; then
    echo "  ✓ Help command works"
else
    echo "  ✗ Help command failed"
fi

echo ""

# Test 5: Validate SKILL.md structure
echo "Test 5: Validating SKILL.md..."
if grep -q "name: youtube-music" "$SKILL_DIR/SKILL.md"; then
    echo "  ✓ SKILL.md has correct name"
else
    echo "  ✗ SKILL.md missing name"
fi

if grep -q "description:" "$SKILL_DIR/SKILL.md"; then
    echo "  ✓ SKILL.md has description"
else
    echo "  ✗ SKILL.md missing description"
fi

if grep -q "youtube-music" "$SKILL_DIR/SKILL.md"; then
    echo "  ✓ SKILL.md properly configured"
else
    echo "  ✗ SKILL.md configuration issue"
fi

echo ""
echo "===================================="
echo "✅ All tests completed!"
echo ""
echo "Next steps:"
echo "1. Run: ./scripts/youtube-music.sh help"
echo "2. Try: ./scripts/youtube-music.sh play \"test song\""
echo "3. Check OpenClaw browser is running"
echo ""
