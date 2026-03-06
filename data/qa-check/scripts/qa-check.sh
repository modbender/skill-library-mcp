#!/bin/bash
# QA Check Script - Run before deploying any project
# Usage: qa-check.sh <project-dir>

set -e

PROJECT_DIR="${1:-.}"
FAILED=0
PASSED=0

echo "🔍 QA Check for: $PROJECT_DIR"
echo "=================================="

# 1. Build Check
echo ""
echo "1️⃣ Build Validation..."
cd "$PROJECT_DIR"
if npm run build 2>&1 | tee /tmp/build.log; then
    echo "✅ Build passed"
    ((PASSED++))
else
    echo "❌ Build FAILED"
    ((FAILED++))
fi

# 2. Check for common issues in build output
echo ""
echo "2️⃣ Checking for warnings..."
if grep -i "warning" /tmp/build.log | grep -v "node_modules" | head -5; then
    echo "⚠️  Warnings found (review above)"
else
    echo "✅ No critical warnings"
    ((PASSED++))
fi

# 3. Check bundle size
echo ""
echo "3️⃣ Bundle size check..."
if [ -d "dist" ]; then
    DIST_SIZE=$(du -sh dist 2>/dev/null | cut -f1)
    echo "📦 Dist size: $DIST_SIZE"
    ((PASSED++))
fi

# 4. Check index.html meta tags
echo ""
echo "4️⃣ SEO/Meta check..."
if [ -f "index.html" ]; then
    TITLE=$(grep -o '<title>[^<]*</title>' index.html 2>/dev/null || echo "")
    DESC=$(grep 'name="description"' index.html 2>/dev/null || echo "")
    OG=$(grep 'property="og:' index.html 2>/dev/null || echo "")
    
    if [ -n "$TITLE" ]; then
        echo "✅ Title: $TITLE"
        ((PASSED++))
    else
        echo "❌ Missing <title>"
        ((FAILED++))
    fi
    
    if [ -n "$DESC" ]; then
        echo "✅ Meta description present"
        ((PASSED++))
    else
        echo "❌ Missing meta description"
        ((FAILED++))
    fi
    
    if [ -n "$OG" ]; then
        echo "✅ Open Graph tags present"
        ((PASSED++))
    else
        echo "⚠️  Missing Open Graph tags"
    fi
fi

# 5. Check for favicon
echo ""
echo "5️⃣ Favicon check..."
if [ -f "public/favicon.svg" ] || [ -f "public/favicon.ico" ] || [ -f "public/favicon.png" ]; then
    echo "✅ Favicon found"
    ((PASSED++))
else
    echo "⚠️  No favicon found in public/"
fi

# Summary
echo ""
echo "=================================="
echo "📊 QA Summary"
echo "✅ Passed: $PASSED"
echo "❌ Failed: $FAILED"
echo ""

if [ $FAILED -gt 0 ]; then
    echo "🚫 QA FAILED - Do not deploy until issues are fixed"
    exit 1
else
    echo "✅ QA PASSED - Safe to deploy"
    exit 0
fi
