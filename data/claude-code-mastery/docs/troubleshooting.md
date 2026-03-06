# Claude Code Troubleshooting Guide

Common issues and solutions for Claude Code CLI.

---

## Authentication Issues

### Invalid API Key

**Symptoms:** "Invalid API key" or authentication errors

**Solutions:**
1. Get a valid API key from [console.anthropic.com](https://console.anthropic.com)
2. Ensure no extra spaces or characters when entering the key
3. Reconfigure: `claude config`

### Browser Login Failures

**Symptoms:** OAuth redirect doesn't work, login hangs

**Solutions:**
1. Log out of Claude completely in your browser
2. Clear browser cookies and cache
3. Try incognito/private browsing window
4. Run `claude config` or `/login` to restart OAuth flow
5. If browser doesn't open, press `c` to copy the OAuth URL manually

### Persistent Logout Bug

**Symptoms:** Repeatedly logged out, session doesn't persist

**Solutions:**
1. Remove auth file and re-login:
   ```bash
   rm -rf ~/.config/claude-code/auth.json
   claude
   ```
2. Try reconfiguring with `/mcp` command as workaround

### Incomplete Onboarding

**Symptoms:** Auth fails even with valid credentials

**Solution:** Complete the initial user onboarding at [claude.ai](https://claude.ai) first

### Third-Party Providers (Bedrock/Vertex)

**Symptoms:** Can't authenticate with AWS Bedrock or Google Vertex

**Solutions:**
1. Set environment variable:
   ```bash
   # For AWS Bedrock
   export CLAUDE_CODE_USE_BEDROCK="1"
   
   # For Google Vertex
   export CLAUDE_CODE_USE_VERTEX="1"
   ```
2. Verify AWS/GCP credentials are properly configured
3. Check IAM permissions for Claude API access

---

## Installation Issues

### "Command not found" (macOS/Linux)

**Symptoms:** `claude: command not found`

**Solutions:**
1. Add `~/.local/bin` to PATH:
   ```bash
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc  # or ~/.bashrc
   source ~/.zshrc
   ```
2. Verify installation: `ls -la ~/.local/bin/claude`

### "installMethod is native, but claude command not found"

**Symptoms:** Installed but command not recognized

**Solutions:**
1. Check installation health: `~/.local/bin/claude doctor`
2. Manually add to PATH (see above)
3. Reinstall using native installer:
   ```bash
   curl -fsSL https://claude.ai/install.sh | bash
   ```

### Node.js Version Issues

**Symptoms:** Errors about Node.js version

**Solutions:**
1. Check version: `node --version` (requires 18.0+)
2. Update Node.js: [nodejs.org](https://nodejs.org)
3. Or use nvm: `nvm install 18 && nvm use 18`

### Windows: "Git Bash Required"

**Symptoms:** Claude Code requires git-bash error

**Solutions:**
1. Install [Git for Windows](https://git-scm.com/downloads/win)
2. Set path explicitly in PowerShell:
   ```powershell
   $env:CLAUDE_CODE_GIT_BASH_PATH="C:\Program Files\Git\bin\bash.exe"
   ```
3. Or add to system environment variables permanently

### WSL Installation Issues

**Platform detection errors:**
```bash
npm config set os linux
npm install -g @anthropic-ai/claude-code --force --no-os-check
```

**Node not found (using Windows npm):**
```bash
# Verify paths point to Linux (/usr/) not Windows (/mnt/c/)
which npm
which node

# If Windows, install via nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
```

**nvm version conflicts:**
Add to `~/.bashrc` or `~/.zshrc`:
```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
```

---

## Network Issues

### Firewall/VPN Blocking

**Symptoms:** Connection timeouts, API errors

**Solutions:**
1. Temporarily disable VPN
2. Check firewall settings - allow connections to Claude API
3. Test connection: `claude "test connection"`

### Proxy Issues

**Symptoms:** Connection fails through corporate proxy

**Solutions:**
1. Use HTTP proxy only (SOCKS5 not supported):
   ```bash
   export HTTP_PROXY="http://proxy:port"
   export HTTPS_PROXY="http://proxy:port"
   ```
2. Unset problematic proxy vars:
   ```bash
   unset ALL_PROXY
   ```

### Service Outages

**Check:** [status.anthropic.com](https://status.anthropic.com)

---

## Performance Issues

### High CPU/Memory Usage

**Solutions:**
1. Use `/compact` regularly to reduce context
2. Close and restart between major tasks
3. Add large build directories to `.gitignore`
4. Use Plan mode (`Shift+Tab`) for read-only exploration

### Command Hangs/Freezes

**Solutions:**
1. Press `Ctrl+C` to cancel
2. If unresponsive, close terminal and restart
3. Check for large context (use `/compact`)

### Slow Search Results (WSL)

**Symptoms:** Fewer results than expected, slow file operations

**Solutions:**
1. Move project to Linux filesystem (`/home/`) not Windows (`/mnt/c/`)
2. Be more specific with searches
3. Consider native Windows instead of WSL

### Search/Discovery Not Working

**Symptoms:** @file mentions, custom agents, skills not working

**Solution:** Install system ripgrep:
```bash
# macOS
brew install ripgrep

# Ubuntu/Debian
sudo apt install ripgrep

# Windows
winget install BurntSushi.ripgrep.MSVC
```

Then set: `export USE_BUILTIN_RIPGREP=0`

---

## IDE Integration Issues

### JetBrains Not Detected (WSL2)

**Option 1: Configure Firewall**
```bash
# Get WSL IP
wsl hostname -I

# In PowerShell (Admin):
New-NetFirewallRule -DisplayName "Allow WSL2" -Direction Inbound -Protocol TCP -Action Allow -RemoteAddress 172.21.0.0/16
```

**Option 2: Mirrored Networking**
Add to `.wslconfig` (Windows user directory):
```ini
[wsl2]
networkingMode=mirrored
```
Then: `wsl --shutdown`

### Escape Key Not Working (JetBrains)

Settings → Tools → Terminal → Uncheck "Move focus to editor with Escape"

---

## Context Management

### Context Fills Too Fast

**Solutions:**
1. Use `/clear` between unrelated tasks
2. Use `/compact` to compress context
3. Use Plan mode for exploration
4. Delegate verbose operations to subagents

### Lost Session Context

**Solutions:**
1. Create `HANDOFF.md` for session continuity
2. Use claude-mem for persistent memory
3. Use `claude -c` to continue previous session

---

## Configuration Issues

### Reset All Settings

```bash
# Reset user settings
rm ~/.claude.json
rm -rf ~/.claude/

# Reset project settings
rm -rf .claude/
rm .mcp.json
```

### Config File Locations

| File | Purpose |
|------|---------|
| `~/.claude/settings.json` | User settings |
| `.claude/settings.json` | Project settings (committed) |
| `.claude/settings.local.json` | Local project settings |
| `~/.claude.json` | Global state (theme, OAuth) |
| `.mcp.json` | Project MCP servers |

---

## Diagnostic Commands

```bash
# Check installation health
claude doctor

# Check version
claude --version

# Verbose debugging
claude --verbose --debug

# Report bug to Anthropic
/bug
```

---

## Getting More Help

1. **Built-in bug report:** `/bug` command in Claude Code
2. **GitHub issues:** [github.com/anthropics/claude-code](https://github.com/anthropics/claude-code)
3. **Ask Claude:** Claude has built-in access to its documentation
4. **Status page:** [status.anthropic.com](https://status.anthropic.com)

---

## Quick Fixes Checklist

- [ ] Node.js 18+? (`node --version`)
- [ ] Claude in PATH? (`which claude`)
- [ ] Auth valid? (`claude config`)
- [ ] Network working? (check VPN/firewall)
- [ ] Context bloated? (`/compact` or `/clear`)
- [ ] Latest version? (`claude doctor`)
