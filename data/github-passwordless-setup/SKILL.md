---
name: github-passwordless-setup
description: Complete GitHub passwordless authentication setup using SSH keys and Personal Access Tokens. Never type passwords or re-authenticate for Git operations and GitHub API calls.
---

# GitHub Passwordless Setup

Complete guide to setting up passwordless authentication for GitHub using SSH keys and Personal Access Tokens (PAT). Once configured, you'll never need to enter passwords for Git operations or GitHub CLI commands.

**Verified Working:**
- ✅ macOS 10.15+ (tested on 14.4)
- ✅ Linux (Ubuntu, Debian, Fedora, Arch)
- ✅ Windows (WSL2, Git Bash)

## 🎯 What This Solves

**Before:**
- ❌ Type password every time you push/pull
- ❌ GitHub CLI requires re-authentication
- ❌ Tokens expire and break workflows
- ❌ HTTPS URLs need credentials repeatedly

**After:**
- ✅ Zero-password Git operations (push/pull/clone)
- ✅ Zero-password repository creation
- ✅ Zero-password issue/PR management
- ✅ Persistent authentication (no expiration)

## 🚀 Quick Setup

One-line automated setup:

```bash
curl -fsSL https://raw.githubusercontent.com/happydog-intj/github-passwordless-setup/master/setup.sh | bash
```

Or follow the manual steps below.

## 📋 Manual Setup

### Part 1: SSH Key Configuration

SSH keys enable password-free Git operations (push/pull/clone).

#### Step 1: Check for Existing SSH Keys

```bash
ls -la ~/.ssh/*.pub
```

If you see `id_ed25519.pub` or `id_rsa.pub`, you already have a key. Skip to Step 3.

#### Step 2: Generate New SSH Key

**Recommended: ED25519 (most secure)**

```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
```

**Or RSA (if ED25519 not supported):**

```bash
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
```

**During generation:**
- Press Enter for default location (`~/.ssh/id_ed25519`)
- Enter passphrase (optional but recommended)
- macOS will save passphrase to Keychain

#### Step 3: Copy Public Key

```bash
# macOS
cat ~/.ssh/id_ed25519.pub | pbcopy

# Linux (xclip)
cat ~/.ssh/id_ed25519.pub | xclip -selection clipboard

# Linux (xsel)
cat ~/.ssh/id_ed25519.pub | xsel --clipboard

# Or just display and copy manually
cat ~/.ssh/id_ed25519.pub
```

#### Step 4: Add Key to GitHub

1. Visit: https://github.com/settings/ssh/new
2. **Title**: `Your Computer Name (macOS/Linux)`
3. **Key type**: `Authentication Key`
4. **Key**: Paste your public key
5. Click **Add SSH key**

#### Step 5: Test SSH Connection

```bash
ssh -T git@github.com
```

Expected output:
```
Hi username! You've successfully authenticated, but GitHub does not provide shell access.
```

### Part 2: GitHub Personal Access Token

PAT enables password-free GitHub CLI operations (create repos, manage issues/PRs).

#### Step 1: Generate Token

Visit: https://github.com/settings/tokens/new

**Configuration:**
- **Note**: `OpenClaw CLI Token` (or any description)
- **Expiration**: `No expiration` (or 90 days)
- **Select scopes**:
  - ✅ **repo** (all sub-scopes)
  - ✅ **workflow** (if using GitHub Actions)
  - ✅ **delete_repo** (if you need to delete repositories)
  - ✅ **admin:org** (if managing organizations)

Click **Generate token** and **copy it immediately** (shown only once!).

Format: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

#### Step 2: Install GitHub CLI

**macOS:**
```bash
brew install gh
```

**Linux (Debian/Ubuntu):**
```bash
type -p curl >/dev/null || (sudo apt update && sudo apt install curl -y)
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh -y
```

**Other Linux:**
See: https://github.com/cli/cli/blob/trunk/docs/install_linux.md

#### Step 3: Configure Token

```bash
# Method 1: Interactive (paste when prompted)
gh auth login --with-token
# Then paste your token and press Enter

# Method 2: One-line (replace YOUR_TOKEN)
echo "ghp_YOUR_TOKEN_HERE" | gh auth login --with-token
```

#### Step 4: Set Git Protocol to SSH

```bash
gh config set git_protocol ssh
```

This ensures `gh` commands use SSH (not HTTPS) for Git operations.

### Part 3: Verification

#### Verify SSH Configuration

```bash
# Test SSH connection
ssh -T git@github.com

# Expected: Hi username! You've successfully authenticated...
```

#### Verify GitHub CLI

```bash
# Check authentication status
gh auth status

# Expected: ✓ Logged in to github.com account username

# Test API access
gh api user --jq '.login'

# Expected: your-username
```

#### Verify Complete Workflow

```bash
# Test creating a repository (will create and delete)
gh repo create test-auth-$(date +%s) --public --description "Test" \
  && echo "✅ Create: SUCCESS" \
  && gh repo delete $(gh repo list --limit 1 --json name --jq '.[0].name') --yes \
  && echo "✅ Delete: SUCCESS"
```

All operations should complete without prompting for passwords.

## 🔄 Convert Existing Repos to SSH

If you have existing repositories using HTTPS URLs:

```bash
# Check current remote
git remote -v

# If it shows https://github.com/...
# Convert to SSH
git remote set-url origin git@github.com:username/repo.git

# Verify
git remote -v
# Should show: git@github.com:username/repo.git
```

**Batch convert all repos in a directory:**

```bash
find . -name ".git" -type d | while read gitdir; do
  cd "$gitdir/.."
  if git remote get-url origin 2>/dev/null | grep -q "https://github.com"; then
    REPO=$(git remote get-url origin | sed 's|https://github.com/|git@github.com:|')
    git remote set-url origin "$REPO"
    echo "✅ Converted: $(pwd)"
  fi
  cd - > /dev/null
done
```

## 🛠️ Automated Setup Script

Save this as `setup.sh`:

```bash
#!/bin/bash
set -e

echo "🔐 GitHub Passwordless Setup"
echo "============================"
echo ""

# Check for existing SSH key
if [ -f ~/.ssh/id_ed25519.pub ]; then
    echo "✅ SSH key already exists"
    SSH_KEY=$(cat ~/.ssh/id_ed25519.pub)
elif [ -f ~/.ssh/id_rsa.pub ]; then
    echo "✅ SSH key already exists (RSA)"
    SSH_KEY=$(cat ~/.ssh/id_rsa.pub)
else
    echo "📝 Generating new ED25519 SSH key..."
    ssh-keygen -t ed25519 -C "$(whoami)@$(hostname)" -f ~/.ssh/id_ed25519 -N ""
    SSH_KEY=$(cat ~/.ssh/id_ed25519.pub)
    echo "✅ SSH key generated"
fi

echo ""
echo "🔑 Your public SSH key:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$SSH_KEY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Next steps:"
echo "1. Copy the key above"
echo "2. Visit: https://github.com/settings/ssh/new"
echo "3. Paste the key and save"
echo "4. Come back and press Enter to continue"
read -p "Press Enter after adding the key to GitHub..."

# Test SSH
echo ""
echo "🧪 Testing SSH connection..."
if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
    echo "✅ SSH authentication successful!"
else
    echo "❌ SSH authentication failed. Please check your key on GitHub."
    exit 1
fi

# Check for GitHub CLI
echo ""
if ! command -v gh &> /dev/null; then
    echo "📦 GitHub CLI not found. Install it from:"
    echo "   macOS: brew install gh"
    echo "   Linux: https://github.com/cli/cli/blob/trunk/docs/install_linux.md"
    exit 1
fi

# Configure GitHub CLI
echo "🎫 Configuring GitHub CLI..."
echo "Please enter your GitHub Personal Access Token:"
echo "(Visit https://github.com/settings/tokens/new if you don't have one)"
echo ""
gh auth login --with-token

# Set git protocol to SSH
gh config set git_protocol ssh

# Verify
echo ""
echo "🔍 Verifying configuration..."
if gh auth status &> /dev/null; then
    echo "✅ GitHub CLI authenticated"
    USERNAME=$(gh api user --jq '.login')
    echo "✅ Username: $USERNAME"
else
    echo "❌ GitHub CLI authentication failed"
    exit 1
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "You can now:"
echo "  • Push/pull without passwords: git push"
echo "  • Create repos instantly: gh repo create my-project --public"
echo "  • Manage issues/PRs: gh issue create, gh pr list"
echo ""
```

Make it executable and run:

```bash
chmod +x setup.sh
./setup.sh
```

## 🔍 Troubleshooting

### SSH Issues

**Problem: "Permission denied (publickey)"**

```bash
# Check SSH agent
ssh-add -l

# If empty or error, add your key
ssh-add ~/.ssh/id_ed25519

# macOS: Add to Keychain permanently
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
```

**Problem: "Host key verification failed"**

```bash
# Remove old host key
ssh-keygen -R github.com

# Reconnect (will prompt to add new key)
ssh -T git@github.com
```

### GitHub CLI Issues

**Problem: "Requires authentication"**

```bash
# Check token validity
gh auth status

# Re-authenticate
gh auth logout
gh auth login --with-token
```

**Problem: "Token scopes insufficient"**

Create a new token with broader scopes:
- Visit: https://github.com/settings/tokens
- Delete old token
- Create new with `repo`, `workflow`, `delete_repo`

### General Issues

**Check Configuration Files:**

```bash
# SSH config
cat ~/.ssh/config

# GitHub CLI config
cat ~/.config/gh/hosts.yml

# Git config
git config --global --list
```

## 🔒 Security Best Practices

### SSH Keys

1. **Use ED25519** (more secure than RSA)
2. **Set a passphrase** (optional but recommended)
3. **Use ssh-agent** (macOS Keychain, gnome-keyring)
4. **Never share private keys** (`id_ed25519` - no .pub)
5. **Revoke compromised keys immediately** at https://github.com/settings/keys

### Personal Access Tokens

1. **Minimum scopes needed** (don't select all)
2. **Set expiration** (90 days for security, or no expiration for convenience)
3. **Revoke unused tokens** at https://github.com/settings/tokens
4. **Never commit tokens** to repositories
5. **Rotate regularly** (every 90 days recommended)

## 📚 Advanced Configuration

### SSH Config File

Create `~/.ssh/config` for custom settings:

```ssh
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519
  AddKeysToAgent yes
  UseKeychain yes
```

### Multiple GitHub Accounts

```ssh
# ~/.ssh/config
Host github-personal
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_personal

Host github-work
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_work
```

Clone with specific account:
```bash
git clone git@github-personal:username/repo.git
git clone git@github-work:company/repo.git
```

### Git Aliases

Add to `~/.gitconfig`:

```ini
[alias]
  pushf = push --force-with-lease
  undo = reset --soft HEAD~1
  amend = commit --amend --no-edit
  sync = !git fetch --all && git pull
```

## 🌐 Environment Variables

Optional environment variables for automation:

```bash
# GitHub CLI
export GH_TOKEN="ghp_xxxxx"  # Auto-auth for gh commands

# Git
export GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519"  # Force specific key
```

Add to your shell profile (`~/.bashrc`, `~/.zshrc`):

```bash
# GitHub CLI auto-auth (optional)
if [ -f ~/.config/gh/token ]; then
  export GH_TOKEN=$(cat ~/.config/gh/token)
fi
```

## 🔄 Maintenance

### Update SSH Key

```bash
# Generate new key
ssh-keygen -t ed25519 -C "new-email@example.com"

# Add to GitHub
cat ~/.ssh/id_ed25519.pub | pbcopy
# Visit: https://github.com/settings/ssh/new

# Update old repos (if using specific key in config)
git config core.sshCommand "ssh -i ~/.ssh/id_ed25519"
```

### Rotate GitHub Token

```bash
# Create new token at https://github.com/settings/tokens/new
# Configure it
echo "ghp_NEW_TOKEN" | gh auth login --with-token

# Revoke old token at https://github.com/settings/tokens
```

## 📊 Comparison: HTTPS vs SSH

| Feature | HTTPS | SSH |
|---------|-------|-----|
| **Authentication** | Username + Token | SSH Key |
| **Password needed** | Every operation | Never |
| **Setup complexity** | Low | Medium |
| **Security** | Good | Excellent |
| **Corporate firewalls** | Usually allowed | Sometimes blocked |
| **Recommendation** | Beginners | Daily use |

## 🎯 Common Workflows

### Create New Project

```bash
# Create repo and push in one go
gh repo create my-project --public --source=. --push

# Or step by step
gh repo create my-project --public
git remote add origin git@github.com:username/my-project.git
git push -u origin main
```

### Clone Private Repo

```bash
# SSH (no password)
git clone git@github.com:username/private-repo.git

# Check access
gh repo view username/private-repo
```

### Manage Issues

```bash
# Create issue
gh issue create --title "Bug found" --body "Description"

# List issues
gh issue list

# Close issue
gh issue close 123
```

## 🤝 Contributing

Found an issue or improvement? Pull requests welcome!

## 📄 License

MIT License

## 🔗 Related Links

- [GitHub SSH Documentation](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
- [GitHub CLI Manual](https://cli.github.com/manual/)
- [OpenClaw](https://github.com/openclaw/openclaw)

---

**Made with ❤️ for developers who value automation**
