#!/bin/bash
# Pre-publish portability checklist
# Run this before pushing code to GitHub/ClawdHub

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🔍 Portable Tools - Pre-Publish Checklist"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

TARGET="${1:-.}"

if [[ ! -d "$TARGET" ]]; then
    echo -e "${RED}❌ Target directory not found: $TARGET${NC}"
    exit 1
fi

echo "Checking: $TARGET"
echo ""

# Check for hardcoded paths
echo "━━━ Hardcoded Paths Check ━━━"
HARDCODED_PATHS=$(grep -r "/Users/" "$TARGET" --include="*.sh" --include="*.bash" --include="*.py" 2>/dev/null || true)
if [[ -n "$HARDCODED_PATHS" ]]; then
    echo -e "${RED}❌ Found hardcoded paths:${NC}"
    echo "$HARDCODED_PATHS" | head -5
    echo -e "${YELLOW}   Use \$HOME, \$USER, or make configurable${NC}"
else
    echo -e "${GREEN}✅ No hardcoded paths${NC}"
fi
echo ""

# Check for validation patterns
echo "━━━ Input Validation Check ━━━"
READS_INPUT=$(grep -r "read\|curl\|jq\|security find" "$TARGET" --include="*.sh" --include="*.bash" 2>/dev/null | wc -l || echo 0)
HAS_VALIDATION=$(grep -r "validate\|check\|verify\|\[\[.*-z\|if.*empty" "$TARGET" --include="*.sh" --include="*.bash" 2>/dev/null | wc -l || echo 0)

if [[ $READS_INPUT -gt 0 ]] && [[ $HAS_VALIDATION -eq 0 ]]; then
    echo -e "${RED}❌ Reads input but no validation found${NC}"
    echo -e "${YELLOW}   Add validation after reading external data${NC}"
else
    echo -e "${GREEN}✅ Has validation patterns${NC}"
fi
echo ""

# Check for error messages
echo "━━━ Error Handling Check ━━━"
HAS_ERRORS=$(grep -r "error\|exit 1" "$TARGET" --include="*.sh" --include="*.bash" 2>/dev/null | wc -l || echo 0)
HAS_HELPFUL_ERRORS=$(grep -r "error.*Hint\|error.*Verify\|error.*Check" "$TARGET" --include="*.sh" --include="*.bash" 2>/dev/null | wc -l || echo 0)

if [[ $HAS_ERRORS -gt 0 ]] && [[ $HAS_HELPFUL_ERRORS -eq 0 ]]; then
    echo -e "${YELLOW}⚠️  Has errors but they could be more helpful${NC}"
    echo -e "${YELLOW}   Add hints: 'Verify with: command', 'Expected: ...'${NC}"
else
    echo -e "${GREEN}✅ Has helpful error messages${NC}"
fi
echo ""

# Check for configuration
echo "━━━ Configuration Check ━━━"
HAS_CONFIG=$(find "$TARGET" -name "*config*.json" -o -name "*config*.example*" 2>/dev/null | wc -l || echo 0)
USES_HARDCODED=$(grep -r "ACCOUNT=\|SERVICE=\|TOKEN=" "$TARGET" --include="*.sh" --include="*.bash" 2>/dev/null | grep -v ":-\|//" | wc -l || echo 0)

if [[ $USES_HARDCODED -gt 0 ]] && [[ $HAS_CONFIG -eq 0 ]]; then
    echo -e "${RED}❌ Uses hardcoded values without config file${NC}"
    echo -e "${YELLOW}   Make values configurable with defaults${NC}"
else
    echo -e "${GREEN}✅ Uses configuration${NC}"
fi
echo ""

# Check for README
echo "━━━ Documentation Check ━━━"
if [[ ! -f "$TARGET/README.md" ]]; then
    echo -e "${RED}❌ No README.md${NC}"
else
    HAS_TROUBLESHOOTING=$(grep -i "troubleshoot\|common issues\|faq" "$TARGET/README.md" 2>/dev/null | wc -l || echo 0)
    if [[ $HAS_TROUBLESHOOTING -eq 0 ]]; then
        echo -e "${YELLOW}⚠️  README exists but no troubleshooting section${NC}"
    else
        echo -e "${GREEN}✅ README with troubleshooting${NC}"
    fi
fi
echo ""

# Interactive questions
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📋 Manual Checklist"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Have you answered these questions?"
echo ""
echo "1️⃣  What varies between devices?"
echo "   (paths? account names? data formats?)"
echo ""
echo "2️⃣  How do you prove this works?"
echo "   (showed BEFORE/AFTER with real values?)"
echo ""
echo "3️⃣  What happens when it breaks?"
echo "   (tested with wrong config? missing data?)"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Review the portable-tools skill for detailed patterns:"
echo "  ~/clawd/skills/portable-tools/SKILL.md"
echo ""
