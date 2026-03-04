# OpenClaw Hardening Guide

Based on the AI SAFE2 framework. Focuses on proven, working security measures.

## ⚠️ IMPORTANT: OpenClaw Security Reality

**OpenClaw already has strong security defaults built-in:**
- Secure authentication required by default
- Strong account/workspace isolation
- CSRF protections for state-changing requests
- Secrets encrypted at rest
- Private-by-default networking (localhost binding)
- Secure OAuth flows (state/PKCE)

**This guide helps you verify and enhance what's already there.**

## Prerequisites

- SSH access to server running OpenClaw (or local tmux session)
- Basic command line knowledge

## Step 1: Verify Network Security (2 min)

```bash
# Check current binding
netstat -an | grep -E "8080|18789|8888" | grep LISTEN

# SECURE if you see:
# tcp4  0  0  127.0.0.1.18789  *.*  LISTEN
# tcp6  0  0  ::1.18789        *.*  LISTEN

# EXPOSED if you see:
# tcp4  0  0  0.0.0.0.18789    *.*  LISTEN  ← BAD!

# If exposed, restart bound to localhost only:
pkill -f "openclaw gateway"
openclaw gateway --bind 127.0.0.1 --port 18789

# Access via SSH tunnel from laptop:
ssh -L 18789:127.0.0.1:18789 user@server
```

**Note:** OpenClaw's default `gateway.bind: "loopback"` config already binds to localhost. Most installations are secure by default.

## Step 2: Lock File Permissions (1 min)

```bash
chmod 700 ~/.openclaw
chmod 600 ~/.openclaw/openclaw.json
chmod 600 ~/.openclaw/*.log 2>/dev/null || true
chmod 600 ~/.openclaw/.env 2>/dev/null || true
chmod 700 ~/.openclaw/credentials 2>/dev/null || true
```

**Verify:**
```bash
ls -la ~/.openclaw/ | head -5
# Should show: drwx------ for .openclaw
# Should show: -rw------- for openclaw.json
```

## Step 3: Run Security Audit (2 min)

⚠️ **SKIP manual config edits for tool restrictions.** OpenClaw's config schema doesn't support the following fields:
- ❌ `logging.redactSensitive`
- ❌ `logging.enabled`
- ❌ `agents.defaults.tools`
- ❌ `agents.defaults.sandbox`

These fields will cause config validation errors. OpenClaw has built-in security controls that work differently.

**Instead, run the built-in security tools:**

```bash
# Validate config
openclaw doctor --fix

# Run deep security audit
openclaw security audit --deep
```

**Target result:** `0 critical · 0-3 warn · 1 info`

**Common warnings (non-critical):**
- `gateway.trusted_proxies_missing` - OK if localhost-only
- `channels.discord.dm.scope_main_multiuser` - Optional session isolation
- `fs.credentials_dir.perms_readable` - Fixed by Step 2

## Step 4: Rotate Secrets (3 min)

**Use OpenClaw's built-in authentication commands (safe, no shell modification):**

1. Generate new API keys from each provider console
2. Update via OpenClaw's secure method:

```bash
# Interactive authentication (recommended)
openclaw models auth paste-token

# Or use environment variables (set these in your terminal session)
export ZAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-..."
```

3. Delete old keys from provider console

**⚠️ IMPORTANT:** Do NOT modify shell startup files (`~/.bashrc`, `~/.zshrc`) directly. Instead:
- Use OpenClaw's `openclaw models auth` command for permanent storage
- Or set environment variables in your current terminal session only

**Verify auth status:**
```bash
openclaw models status
# Check "Auth overview" section
# Look for OAuth expiration dates
```

## Step 5: Git-Track Config for Rollback (2 min)

```bash
cd ~/.openclaw

# Initialize git if not already done
git init 2>/dev/null || true

# Create .gitignore
printf 'agents/*/sessions/\nagents/*/agent/*.jsonl\n*.log\n' > .gitignore

# Commit current config
git add .gitignore openclaw.json agents/*/agent/auth-profiles.json agents/*/agent/models.json
git commit -m "security: baseline hardened config"

# View commit history for rollback
git log --oneline
```

**To rollback:**
```bash
cd ~/.openclaw
git log --oneline  # Find commit hash
git checkout <commit-hash> -- openclaw.json
openclaw doctor --fix  # Validate after rollback
```

## Step 6: Optional Backups

**⚠️ MANUAL SETUP REQUIRED:** This skill does NOT automatically set up cron jobs or modify system schedules for security reasons.

If you want automated backups, manually create a backup script and schedule it yourself:

1. Create backup script manually: `~/backup-openclaw.sh`
2. Make it executable: `chmod +x ~/backup-openclaw.sh`
3. **Manually** add to crontab using `crontab -e`

**Example backup script content** (create this yourself):
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
mkdir -p ~/backups
tar -czf ~/backups/openclaw-$DATE.tar.gz ~/.openclaw/openclaw.json ~/.openclaw/agents/
find ~/backups/ -name "openclaw-*.tar.gz" -mtime +30 -delete
```

**This skill will NOT create or schedule this for you.** You must do this manually if desired.

## Optional: Isolate Discord DM Sessions

If you have multiple users DMing your bot, add to `openclaw.json`:

```json
{
  "session": {
    "dmScope": "per-channel-peer"
  }
}
```

This prevents context leakage between different DM senders.

## Verification Checklist

After hardening, verify with:

```bash
# 1. Network security
netstat -an | grep 18789 | grep LISTEN
# Should show: 127.0.0.1 or ::1 (NOT 0.0.0.0)

# 2. File permissions
ls -la ~/.openclaw/ | head -5
# Should show: drwx------ for directory

# 3. Security audit
openclaw security audit --deep
# Target: 0 critical · 0-2 warn · 1 info

# 4. Config validity
openclaw doctor --fix
# Should complete without errors

# 5. Gateway health
openclaw health
# Should show: Discord: ok, Agents: main
```

## Safety Rules

1. **Human approval** for external comms (email, social media, purchases)
2. **Dedicated bot accounts** — never use personal credentials
3. **Separate machine** — don't run OpenClaw on your personal laptop with sensitive files
4. **Rotate keys** every 90 days minimum, immediately after any suspected compromise

## What OpenClaw Already Provides

You don't need to manually configure these - they're built-in:

✅ Secure authentication required by default  
✅ Strong account/workspace isolation across all actions  
✅ CSRF protections for state-changing requests  
✅ Strict origin checks to block cross-site attacks  
✅ WebSocket origin validation to prevent hijacking  
✅ Rate limiting and abuse prevention on sensitive endpoints  
✅ Secrets encrypted at rest  
✅ Secrets transmitted securely and never logged  
✅ Short-lived/rotating access credentials where applicable  
✅ Private-by-default networking  
✅ Tight allowlists for any browser-accessible control surfaces  
✅ Secure OAuth flows (state/PKCE) for supported providers  
✅ Security-focused HTTP headers (CSP, clickjacking, etc.)  
✅ Least-privilege runtime (non-root) for services  

**Your job:** Verify these are working, lock down file permissions, and maintain good operational security practices.
