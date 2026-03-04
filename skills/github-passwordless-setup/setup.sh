#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔐 GitHub Passwordless Setup${NC}"
echo "============================"
echo ""

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    CYGWIN*|MINGW*|MSYS*)    MACHINE=Windows;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo -e "${GREEN}Platform detected: $MACHINE${NC}"
echo ""

# Part 1: SSH Key Setup
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Part 1: SSH Key Configuration${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check for existing SSH key
SSH_KEY_PATH=""
if [ -f ~/.ssh/id_ed25519.pub ]; then
    echo -e "${GREEN}✅ SSH key already exists (ED25519)${NC}"
    SSH_KEY_PATH=~/.ssh/id_ed25519.pub
elif [ -f ~/.ssh/id_rsa.pub ]; then
    echo -e "${GREEN}✅ SSH key already exists (RSA)${NC}"
    SSH_KEY_PATH=~/.ssh/id_rsa.pub
else
    echo -e "${BLUE}📝 Generating new ED25519 SSH key...${NC}"
    
    # Get user email
    read -p "Enter your email for SSH key: " USER_EMAIL
    
    # Generate key
    ssh-keygen -t ed25519 -C "$USER_EMAIL" -f ~/.ssh/id_ed25519 -N ""
    
    SSH_KEY_PATH=~/.ssh/id_ed25519.pub
    echo -e "${GREEN}✅ SSH key generated${NC}"
fi

# Display and copy public key
echo ""
echo -e "${BLUE}🔑 Your public SSH key:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
SSH_KEY=$(cat $SSH_KEY_PATH)
echo "$SSH_KEY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Copy to clipboard
if command -v pbcopy &> /dev/null; then
    echo "$SSH_KEY" | pbcopy
    echo -e "${GREEN}✅ Key copied to clipboard (macOS)${NC}"
elif command -v xclip &> /dev/null; then
    echo "$SSH_KEY" | xclip -selection clipboard
    echo -e "${GREEN}✅ Key copied to clipboard (xclip)${NC}"
elif command -v xsel &> /dev/null; then
    echo "$SSH_KEY" | xsel --clipboard
    echo -e "${GREEN}✅ Key copied to clipboard (xsel)${NC}"
else
    echo -e "${YELLOW}📋 Please copy the key above manually${NC}"
fi

echo ""
echo -e "${YELLOW}📋 Next steps:${NC}"
echo "1. Visit: https://github.com/settings/ssh/new"
echo "2. Paste the key above"
echo "3. Click 'Add SSH key'"
echo ""
read -p "Press Enter after adding the key to GitHub..."

# Test SSH connection
echo ""
echo -e "${BLUE}🧪 Testing SSH connection to GitHub...${NC}"
if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
    echo -e "${GREEN}✅ SSH authentication successful!${NC}"
else
    echo -e "${RED}❌ SSH authentication failed.${NC}"
    echo "Please verify:"
    echo "  1. Key was added correctly to GitHub"
    echo "  2. You're connected to the internet"
    echo "  3. GitHub is accessible from your network"
    exit 1
fi

# Part 2: GitHub CLI Setup
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Part 2: GitHub CLI Configuration${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check for GitHub CLI
if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}📦 GitHub CLI not found${NC}"
    echo ""
    echo "Install instructions:"
    if [ "$MACHINE" = "Mac" ]; then
        echo "  brew install gh"
    elif [ "$MACHINE" = "Linux" ]; then
        echo "  Visit: https://github.com/cli/cli/blob/trunk/docs/install_linux.md"
    else
        echo "  Visit: https://cli.github.com/"
    fi
    echo ""
    read -p "Install GitHub CLI and press Enter to continue (or Ctrl+C to exit)..."
    
    # Re-check
    if ! command -v gh &> /dev/null; then
        echo -e "${RED}❌ GitHub CLI still not found${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ GitHub CLI found${NC}"
echo ""

# Configure GitHub CLI
echo -e "${BLUE}🎫 Configuring GitHub CLI with Personal Access Token...${NC}"
echo ""
echo "To create a token:"
echo "  1. Visit: https://github.com/settings/tokens/new"
echo "  2. Note: 'OpenClaw CLI Token' (or any description)"
echo "  3. Expiration: 'No expiration' (or 90 days)"
echo "  4. Scopes: ✅ repo (select all sub-scopes)"
echo "  5. Click 'Generate token' and copy it"
echo ""
echo "Token format: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
echo ""

# Logout any existing sessions
gh auth logout -h github.com 2>/dev/null || true

echo "Please paste your GitHub Personal Access Token:"
gh auth login --with-token

# Set git protocol to SSH
gh config set git_protocol ssh
echo -e "${GREEN}✅ Git protocol set to SSH${NC}"

# Part 3: Verification
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Part 3: Verification${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Verify SSH
echo -e "${BLUE}🔍 Verifying SSH...${NC}"
if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
    echo -e "${GREEN}✅ SSH: Working${NC}"
else
    echo -e "${RED}❌ SSH: Failed${NC}"
    exit 1
fi

# Verify GitHub CLI
echo -e "${BLUE}🔍 Verifying GitHub CLI...${NC}"
if gh auth status &> /dev/null; then
    USERNAME=$(gh api user --jq '.login' 2>/dev/null)
    echo -e "${GREEN}✅ GitHub CLI: Authenticated as $USERNAME${NC}"
else
    echo -e "${RED}❌ GitHub CLI: Authentication failed${NC}"
    exit 1
fi

# Test complete workflow
echo -e "${BLUE}🔍 Testing complete workflow...${NC}"
TEST_REPO="test-auth-verify-$(date +%s | tail -c 6)"
if gh repo create "$TEST_REPO" --public --description "Automated test" &> /dev/null; then
    echo -e "${GREEN}✅ Repository creation: Working${NC}"
    
    # Delete test repo
    if gh repo delete "$(gh api user --jq '.login')/$TEST_REPO" --yes &> /dev/null; then
        echo -e "${GREEN}✅ Repository deletion: Working${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Repository creation: Skipped (permissions?)${NC}"
fi

# Success!
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "You can now:"
echo "  • Push/pull without passwords:"
echo "    ${BLUE}git push${NC}, ${BLUE}git pull${NC}, ${BLUE}git clone${NC}"
echo ""
echo "  • Create repositories instantly:"
echo "    ${BLUE}gh repo create my-project --public${NC}"
echo ""
echo "  • Manage issues and PRs:"
echo "    ${BLUE}gh issue create${NC}, ${BLUE}gh pr list${NC}"
echo ""
echo "  • Convert existing repos to SSH:"
echo "    ${BLUE}git remote set-url origin git@github.com:user/repo.git${NC}"
echo ""
echo -e "${YELLOW}📚 See README.md and SKILL.md for more info${NC}"
echo ""
