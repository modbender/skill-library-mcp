#!/bin/bash
# pre-create-check.sh — Run BEFORE creating any new Python file in a project
# Lists existing modules and functions so agents can import instead of rewrite.
# Usage: bash pre-create-check.sh [project_directory]

set -euo pipefail

PROJECT_DIR="${1:-.}"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Directory not found: $PROJECT_DIR"
    exit 1
fi

echo "╔══════════════════════════════════════════════════╗"
echo "║          PRE-CREATION CHECK                      ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# 1. List existing Python modules
echo "📦 Existing Python modules:"
echo "─────────────────────────────"
find "$PROJECT_DIR" -maxdepth 2 -name "*.py" -not -path "*/__pycache__/*" -not -path "*/.git/*" | sort | while read -r f; do
    funcs=$(grep -c "^def " "$f" 2>/dev/null || true)
    funcs=${funcs:-0}
    funcs=$(echo "$funcs" | tr -d '[:space:]')
    echo "  $(basename "$f") ($funcs functions)"
done
echo ""

# 2. List validation/scoring/analysis functions
echo "🔍 Validation / Scoring / Analysis functions:"
echo "─────────────────────────────────────────────"
FOUND_VALIDATION=$(grep -rn "^def \(validate\|score\|analyze\|check\|verify\|assess\|evaluate\|fetch\|generate_report\)" "$PROJECT_DIR"/*.py 2>/dev/null || true)
if [ -n "$FOUND_VALIDATION" ]; then
    echo "$FOUND_VALIDATION" | sed 's|^.*/||' | while IFS=: read -r file line func; do
        echo "  $file:$line → $func"
    done
else
    echo "  (none found)"
fi
echo ""

# 3. List ALL public functions for import reference
echo "📋 All public functions available for import:"
echo "─────────────────────────────────────────────"
FOUND_PUBLIC=$(grep -rn "^def [a-z]" "$PROJECT_DIR"/*.py 2>/dev/null || true)
if [ -n "$FOUND_PUBLIC" ]; then
    echo "$FOUND_PUBLIC" | sed 's|^.*/||' | while IFS=: read -r file line func; do
        func_name=$(echo "$func" | sed 's/def \([a-zA-Z_]*\).*/\1/')
        echo "  from $(basename "$file" .py) import $func_name  # $file:$line"
    done
else
    echo "  (none found)"
fi
echo ""

# 4. Show SKILL.md / STATUS.md if present
for doc in SKILL.md STATUS.md; do
    if [ -f "$PROJECT_DIR/$doc" ]; then
        echo "📖 $doc summary:"
        echo "─────────────────────"
        head -40 "$PROJECT_DIR/$doc"
        echo ""
        echo "  ... (read full $doc for details)"
        echo ""
    fi
done

# 5. Show __init__.py registry if it exists
if [ -f "$PROJECT_DIR/__init__.py" ]; then
    echo "📦 Official module registry (__init__.py):"
    echo "─────────────────────────────────────────"
    cat "$PROJECT_DIR/__init__.py"
    echo ""
fi

echo "╔══════════════════════════════════════════════════╗"
echo "║  ⚠️  IMPORT existing modules, don't rewrite!     ║"
echo "║  Check above list. If it exists, USE it.         ║"
echo "╚══════════════════════════════════════════════════╝"
