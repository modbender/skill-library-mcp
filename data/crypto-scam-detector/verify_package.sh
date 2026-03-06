#!/bin/bash
# Verify package is ready for ClawHub publication

echo "🔍 Crypto Scam Detector v2.0 - Package Verification"
echo "========================================================"
echo ""

SKILL_DIR="$HOME/.openclaw/workspace/skills/crypto-scam-detector"
cd "$SKILL_DIR" || exit 1

echo "📁 Package location: $SKILL_DIR"
echo ""

# Count files by type
echo "📊 File Statistics:"
echo "-------------------"
PY_FILES=$(ls -1 *.py 2>/dev/null | wc -l)
SH_FILES=$(ls -1 *.sh 2>/dev/null | wc -l)
MD_FILES=$(ls -1 *.md 2>/dev/null | wc -l)
JSON_FILES=$(ls -1 *.json 2>/dev/null | wc -l)
TXT_FILES=$(ls -1 *.txt 2>/dev/null | wc -l)
TOTAL_FILES=$((PY_FILES + SH_FILES + MD_FILES + JSON_FILES + TXT_FILES + 1))

echo "  Python modules: $PY_FILES"
echo "  Shell scripts: $SH_FILES"
echo "  Documentation: $MD_FILES"
echo "  Config files: $JSON_FILES"
echo "  Requirements: $TXT_FILES"
echo "  License: 1"
echo "  ---"
echo "  Total files: $TOTAL_FILES"
echo ""

# Check essential files
echo "✅ Essential Files Check:"
echo "-------------------------"

check_file() {
    if [ -f "$1" ]; then
        SIZE=$(ls -lh "$1" | awk '{print $5}')
        echo "  ✅ $1 ($SIZE)"
    else
        echo "  ❌ MISSING: $1"
        return 1
    fi
}

# Core files
check_file "SKILL.md"
check_file "README.md"
check_file "CHANGELOG.md"
check_file "database.py"
check_file "crypto_check_db.py"
check_file "sync_worker.py"
check_file "install.sh"
check_file "requirements.txt"
check_file "clawhub-manifest.json"

echo ""

# Check for unwanted files
echo "🗑️  Legacy File Check (should be removed):"
echo "-------------------------------------------"

check_removed() {
    if [ -f "$1" ]; then
        echo "  ⚠️  FOUND (should remove): $1"
        return 1
    else
        echo "  ✅ Removed: $1"
    fi
}

check_removed "crypto_analyzer.py"
check_removed "crypto_check.py"
check_removed "mcp_server.py"
check_removed "start.sh"
check_removed "quick_start.sh"

echo ""

# Test Python syntax
echo "🐍 Python Syntax Check:"
echo "-----------------------"

for pyfile in *.py; do
    if python3 -m py_compile "$pyfile" 2>/dev/null; then
        echo "  ✅ $pyfile"
    else
        echo "  ❌ Syntax error: $pyfile"
    fi
done

echo ""

# Test shell scripts
echo "🔧 Shell Script Check:"
echo "----------------------"

for shfile in *.sh; do
    if bash -n "$shfile" 2>/dev/null; then
        echo "  ✅ $shfile"
    else
        echo "  ❌ Syntax error: $shfile"
    fi
done

echo ""

# Check JSON validity
echo "📋 JSON Validation:"
echo "-------------------"

for jsonfile in *.json; do
    if python3 -m json.tool "$jsonfile" > /dev/null 2>&1; then
        echo "  ✅ $jsonfile"
    else
        echo "  ❌ Invalid JSON: $jsonfile"
    fi
done

echo ""

# Test database initialization
echo "💾 Database Test:"
echo "-----------------"

if [ -d "venv" ]; then
    source venv/bin/activate
    if python3 -c "from database import CryptoDatabase; db = CryptoDatabase(); print('✅ Database module works')" 2>/dev/null; then
        echo "  ✅ Database initialization works"
    else
        echo "  ⚠️  Database test failed (may need dependencies)"
    fi
    deactivate
else
    echo "  ⚠️  Virtual environment not found (run install.sh)"
fi

echo ""

# Final summary
echo "========================================================"
echo "📦 Package Summary:"
echo "========================================================"
echo ""
echo "  Version: 2.0.0"
echo "  Total Files: $TOTAL_FILES"
echo "  Package Size: $(du -sh . | awk '{print $1}')"
echo ""
echo "🚀 Ready to Publish:"
echo "--------------------"
echo ""
echo "  cd ~/.openclaw/workspace/skills/crypto-scam-detector"
echo "  clawhub publish ."
echo ""
echo "  Or:"
echo "  cd ~/.openclaw/workspace"
echo "  clawhub sync"
echo ""
echo "========================================================"
