# Security Policy

## Overview

ClawBrain is a personal AI memory system that handles sensitive data including encrypted secrets, API keys, and user preferences. This document explains our security model, what permissions are required, and how to use ClawBrain safely.

## Security Model

### What ClawBrain Does

1. **Stores Memories**: Conversations, preferences, and learning insights in SQLite or PostgreSQL
2. **Manages Encryption Keys**: Generates and stores a Fernet encryption key for securing sensitive data
3. **Installs Hooks**: Adds startup hooks to ClawdBot/OpenClaw for automatic memory refresh
4. **Optional Network Access**: Connects to PostgreSQL/Redis if configured (disabled by default)

### What ClawBrain Does NOT Do

- **No Telemetry**: Does not phone home or send usage data anywhere
- **No External APIs**: Does not make network calls except to configured PostgreSQL/Redis backends
- **No Code Execution**: Does not download or execute remote code after installation

### No Sudo Required (Core Installation)

**Core installation and operation never require root privileges:**

✅ **Without sudo**:
- `pip install clawbrain[all]` - Package installation
- `clawbrain setup` - Generates key, installs hooks to `~/.openclaw/hooks`
- All operations in user's home directory
- Default SQLite storage
- Auto-generated encryption key at `~/.config/clawbrain/.brain_key`

⚠️ **Sudo only needed for optional systemd configuration**:
- Setting environment variables via systemd drop-ins (`/etc/systemd/system/`)
- **Alternative**: Use shell environment variables instead (no sudo)
- **Not required**: ClawBrain works with zero configuration

**If you see sudo in documentation, it's only for optional systemd env var configuration, not core functionality.**

## Installation Security

### Verified Installation Methods

We recommend these installation methods in order of security:

1. **PyPI (Recommended)**
   ```bash
   pip install clawbrain[all]
   clawbrain setup
   ```
   - Downloads from official PyPI with checksums
   - No shell script execution
   - Standard Python package installation
   - CLI-based setup (no bash scripts)

2. **Git Clone (Auditable)**
   ```bash
   git clone https://github.com/clawcolab/clawbrain.git
   cd clawbrain
   pip install -e .[all]
   clawbrain setup
   ```
   - Full source code available for review
   - No remote downloads during install
   - Same CLI-based setup as PyPI

### What `clawbrain setup` Does

The `clawbrain setup` command performs these actions:
1. Detects your platform (OpenClaw or ClawdBot)
2. Generates encryption key at `~/.config/clawbrain/.brain_key`
3. Copies hook files to `~/.openclaw/hooks` or `~/.clawdbot/hooks`
4. Tests the installation with a health check
5. **Does NOT**:
   - Require sudo or root access
   - Modify system files outside your home directory
   - Download additional code from the internet
   - Execute shell commands or privileged operations

## Key Management

### Encryption Key Storage

- **Location**: `~/.config/clawbrain/.brain_key`
- **Format**: Fernet encryption key (44 bytes, base64-encoded)
- **Permissions**: Should be readable only by your user (chmod 600)
- **Auto-generated**: Created on first use if not present

### CLI Key Commands

The CLI provides commands to manage your encryption key:

```bash
clawbrain show-key          # Shows masked key (safe)
clawbrain show-key --full   # Shows full key (⚠️  SENSITIVE!)
clawbrain backup-key --all  # Backup key to file/QR/clipboard
```

⚠️ **SECURITY WARNING**: The `show-key --full` command displays your complete encryption key. This is intentional for backup purposes, but:
- Only run this command when you need to backup/migrate keys
- Never share your key in screenshots, logs, or public channels
- Treat your encryption key like a password
- If compromised, generate a new key and re-encrypt your data

### Key Backup Best Practices

1. **Immediately after setup**:
   ```bash
   clawbrain backup-key --file ~/clawbrain-key-backup.txt
   ```
   Store this file in a secure location (password manager, encrypted drive)

2. **For offline backup**:
   ```bash
   clawbrain backup-key --qr
   ```
   Print or save the QR code in a secure physical location

3. **Never**:
   - Commit `.brain_key` to git (already in `.gitignore`)
   - Share your key over unencrypted channels
   - Store your key in the same database as encrypted data

## Permissions Required

### File System Access

- **Read**: Configuration files, hooks directory, database files
- **Write**:
  - `~/.config/clawbrain/` (config and key storage)
  - `~/.openclaw/hooks/` or `~/.clawdbot/hooks/` (hook installation)
  - `./brain_data.db` or custom path (SQLite database)

### Network Access (Optional)

ClawBrain only makes network connections if you explicitly configure them:

- **PostgreSQL**: Only if `BRAIN_POSTGRES_HOST` is set
- **Redis**: Only if `BRAIN_REDIS_HOST` is set
- **No other network access**: No telemetry, no external APIs, no updates

### Environment Variables

ClawBrain reads these environment variables (**all optional** - works with zero config):

| Variable | Purpose | Default | Sensitive? |
|----------|---------|---------|------------|
| `BRAIN_AGENT_ID` | Agent identifier | `default` | No |
| `BRAIN_ENCRYPTION_KEY` | Override auto-generated key | Auto-generated | **YES** |
| `BRAIN_POSTGRES_HOST` | PostgreSQL host | None (SQLite used) | No |
| `BRAIN_POSTGRES_PASSWORD` | PostgreSQL password | None | **YES** |
| `BRAIN_REDIS_HOST` | Redis host | None | No |

**How to Set** (choose one):
1. **Shell environment** (no sudo): Add to `~/.bashrc` or `~/.zshrc`
2. **Systemd drop-in** (requires sudo): Create `/etc/systemd/system/{service}.service.d/brain.conf`
3. **Don't set anything**: ClawBrain works with defaults (SQLite + auto-generated key)

## Startup Hooks

### What the Hook Does

On `gateway:startup` event:
1. Calls `Brain.refresh_on_startup(agent_id)` via Python bridge
2. Loads memories and personality for the configured agent
3. Logs startup context to ClawdBot/OpenClaw

On `command:new` event:
1. Saves current session summary to memory
2. Clears session state

### Hook Code Location

- Source: `hooks/clawbrain-startup/handler.js`
- Installed to: `~/.openclaw/hooks/clawbrain-startup/` or `~/.clawdbot/hooks/clawbrain-startup/`
- **Review before installing**: The hook code is ~50 lines and fully auditable

### Disabling Hooks

If you want to use ClawBrain without automatic startup:

```bash
# Remove the hook
rm -rf ~/.openclaw/hooks/clawbrain-startup

# Or disable events in skill.json
# Set "events": [] instead of ["gateway:startup", "command:new"]
```

ClawBrain will still work via direct API calls in Python.

## Data Storage

### SQLite (Default)

- **Location**: `./brain_data.db` (current directory) or `$CLAWBRAIN_DB_PATH`
- **Encryption**: Secrets encrypted with Fernet, rest in plaintext SQLite
- **Permissions**: Should be readable only by your user
- **Backup**: Standard SQLite backup procedures

### PostgreSQL (Optional)

- **Connection**: Via `BRAIN_POSTGRES_HOST` environment variable
- **Encryption**: Same as SQLite (Fernet for secrets, database-level encryption optional)
- **Network**: Connections use standard PostgreSQL protocol (can use SSL/TLS)

### What's Stored

| Table | Contents | Encrypted? |
|-------|----------|------------|
| `memories` | Conversation history, facts | **Only if `memory_type='secret'`** |
| `user_profiles` | User preferences, interests | No |
| `souls` | Personality traits | No |
| `learning_insights` | Learning patterns | No |
| `conversations` | Session state | No |

## Threat Model

### What ClawBrain Protects Against

✅ **Encrypted at Rest**: Secrets in database are Fernet-encrypted
✅ **Local-Only by Default**: No network access unless configured
✅ **No Code Execution**: Cannot execute arbitrary code from memory
✅ **User Isolation**: Each agent has separate memory space

### What ClawBrain Does NOT Protect Against

❌ **Root Access**: If attacker has root, they can read the key file
❌ **Memory Dumps**: Decrypted secrets exist in RAM during use
❌ **Database Access**: If attacker can read DB and key file, they can decrypt
❌ **Compromised Python Environment**: Malicious code can access Brain API

### Recommendations for High-Security Deployments

1. **System Hardening**:
   - Run ClawdBot/OpenClaw as dedicated user with minimal privileges
   - Use full disk encryption (LUKS, FileVault, BitLocker)
   - Restrict file permissions: `chmod 600 ~/.config/clawbrain/.brain_key`

2. **Network Isolation**:
   - Run PostgreSQL on localhost or private network
   - Use TLS for PostgreSQL connections
   - Firewall Redis to localhost only

3. **Key Management**:
   - Consider external key management (Vault, KMS)
   - Rotate encryption keys periodically
   - Never commit keys to version control

4. **Monitoring**:
   - Log access to encryption key file
   - Monitor for unusual database access patterns
   - Alert on hook modifications

## Vulnerability Reporting

If you discover a security vulnerability in ClawBrain:

1. **DO NOT** open a public GitHub issue
2. Email: security@clawcolab.com (if available) or use GitHub Security Advisories
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will acknowledge within 48 hours and provide a fix timeline.

## Security Checklist for Users

Before using ClawBrain in production:

- [ ] Review install.sh and hook code before installation
- [ ] Verify package checksums from PyPI
- [ ] Backup encryption key to secure offline storage
- [ ] Set file permissions: `chmod 600 ~/.config/clawbrain/.brain_key`
- [ ] Use systemd drop-ins for environment variables (not shell rc files)
- [ ] Review what data will be stored (see Data Storage section)
- [ ] Test in isolated environment first
- [ ] Understand that CLI can display full encryption key
- [ ] Configure PostgreSQL/Redis with TLS if using over network
- [ ] Document your key backup and recovery procedure

## Comparison to OpenClaw Scanner Warnings

### "No required environment variables"

✅ **Correct**: All env vars are optional. ClawBrain works with zero configuration (SQLite + auto-generated key).

### "CLI can display full encryption key"

✅ **Correct and Intentional**: `clawbrain show-key --full` is for backup/recovery. Users should understand this is sensitive and treat it like a password.

### "Installs startup hooks"

✅ **Correct**: Required for automatic memory refresh. Hook code is auditable and can be disabled.

### "Registry metadata mismatch"

✅ **Fixed**: skill.json now declares all optional env vars and includes explicit security metadata.

### "Remote install script"

⚠️ **Warning Valid**: `remote-install.sh` downloads code from GitHub. We recommend pip or git clone for production. Remote install includes security warnings and confirmation prompts.

## Conclusion

ClawBrain is designed for personal AI memory with reasonable security defaults:
- Local-only storage by default
- Encryption for sensitive data
- No telemetry or external calls
- Auditable installation

However, it requires certain privileges (file access, hooks, key management) to function. Users should:
1. Review code before installation
2. Understand what permissions are granted
3. Follow security best practices for key management
4. Use appropriate isolation for production deployments

For questions or concerns, see our GitHub Issues or contact the maintainers.
