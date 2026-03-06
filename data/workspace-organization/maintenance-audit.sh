#!/bin/bash
# Workspace Maintenance Audit
# Detects broken symlinks, empty dirs, large files, malformed names
# Usage: ./maintenance-audit.sh [workspace_path]
# Example: ./maintenance-audit.sh ~/.openclaw/workspace

set -e

# Auto-detect workspace or use provided path
if [ -n "$1" ]; then
    WS="$1"
elif [ -n "$OPENCLAW_WORKSPACE" ]; then
    WS="$OPENCLAW_WORKSPACE"
elif [ -d "${HOME}/.openclaw/workspace" ]; then
    WS="${HOME}/.openclaw/workspace"
else
    echo "Error: Could not detect workspace. Usage: ./maintenance-audit.sh [workspace_path]"
    exit 1
fi

if [ ! -d "$WS" ]; then
    echo "Error: Workspace not found: $WS"
    exit 1
fi

echo "=== Workspace Maintenance Audit ==="
echo "Date: $(date '+%Y-%m-%d %H:%M')"
echo "Path: $WS"
echo ""

# 1. Broken symlinks
echo "1. Checking for broken symlinks..."
BROKEN=$(find "$WS" -xtype l 2>/dev/null || true)
if [ -n "$BROKEN" ]; then
    echo "⚠️  Found broken symlinks:"
    echo "$BROKEN"
else
    echo "✓ No broken symlinks"
fi
echo ""

# 2. Empty directories (excluding .git, node_modules, __pycache__)
echo "2. Checking for empty directories..."
EMPTY=$(find "$WS" -type d -empty 2>/dev/null \
    | grep -v "node_modules" \
    | grep -v "\.git" \
    | grep -v "__pycache__" \
    | grep -v "\.venv" \
    || true)
if [ -n "$EMPTY" ]; then
    echo "ℹ️  Found empty directories:"
    echo "$EMPTY"
else
    echo "✓ No empty directories"
fi
echo ""

# 3. Large files (>10MB)
echo "3. Checking for large files (>10MB)..."
LARGE=$(find "$WS" -type f -size +10M 2>/dev/null || true)
if [ -n "$LARGE" ]; then
    echo "ℹ️  Found large files:"
    echo "$LARGE" | while read -r file; do
        du -h "$file" 2>/dev/null
    done
else
    echo "✓ No large files"
fi
echo ""

# 4. Malformed names (spaces, braces, special chars)
echo "4. Checking for malformed file/directory names..."
MALFORMED=$(find "$WS" \( -name "* *" -o -name "*{*" -o -name "*}*" -o -name "*(*" -o -name "*)*" \) 2>/dev/null || true)
if [ -n "$MALFORMED" ]; then
    echo "⚠️  Found malformed names (spaces/special chars):"
    echo "$MALFORMED"
    echo ""
    echo "   Recommendation: Rename to kebab-case or snake_case"
    echo "   Example: 'my project' → 'my-project'"
else
    echo "✓ No malformed names"
fi
echo ""

# 5. Disk usage summary
echo "5. Disk usage by top-level directory:"
if [ -n "$(ls -A "$WS" 2>/dev/null)" ]; then
    du -sh "$WS"/* 2>/dev/null | sort -h || echo "  (Could not calculate disk usage)"
else
    echo "  (Empty workspace)"
fi
echo ""

# 6. File count summary
echo "6. File counts:"
TOTAL_FILES=$(find "$WS" -type f 2>/dev/null | wc -l)
TOTAL_DIRS=$(find "$WS" -type d 2>/dev/null | wc -l)
SKILLS=$(ls "$WS"/skills 2>/dev/null | wc -l)
SUBAGENTS=$(ls "$WS"/subagents 2>/dev/null | wc -l)

echo "  Total files: $TOTAL_FILES"
echo "  Total directories: $TOTAL_DIRS"
echo "  Skills: $SKILLS"
echo "  Subagents: $SUBAGENTS"
echo ""

# 7. Recent changes (last 24 hours)
echo "7. Recently modified files (last 24 hours):"
RECENT=$(find "$WS" -type f -mtime -1 2>/dev/null | head -10)
if [ -n "$RECENT" ]; then
    echo "$RECENT"
else
    echo "  (No recent changes)"
fi
echo ""

# 8. Git status summary (if .git exists)
if [ -d "$WS/.git" ]; then
    echo "8. Git status:"
    cd "$WS"
    UNSTAGED=$(git status --short 2>/dev/null | grep "^.M\|^.D\|^.A" | wc -l)
    UNTRACKED=$(git status --short 2>/dev/null | grep "^??" | wc -l)
    echo "  Unstaged changes: $UNSTAGED"
    echo "  Untracked files: $UNTRACKED"
    echo ""
fi

echo "=== Audit Complete ==="
echo ""
echo "Review findings and run cleanup if needed."
echo "See docs/organization-standards.md for best practices."
