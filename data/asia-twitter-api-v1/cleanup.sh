#!/bin/bash
# OpenClaw Twitter - Package Cleanup Script
# Removes system files, cache, and temporary files before distribution

set -e  # Exit on error

echo "🧹 OpenClaw Twitter - Package Cleanup"
echo "======================================"
echo ""

# Counter for removed files
count=0

# Function to remove files and count
remove_files() {
    local pattern=$1
    local description=$2
    local found=$(find . -name "$pattern" -type f 2>/dev/null | wc -l)
    
    if [ "$found" -gt 0 ]; then
        echo "🗑️  Removing $description... ($found files)"
        find . -name "$pattern" -type f -delete 2>/dev/null
        count=$((count + found))
    fi
}

# Function to remove directories
remove_dirs() {
    local pattern=$1
    local description=$2
    local found=$(find . -type d -name "$pattern" 2>/dev/null | wc -l)
    
    if [ "$found" -gt 0 ]; then
        echo "🗑️  Removing $description... ($found directories)"
        find . -type d -name "$pattern" -exec rm -rf {} + 2>/dev/null || true
        count=$((count + found))
    fi
}

echo "Cleaning system files..."
echo "------------------------"

# macOS system files
remove_files ".DS_Store" "macOS .DS_Store files"
remove_files "._*" "macOS resource forks"
remove_dirs ".Spotlight-V100" "Spotlight indexes"
remove_dirs ".Trashes" "Trash metadata"
remove_files ".AppleDouble" "AppleDouble files"
remove_files ".LSOverride" "LSOverride files"

# Windows system files
remove_files "Thumbs.db" "Windows thumbnail cache"
remove_files "Desktop.ini" "Windows Desktop.ini"
remove_dirs "\$RECYCLE.BIN" "Recycle bin"
remove_files "ehthumbs.db" "Windows thumbnail cache"

# Linux backup files
remove_files "*~" "Linux backup files"
remove_files ".directory" "KDE directory metadata"

echo ""
echo "Cleaning Python artifacts..."
echo "----------------------------"

# Python cache
remove_dirs "__pycache__" "Python cache directories"
remove_files "*.pyc" "Python compiled files"
remove_files "*.pyo" "Python optimized files"
remove_files "*.pyd" "Python DLL files"
remove_dirs ".pytest_cache" "Pytest cache"
remove_dirs ".tox" "Tox environments"
remove_dirs ".coverage" "Coverage reports"
remove_dirs "htmlcov" "HTML coverage reports"
remove_dirs "*.egg-info" "Egg info"

echo ""
echo "Cleaning temporary files..."
echo "---------------------------"

remove_files "*.tmp" "Temporary files"
remove_files "*.temp" "Temporary files"
remove_files "*.log" "Log files"
remove_files "*.bak" "Backup files"
remove_files "*.backup" "Backup files"
remove_files "*.swp" "Vim swap files"
remove_files "*.swo" "Vim swap files"
remove_files "*.swn" "Vim swap files"

echo ""
echo "Cleaning IDE files..."
echo "---------------------"

remove_dirs ".vscode" "VS Code settings"
remove_dirs ".idea" "IntelliJ IDEA settings"
remove_files "*.sublime-project" "Sublime Text projects"
remove_files "*.sublime-workspace" "Sublime Text workspaces"

echo ""
echo "Cleaning build artifacts..."
echo "---------------------------"

remove_dirs "build" "Build directories"
remove_dirs "dist" "Distribution directories"
remove_dirs ".eggs" "Eggs directories"

echo ""
echo "✅ Cleanup complete!"
echo "===================="
echo "📊 Removed: $count items"
echo ""

# Verify no sensitive data
echo "🔍 Checking for potential secrets..."
echo "-------------------------------------"

secrets_found=false

# Check for API keys (common patterns)
if grep -r "sk-[a-zA-Z0-9]\{20,\}" . 2>/dev/null | grep -v ".git" | grep -v "cleanup.sh" | grep -v "PACKAGE_HYGIENE.md"; then
    echo "⚠️  WARNING: Potential API keys found!"
    secrets_found=true
fi

# Check for hardcoded credentials
if grep -r "password.*=.*['\"][^'\"]*['\"]" . 2>/dev/null | grep -v ".git" | grep -v "cleanup.sh" | grep -v "SECURITY.md" | grep -v "twitter_client.py"; then
    echo "⚠️  WARNING: Potential hardcoded passwords found!"
    secrets_found=true
fi

# Check for .env files
if find . -name ".env" -o -name "*.env" | grep -v ".gitignore"; then
    echo "⚠️  WARNING: Environment files found!"
    secrets_found=true
fi

if [ "$secrets_found" = false ]; then
    echo "✅ No obvious secrets detected"
fi

echo ""
echo "📋 Package summary:"
echo "-------------------"
echo "Total files: $(find . -type f | wc -l)"
echo "Total size:  $(du -sh . | cut -f1)"
echo ""

# List remaining files by type
echo "📁 File types:"
if command -v tree >/dev/null 2>&1; then
    tree -L 2 --dirsfirst
else
    echo ""
    echo "Python files:     $(find . -name "*.py" | wc -l)"
    echo "Markdown files:   $(find . -name "*.md" | wc -l)"
    echo "Other files:      $(find . -type f ! -name "*.py" ! -name "*.md" | wc -l)"
fi

echo ""
echo "💡 Next steps:"
echo "  1. Review the file list above"
echo "  2. If secrets were found, remove them before distribution"
echo "  3. Run: git status"
echo "  4. Create clean archive: git archive HEAD -o package.zip"
echo ""
