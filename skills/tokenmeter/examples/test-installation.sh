#!/bin/bash
# test-installation.sh - Verify tokenmeter is installed correctly

set -e

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "🧪 Testing tokenmeter installation..."
echo ""
echo "Skill directory: $SKILL_DIR"
echo ""

# The actual tokenmeter repo is symlinked/cloned here
# Check if it's a symlink to the main install
TOKENMETER_DIR="$HOME/clawd/tokenmeter"

if [ -d "$TOKENMETER_DIR/.venv" ]; then
    cd "$TOKENMETER_DIR"
    echo "✅ Using main tokenmeter installation: $TOKENMETER_DIR"
elif [ -d "$SKILL_DIR/.venv" ]; then
    cd "$SKILL_DIR"
    echo "✅ Using skill-local installation: $SKILL_DIR"
else
    echo "❌ Virtual environment not found. Run:"
    echo "   cd $TOKENMETER_DIR"
    echo "   python3 -m venv .venv"
    echo "   source .venv/bin/activate"
    echo "   pip install -e ."
    exit 1
fi

# Activate venv
source .venv/bin/activate

# Check if tokenmeter is installed
if ! command -v tokenmeter &> /dev/null; then
    echo "❌ tokenmeter command not found. Run:"
    echo "   pip install -e ."
    exit 1
fi

# Check version
echo "✅ tokenmeter found:"
tokenmeter version
echo ""

# Check database
DB_PATH="$HOME/.tokenmeter/usage.db"
if [ -f "$DB_PATH" ]; then
    RECORD_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM usage;")
    echo "✅ Database found: $DB_PATH"
    echo "   Records: $RECORD_COUNT"
else
    echo "⚠️  Database not found (will be created on first use)"
fi
echo ""

# Show models
echo "✅ Supported models:"
tokenmeter models | head -10
echo ""

# Show empty dashboard
echo "✅ Dashboard:"
tokenmeter dashboard
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Installation test passed!"
echo ""
echo "Next steps:"
echo "  1. Read SKILL.md for usage guide"
echo "  2. Run: tokenmeter import --auto"
echo "  3. Check: tokenmeter dashboard"
