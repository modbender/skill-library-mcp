# Installation Errors

Complete guide to OpenClaw installation and setup issues across all platforms.

## Error Types

### NODE_VERSION_OLD

**Symptoms:**
- "Node.js version 22 or higher required" error
- Installation fails with version check
- Features not working (using old syntax)
- npm/pnpm errors about unsupported version

**Diagnostic Commands:**
```bash
# Check Node.js version
node --version

# Check npm version
npm --version

# Check if nvm installed
nvm --version
```

**Fix:**

**Linux:**
```bash
# Using nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 22
nvm use 22
nvm alias default 22

# Using NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify
node --version  # Should show v22.x.x
```

**macOS:**
```bash
# Using nvm
brew install nvm
nvm install 22
nvm use 22

# Or using Homebrew directly
brew install node@22
brew link --overwrite node@22

# Verify
node --version
```

**Windows:**
```powershell
# Download from nodejs.org
# Or use nvm-windows
choco install nvm
nvm install 22
nvm use 22

# Or use official installer
# https://nodejs.org/dist/v22.0.0/node-v22.0.0-x64.msi

# Verify
node --version
```

**Auto-Fix Available:** No (requires system-level install)

---

### PNPM_NOT_FOUND

**Symptoms:**
- "pnpm: command not found" error
- Installation script fails
- Cannot run OpenClaw commands

**Diagnostic Commands:**
```bash
# Check if pnpm installed
which pnpm
pnpm --version

# Check PATH
echo $PATH | tr ':' '\n' | grep pnpm
```

**Fix:**

**All Platforms:**
```bash
# Install pnpm via npm (recommended)
npm install -g pnpm

# Or via standalone script
curl -fsSL https://get.pnpm.io/install.sh | sh -

# Or via Homebrew (macOS)
brew install pnpm

# Or via Chocolatey (Windows)
choco install pnpm

# Verify
pnpm --version
```

**Fix PATH if needed:**
```bash
# Linux/macOS
echo 'export PATH="$HOME/.local/share/pnpm:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Windows (PowerShell as Admin)
$env:Path += ";$env:LOCALAPPDATA\pnpm"
[Environment]::SetEnvironmentVariable("Path", $env:Path, "User")
```

**Auto-Fix Available:** No (requires package manager)

---

### NPM_INSTALL_FAILED

**Symptoms:**
- "npm install failed" or "pnpm install failed"
- Dependency resolution errors
- Network timeout during install
- Permission errors during install

**Common Causes:**
- Network connectivity issues
- Registry timeout
- Permission denied (installing globally without sudo)
- Disk space full
- Corrupted package cache

**Diagnostic Commands:**
```bash
# Check disk space
df -h

# Check npm registry
npm config get registry
ping registry.npmjs.org

# Check cache
npm cache verify
pnpm store status

# Test network
curl -I https://registry.npmjs.org
```

**Fix:**

**Network Issues:**
```bash
# Use different registry
npm config set registry https://registry.npmmirror.com  # China mirror
pnpm config set registry https://registry.npmmirror.com

# Increase timeout
npm config set timeout 60000
pnpm config set network-timeout 60000

# Use corporate proxy
npm config set proxy http://proxy.company.com:8080
npm config set https-proxy http://proxy.company.com:8080
```

**Permission Issues:**
```bash
# Fix npm permissions (Linux/macOS)
mkdir -p ~/.npm-global
npm config set prefix ~/.npm-global
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.profile
source ~/.profile

# Or use sudo (not recommended)
sudo npm install -g openclaw

# Fix ownership
sudo chown -R $USER:$USER ~/.npm
sudo chown -R $USER:$USER ~/.pnpm-store
```

**Cache Issues:**
```bash
# Clear npm cache
npm cache clean --force

# Clear pnpm cache
pnpm store prune

# Remove node_modules and retry
rm -rf node_modules package-lock.json
npm install
```

**Dependency Conflicts:**
```bash
# Use legacy peer deps
npm install --legacy-peer-deps

# Or force install
npm install --force

# For pnpm
pnpm install --no-strict-peer-dependencies
```

**Auto-Fix Available:** Partial

---

### PATH_NOT_SET

**Symptoms:**
- "openclaw: command not found" error
- Binary installed but not accessible
- Works in install directory but not globally

**Diagnostic Commands:**
```bash
# Check if openclaw exists
which openclaw
find / -name openclaw 2>/dev/null

# Check PATH
echo $PATH

# Check npm global bin path
npm bin -g
pnpm bin -g
```

**Fix:**

**Linux/macOS:**
```bash
# Add npm global bin to PATH
echo 'export PATH="$(npm bin -g):$PATH"' >> ~/.bashrc
source ~/.bashrc

# Or for pnpm
echo 'export PATH="$(pnpm bin -g):$PATH"' >> ~/.bashrc
source ~/.bashrc

# Or add specific path
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# For zsh users
echo 'export PATH="$(npm bin -g):$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Windows:**
```powershell
# Add to PATH (PowerShell as Admin)
$npmPath = npm bin -g
$env:Path += ";$npmPath"
[Environment]::SetEnvironmentVariable("Path", $env:Path, "User")

# Restart terminal
```

**Verify:**
```bash
# Should show path to openclaw
which openclaw

# Should work from any directory
cd ~
openclaw --version
```

**Auto-Fix Available:** Yes

---

### DEPENDENCY_CONFLICT

**Symptoms:**
- "Peer dependency conflict" errors
- "Could not resolve dependency" errors
- Version mismatch warnings
- Installation completes but features broken

**Diagnostic Commands:**
```bash
# Check for conflicts
npm ls
pnpm why <package-name>

# View dependency tree
npm list --depth=1
```

**Fix:**
```bash
# Update to compatible versions
pnpm update --latest

# Resolve conflicts
pnpm install --fix-lockfile

# Use overrides (package.json)
{
  "pnpm": {
    "overrides": {
      "problematic-package": "^2.0.0"
    }
  }
}

# Or dedupe
npm dedupe

# Clean install
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

**Auto-Fix Available:** No (requires manual resolution)

---

## Platform-Specific Installation

### Linux (Ubuntu/Debian)

```bash
# Install prerequisites
sudo apt update
sudo apt install -y curl git build-essential

# Install Node.js 22
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs

# Install pnpm
npm install -g pnpm

# Install OpenClaw
pnpm install -g openclaw

# Verify
openclaw --version
openclaw doctor
```

### macOS

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Node.js
brew install node@22
brew link --overwrite node@22

# Install pnpm
brew install pnpm

# Install OpenClaw
pnpm install -g openclaw

# Verify
openclaw --version
openclaw doctor
```

### Windows

```powershell
# Install via Chocolatey (run as Administrator)
# Install Chocolatey first: https://chocolatey.org/install

# Install Node.js
choco install nodejs-lts --version=22.0.0

# Install pnpm
choco install pnpm

# Install OpenClaw
pnpm install -g openclaw

# Verify
openclaw --version
openclaw doctor
```

### Docker Installation

```bash
# Pull official image
docker pull openclaw/openclaw:latest

# Or build from source
git clone https://github.com/openclaw/openclaw.git
cd openclaw
docker build -t openclaw:local .

# Run container
docker run -d \
  --name openclaw \
  -p 18789:18789 \
  -v ~/.openclaw:/root/.openclaw \
  -e OPENAI_API_KEY=sk-... \
  openclaw/openclaw:latest

# Check status
docker logs openclaw
docker exec openclaw openclaw status
```

## Post-Installation Setup

### First-Time Configuration

```bash
# Run setup wizard
openclaw init

# Or manual setup
openclaw config init

# Set API keys
openclaw config set ai.providers.openai.apiKey "sk-..."
openclaw config set ai.providers.anthropic.apiKey "sk-ant-..."

# Enable channels
openclaw channels enable whatsapp
openclaw channels enable telegram

# Start gateway
openclaw start

# Verify installation
openclaw doctor
openclaw status
```

### Verify Installation

```bash
# Check all components
openclaw doctor --full

# Expected output:
# ✓ Node.js version (22.x.x)
# ✓ pnpm installed
# ✓ OpenClaw installed
# ✓ Configuration valid
# ✓ Gateway running (port 18789)
# ✓ AI providers configured
# ✓ Channels configured
```

## Common Installation Workflows

### Fresh Install
```bash
# 1. Install Node.js 22+
nvm install 22

# 2. Install pnpm
npm install -g pnpm

# 3. Install OpenClaw
pnpm install -g openclaw

# 4. Initialize
openclaw init

# 5. Configure
openclaw config wizard

# 6. Start
openclaw start
```

### Update/Upgrade
```bash
# Check current version
openclaw --version

# Update to latest
pnpm update -g openclaw

# Or reinstall
pnpm remove -g openclaw
pnpm install -g openclaw

# Migrate config if needed
openclaw config migrate

# Restart
openclaw restart
```

### Troubleshooting Failed Install
```bash
# 1. Clean everything
pnpm remove -g openclaw
rm -rf ~/.openclaw/cache
pnpm cache clean --force

# 2. Check prerequisites
node --version  # Must be 22+
pnpm --version

# 3. Fix permissions
sudo chown -R $USER:$USER ~/.npm
sudo chown -R $USER:$USER ~/.pnpm-store

# 4. Reinstall
pnpm install -g openclaw --force

# 5. Verify
openclaw doctor --verbose
```

## Development Installation

```bash
# Clone repository
git clone https://github.com/openclaw/openclaw.git
cd openclaw

# Install dependencies
pnpm install

# Build
pnpm build

# Link for local development
pnpm link --global

# Run in dev mode
pnpm dev

# Run tests
pnpm test
```

## Uninstallation

```bash
# Stop gateway
openclaw stop

# Uninstall package
pnpm remove -g openclaw

# Remove config (optional)
rm -rf ~/.openclaw

# Remove from PATH (if manually added)
# Edit ~/.bashrc and remove openclaw PATH entries
```

## Related Files

- [Error Catalog](error-catalog.md) - All error types
- [Configuration Errors](configuration-errors.md) - Config setup
- [Gateway Errors](gateway-errors.md) - Post-install issues
- [Diagnostic Commands](diagnostic-commands.md) - Verification commands
