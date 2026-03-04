#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 GitHub Passwordless Configuration Verification${NC}"
echo "=================================================="
echo ""

ERRORS=0

# Check 1: SSH Key
echo -e "${YELLOW}1️⃣ Checking SSH Key...${NC}"
if [ -f ~/.ssh/id_ed25519.pub ] || [ -f ~/.ssh/id_rsa.pub ]; then
    echo -e "${GREEN}   ✅ SSH key exists${NC}"
    
    # Test connection
    if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
        echo -e "${GREEN}   ✅ SSH connection to GitHub: Working${NC}"
    else
        echo -e "${RED}   ❌ SSH connection to GitHub: Failed${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${RED}   ❌ No SSH key found${NC}"
    echo -e "${YELLOW}   Run: ssh-keygen -t ed25519 -C \"your-email@example.com\"${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 2: GitHub CLI
echo -e "${YELLOW}2️⃣ Checking GitHub CLI...${NC}"
if command -v gh &> /dev/null; then
    echo -e "${GREEN}   ✅ GitHub CLI installed${NC}"
    
    # Check authentication
    if gh auth status &> /dev/null; then
        USERNAME=$(gh api user --jq '.login' 2>/dev/null)
        echo -e "${GREEN}   ✅ Authenticated as: $USERNAME${NC}"
        
        # Check git protocol
        PROTOCOL=$(gh config get git_protocol 2>/dev/null || echo "https")
        if [ "$PROTOCOL" = "ssh" ]; then
            echo -e "${GREEN}   ✅ Git protocol: SSH${NC}"
        else
            echo -e "${YELLOW}   ⚠️  Git protocol: $PROTOCOL (recommended: ssh)${NC}"
            echo -e "${YELLOW}   Run: gh config set git_protocol ssh${NC}"
        fi
    else
        echo -e "${RED}   ❌ Not authenticated${NC}"
        echo -e "${YELLOW}   Run: gh auth login --with-token${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${RED}   ❌ GitHub CLI not installed${NC}"
    echo -e "${YELLOW}   macOS: brew install gh${NC}"
    echo -e "${YELLOW}   Linux: https://github.com/cli/cli/blob/trunk/docs/install_linux.md${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 3: Test workflow
echo -e "${YELLOW}3️⃣ Testing complete workflow...${NC}"
if command -v gh &> /dev/null && gh auth status &> /dev/null; then
    TEST_REPO="test-verify-$(date +%s | tail -c 6)"
    
    if gh repo create "$TEST_REPO" --public --description "Test" &> /dev/null; then
        echo -e "${GREEN}   ✅ Create repository: Working${NC}"
        
        if gh repo delete "$(gh api user --jq '.login')/$TEST_REPO" --yes &> /dev/null; then
            echo -e "${GREEN}   ✅ Delete repository: Working${NC}"
        else
            echo -e "${YELLOW}   ⚠️  Delete repository: Failed${NC}"
        fi
    else
        echo -e "${RED}   ❌ Create repository: Failed${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${YELLOW}   ⏭️  Skipped (prerequisites not met)${NC}"
fi
echo ""

# Summary
echo "=================================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}🎉 All checks passed!${NC}"
    echo ""
    echo "Your GitHub passwordless setup is complete and working."
    echo ""
    echo "You can now:"
    echo "  • git push/pull without passwords"
    echo "  • gh repo create without re-authentication"
    echo "  • All GitHub operations seamlessly"
else
    echo -e "${RED}❌ $ERRORS error(s) found${NC}"
    echo ""
    echo "Please review the errors above and fix them."
    echo "See SKILL.md for detailed troubleshooting."
fi
echo "=================================================="
echo ""

exit $ERRORS
