# OpenClaw Hardening: Lessons Learned

**Date:** 2026-02-08  
**Source:** Real-world hardening session with OpenClaw 2026.2.6-3

## What We Learned The Hard Way

### ❌ Config Fields That DON'T Work

These fields cause `Config validation failed` errors:

```json
{
  "logging": {
    "redactSensitive": "all",  // ❌ Invalid input
    "enabled": true             // ❌ Unrecognized key
  },
  "agents": {
    "defaults": {
      "tools": {                // ❌ Unrecognized key
        "deny": ["exec", "browser", "cron", "process", "gateway"]
      },
      "sandbox": {              // ❌ Unrecognized key (in defaults)
        "mode": "all",
        "scope": "agent"
      }
    }
  }
}
```

**Why?** OpenClaw's config schema doesn't support these fields. The original hardening guide was based on assumptions, not tested reality.

### ✅ What Actually Works

1. **File Permissions** (tested, works):
   ```bash
   chmod 700 ~/.openclaw
   chmod 600 ~/.openclaw/openclaw.json
   chmod 700 ~/.openclaw/credentials
   ```

2. **Built-in Security Tools** (use these instead):
   ```bash
   openclaw doctor --fix           # Validates and fixes config
   openclaw security audit --deep  # Comprehensive security scan
   openclaw health                 # Gateway and connection health
   openclaw models status          # Auth and model status
   ```

3. **Network Security** (check with):
   ```bash
   netstat -an | grep 18789 | grep LISTEN
   # Secure: 127.0.0.1 or ::1
   # Exposed: 0.0.0.0
   ```

4. **Git Tracking** (rollback capability):
   ```bash
   cd ~/.openclaw && git init
   git add openclaw.json && git commit -m "config: baseline"
   ```

## Security Audit Results

After hardening a real installation:

```
Summary: 0 critical · 2 warn · 1 info
```

**Typical warnings (non-critical):**
- `gateway.trusted_proxies_missing` - OK if localhost-only
- `channels.discord.dm.scope_main_multiuser` - Optional session isolation
- `fs.credentials_dir.perms_readable` - Fixed with `chmod 700`

## The Reality: OpenClaw is Secure by Default

OpenClaw already provides:
- ✅ Localhost-only binding (`gateway.bind: "loopback"`)
- ✅ Token-based authentication required
- ✅ Secrets encrypted at rest
- ✅ OAuth flows with PKCE
- ✅ Session isolation
- ✅ CSRF protections
- ✅ Rate limiting

**Your job:** Verify these are working, lock down file permissions, maintain good operational security practices.

## Workflow That Works

```bash
# 1. Check network exposure
netstat -an | grep 18789 | grep LISTEN

# 2. Lock file permissions
chmod 700 ~/.openclaw
chmod 600 ~/.openclaw/openclaw.json
chmod 700 ~/.openclaw/credentials

# 3. Run security audit
openclaw security audit --deep

# 4. Fix any issues
openclaw doctor --fix

# 5. Git-track for rollback
cd ~/.openclaw && git init
git add openclaw.json && git commit -m "security: baseline config"

# 6. Verify health
openclaw health
openclaw models status
```

## Don't Waste Time On

- ❌ Manual config edits for tool restrictions (schema doesn't support)
- ❌ Manual logging config (not supported)
- ❌ Sandbox mode in defaults (not supported)
- ❌ Complex security configs (already built-in)

## Focus On

- ✅ File permissions (700/600)
- ✅ Network binding verification
- ✅ Regular security audits (`openclaw security audit --deep`)
- ✅ API key rotation (90-day cycle)
- ✅ Git-tracking config changes
- ✅ Operational security (dedicated accounts, separate machines)

## Command Reference

| Task | Command | Expected Result |
|------|---------|----------------|
| Check network | `netstat -an \| grep 18789` | 127.0.0.1 (not 0.0.0.0) |
| Validate config | `openclaw doctor --fix` | "Doctor complete." |
| Security scan | `openclaw security audit --deep` | 0 critical |
| Check health | `openclaw health` | "Discord: ok" |
| Auth status | `openclaw models status` | Lists auth providers |

## Key Insight

**Stop adding manual security configs. Start verifying built-in security.**

OpenClaw is secure by design. The hardening process is about verification and operational security, not configuration hacking.
