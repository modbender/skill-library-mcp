#!/bin/bash
# Verify Bittensor SN85 Vibe Miner Skill Package
# Checks that all files are present and valid

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "🔍 Verifying SN85 Vibe Miner Skill Package"
echo "Location: $SKILL_DIR"
echo "=========================================="
echo

ERRORS=0

# Check core files
echo "📋 Checking core files..."
for file in "SKILL.md" "README.md" "package.json"; do
    if [ -f "$SKILL_DIR/$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ MISSING: $file"
        ((ERRORS++))
    fi
done
echo

# Check scripts
echo "📋 Checking scripts..."
for script in "install.sh" "register.sh" "monitor.sh" "storage_setup.sh" "start_miners.sh"; do
    SCRIPT_PATH="$SKILL_DIR/scripts/$script"
    if [ -f "$SCRIPT_PATH" ]; then
        if [ -x "$SCRIPT_PATH" ]; then
            echo "   ✅ $script (executable)"
        else
            echo "   ⚠️  $script (not executable, will fix)"
            chmod +x "$SCRIPT_PATH"
        fi
    else
        echo "   ❌ MISSING: $script"
        ((ERRORS++))
    fi
done
echo

# Check patches
echo "📋 Checking patches..."
PATCH_FILE="$SKILL_DIR/patches/validator_merger_vmaf.patch"
if [ -f "$PATCH_FILE" ]; then
    # Verify it's a valid patch
    if grep -q "calculate_full_video_vmaf" "$PATCH_FILE"; then
        echo "   ✅ validator_merger_vmaf.patch (valid)"
    else
        echo "   ⚠️  validator_merger_vmaf.patch (content suspicious)"
    fi
else
    echo "   ❌ MISSING: validator_merger_vmaf.patch"
    ((ERRORS++))
fi
echo

# Check docs
echo "📋 Checking documentation..."
for doc in "docs/TROUBLESHOOTING.md" "docs/SKILL_COMPLETE.md"; do
    if [ -f "$SKILL_DIR/$doc" ]; then
        echo "   ✅ $doc"
    else
        echo "   ⚠️  MISSING: $doc (optional)"
    fi
done
echo

# Validate package.json
echo "📋 Validating package.json..."
if command -v jq &> /dev/null; then
    if jq empty "$SKILL_DIR/package.json" 2>/dev/null; then
        NAME=$(jq -r .name "$SKILL_DIR/package.json")
        VERSION=$(jq -r .version "$SKILL_DIR/package.json")
        echo "   ✅ Valid JSON"
        echo "   📦 Name: $NAME"
        echo "   🏷️  Version: $VERSION"
    else
        echo "   ❌ Invalid JSON"
        ((ERRORS++))
    fi
else
    echo "   ⚠️  jq not installed, cannot validate JSON"
fi
echo

# Check shell syntax
echo "📋 Checking shell script syntax..."
SYNTAX_ERRORS=0
for script in "$SKILL_DIR"/scripts/*.sh; do
    if bash -n "$script" 2>/dev/null; then
        echo "   ✅ $(basename "$script")"
    else
        echo "   ❌ SYNTAX ERROR: $(basename "$script")"
        ((SYNTAX_ERRORS++))
    fi
done

if [ $SYNTAX_ERRORS -gt 0 ]; then
    echo "   ⚠️  $SYNTAX_ERRORS script(s) have syntax errors"
    ((ERRORS++))
fi
echo

# Summary
echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo "✅ VERIFICATION PASSED"
    echo "=========================================="
    echo
    echo "Skill package is complete and valid!"
    echo
    echo "📦 Ready for ClawHub publishing:"
    echo "   cd $SKILL_DIR"
    echo "   clawhub publish"
    echo
    exit 0
else
    echo "❌ VERIFICATION FAILED"
    echo "=========================================="
    echo
    echo "Found $ERRORS error(s). Fix before publishing."
    echo
    exit 1
fi
