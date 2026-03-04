# Auto-Fix Capabilities

Complete reference for automated error fixes in OpenClaw Doctor Pro.

## Fix Safety Levels

| Safety Level | Description | User Confirmation | Rollback Available |
|--------------|-------------|-------------------|-------------------|
| **Safe** | No risk, fully reversible | No | Yes |
| **Moderate** | Low risk, config changes only | Optional | Yes |
| **Risky** | Potential data impact | Required | Partial |
| **Manual** | Cannot auto-fix, guidance provided | N/A | N/A |

## Auto-Fix Recipes

### Authentication Errors

| Error | Fix Recipe | Safety | What It Does |
|-------|-----------|--------|--------------|
| 401 | Set API key from env | Safe | Reads API key from .env and sets in config |
| INVALID_API_KEY | Validate and prompt | Moderate | Validates format, prompts for new key if invalid |
| TOKEN_EXPIRED | Refresh token | Safe | Calls auth refresh endpoint |
| MISSING_ENV_VAR | Template .env file | Moderate | Creates .env from .env.example |
| GATEWAY_TOKEN_MISMATCH | Regenerate token | Risky | Generates new token, updates all channels |

**Commands:**
```bash
# Auto-fix auth errors
python3 scripts/error-fixer.py --error 401 --auto-fix
python3 scripts/error-fixer.py --category authentication --auto-fix

# With confirmation
python3 scripts/error-fixer.py --error GATEWAY_TOKEN_MISMATCH --auto-fix --confirm
```

---

### Rate Limiting Errors

| Error | Fix Recipe | Safety | What It Does |
|-------|-----------|--------|--------------|
| 429 | Enable retry strategy | Safe | Adds exponential backoff config |
| QUOTA_EXCEEDED | Enable fallback provider | Moderate | Switches to alternate provider |
| PROVIDER_THROTTLE | Reduce request rate | Safe | Lowers RPM in config |
| CONCURRENT_LIMIT | Reduce concurrency | Safe | Lowers max concurrent requests |
| BURST_LIMIT | Add burst protection | Safe | Enables rate limiting per second |

**Commands:**
```bash
# Auto-fix rate limits
python3 scripts/error-fixer.py --error 429 --auto-fix

# Apply recommended config
python3 scripts/error-fixer.py --error QUOTA_EXCEEDED --apply-recommended
```

**What Gets Changed:**
```yaml
# Before
ai:
  retryStrategy:
    enabled: false

# After (429 fix)
ai:
  retryStrategy:
    enabled: true
    maxRetries: 3
    backoffMs: 1000
    backoffMultiplier: 2
    jitter: true
```

---

### Gateway Errors

| Error | Fix Recipe | Safety | What It Does |
|-------|-----------|--------|--------------|
| 502 | Restart gateway | Safe | Executes `openclaw restart` |
| EADDRINUSE | Kill process on port | Moderate | Finds and kills process using port 18789 |
| ECONNREFUSED | Fix binding + restart | Moderate | Sets host to 0.0.0.0, restarts gateway |
| NETWORK_TIMEOUT | Increase timeouts | Safe | Raises timeout values in config |
| DNS_RESOLUTION | Set public DNS | Moderate | Configures 8.8.8.8 and 1.1.1.1 |

**Commands:**
```bash
# Auto-fix port conflict
python3 scripts/error-fixer.py --error EADDRINUSE --auto-fix

# Dry-run (show what would change)
python3 scripts/error-fixer.py --error ECONNREFUSED --auto-fix --dry-run
```

**EADDRINUSE Fix Process:**
```bash
# Step 1: Detect process
lsof -t -i:18789

# Step 2: Attempt graceful shutdown
kill -15 <PID>
sleep 2

# Step 3: Force kill if needed
kill -9 <PID>

# Step 4: Verify port free
lsof -i:18789 || echo "Port available"

# Step 5: Start gateway
openclaw start
```

---

### Channel Errors

| Error | Fix Recipe | Safety | What It Does |
|-------|-----------|--------|--------------|
| WHATSAPP_NOT_LINKED | Initiate linking | Manual | Guides through QR code linking |
| TELEGRAM_WEBHOOK_FAIL | Re-set webhook | Moderate | Calls Telegram API to set webhook |
| DISCORD_INVALID_PERMS | Generate invite URL | Safe | Creates invite with correct permissions |
| SLACK_BOLT_ERROR | Refresh tokens | Moderate | Regenerates OAuth tokens |
| SIGNAL_CLI_MISSING | Install Signal CLI | Risky | Downloads and installs Signal CLI binary |

**Commands:**
```bash
# Auto-fix Telegram webhook
python3 scripts/error-fixer.py --error TELEGRAM_WEBHOOK_FAIL --auto-fix

# Install Signal CLI
python3 scripts/error-fixer.py --error SIGNAL_CLI_MISSING --auto-fix --confirm
```

**SIGNAL_CLI_MISSING Fix Process:**
```bash
# Step 1: Detect OS
OS=$(uname -s)

# Step 2: Download binary
wget https://github.com/AsamK/signal-cli/releases/download/v0.11.11/signal-cli-0.11.11-Linux.tar.gz

# Step 3: Extract
tar xf signal-cli-*.tar.gz -C /opt

# Step 4: Symlink
sudo ln -sf /opt/signal-cli-*/bin/signal-cli /usr/local/bin/

# Step 5: Verify
signal-cli --version

# Step 6: Update config
openclaw config set channels.signal.cliPath "/usr/local/bin/signal-cli"
```

---

### Sandbox Errors

| Error | Fix Recipe | Safety | What It Does |
|-------|-----------|--------|--------------|
| DOCKER_NOT_RUNNING | Start Docker daemon | Risky | Executes `systemctl start docker` |
| CONTAINER_OOM | Increase memory limit | Safe | Raises memory limit to 2GB |
| SANDBOX_TIMEOUT | Increase timeout | Safe | Raises execution timeout to 5 minutes |
| WORKSPACE_MOUNT_FAIL | Create workspace dir | Moderate | Creates and sets permissions on workspace |
| PERMISSION_DENIED | Fix ownership | Moderate | Chowns workspace to UID 1000 |

**Commands:**
```bash
# Auto-fix memory issues
python3 scripts/error-fixer.py --error CONTAINER_OOM --auto-fix

# Fix workspace permissions
python3 scripts/error-fixer.py --error WORKSPACE_MOUNT_FAIL --auto-fix
```

**CONTAINER_OOM Fix Changes:**
```yaml
# Before
sandbox:
  memory:
    limit: "512MB"

# After
sandbox:
  memory:
    limit: "2GB"
    swap: "4GB"
  monitoring:
    memory:
      enabled: true
      alertThreshold: 85
```

---

### Configuration Errors

| Error | Fix Recipe | Safety | What It Does |
|-------|-----------|--------|--------------|
| CONFIG_SCHEMA_INVALID | Auto-correct schema | Safe | Fixes common YAML/JSON syntax errors |
| MISSING_REQUIRED_FIELD | Add with defaults | Safe | Adds missing fields with default values |
| INVALID_VALUE_TYPE | Convert types | Safe | Converts strings to numbers, booleans, etc. |
| DEPRECATED_KEY | Migrate config | Safe | Renames deprecated keys to new format |
| CONFIG_PARSE_ERROR | Restore backup | Moderate | Restores last known good config |

**Commands:**
```bash
# Auto-fix config issues
python3 scripts/error-fixer.py --error CONFIG_SCHEMA_INVALID --auto-fix

# Migrate deprecated keys
python3 scripts/error-fixer.py --error DEPRECATED_KEY --auto-fix
```

**Type Conversion Examples:**
```yaml
# Before (INVALID_VALUE_TYPE)
gateway:
  port: "18789"           # String
  cors:
    enabled: "true"       # String

# After (auto-fixed)
gateway:
  port: 18789             # Number
  cors:
    enabled: true         # Boolean
```

---

### Installation Errors

| Error | Fix Recipe | Safety | What It Does |
|-------|-----------|--------|--------------|
| NODE_VERSION_OLD | Guide NVM install | Manual | Provides installation commands |
| PNPM_NOT_FOUND | Install pnpm | Moderate | Runs `npm install -g pnpm` |
| NPM_INSTALL_FAILED | Clear cache + retry | Moderate | Clears npm cache, retries install |
| PATH_NOT_SET | Add to PATH | Moderate | Adds npm bin to shell profile |
| DEPENDENCY_CONFLICT | Use legacy peer deps | Safe | Retries with `--legacy-peer-deps` |

**Commands:**
```bash
# Auto-fix pnpm missing
python3 scripts/error-fixer.py --error PNPM_NOT_FOUND --auto-fix

# Fix PATH
python3 scripts/error-fixer.py --error PATH_NOT_SET --auto-fix
```

**PATH_NOT_SET Fix Process:**
```bash
# Step 1: Detect shell
SHELL_NAME=$(basename "$SHELL")

# Step 2: Get npm bin path
NPM_BIN=$(npm bin -g)

# Step 3: Add to profile
if [ "$SHELL_NAME" = "bash" ]; then
  echo 'export PATH="'$NPM_BIN':$PATH"' >> ~/.bashrc
  source ~/.bashrc
elif [ "$SHELL_NAME" = "zsh" ]; then
  echo 'export PATH="'$NPM_BIN':$PATH"' >> ~/.zshrc
  source ~/.zshrc
fi

# Step 4: Verify
which openclaw
```

---

## Batch Auto-Fix

### Fix All Safe Issues
```bash
# Auto-fix everything marked as "Safe"
python3 scripts/error-fixer.py --fix-all-safe

# Expected output:
# ✓ Fixed: SANDBOX_TIMEOUT (increased to 300s)
# ✓ Fixed: INVALID_VALUE_TYPE (converted 3 fields)
# ✓ Fixed: DEPRECATED_KEY (migrated 5 keys)
# ⚠ Skipped: GATEWAY_TOKEN_MISMATCH (requires confirmation)
# ⚠ Skipped: DOCKER_NOT_RUNNING (risky operation)
```

### Fix by Category
```bash
# Fix all authentication issues
python3 scripts/error-fixer.py --category authentication --auto-fix-safe

# Fix all configuration issues
python3 scripts/error-fixer.py --category configuration --auto-fix-safe

# Fix all sandbox issues
python3 scripts/error-fixer.py --category sandbox --auto-fix-safe
```

### Fix with Confirmation
```bash
# Fix moderate-risk items with prompts
python3 scripts/error-fixer.py --auto-fix-moderate --interactive

# Example interaction:
# ? Fix EADDRINUSE by killing process 12345? (y/N): y
# ✓ Killed process 12345
# ✓ Port 18789 now available
# ? Fix WORKSPACE_MOUNT_FAIL by creating directory? (y/N): y
# ✓ Created /home/user/.openclaw/workspace
# ✓ Set permissions to 755
```

## Rollback Support

### Automatic Backups
```bash
# All fixes create backups
python3 scripts/error-fixer.py --error CONFIG_SCHEMA_INVALID --auto-fix

# Backup created at:
# ~/.openclaw/backups/config-20260208-075230.yaml
```

### Manual Rollback
```bash
# List backups
python3 scripts/error-fixer.py --list-backups

# Rollback to specific backup
python3 scripts/error-fixer.py --rollback config-20260208-075230

# Rollback last fix
python3 scripts/error-fixer.py --undo-last
```

## Fix Logging

### View Fix History
```bash
# Show all fixes applied
python3 scripts/error-fixer.py --history

# Example output:
# 2026-02-08 07:52:30 - Fixed: CONTAINER_OOM
#   Changed: sandbox.memory.limit "512MB" → "2GB"
#   Backup: backups/config-20260208-075230.yaml
#
# 2026-02-08 07:45:15 - Fixed: DEPRECATED_KEY
#   Migrated: ai.openai.key → ai.providers.openai.apiKey
#   Backup: backups/config-20260208-074515.yaml
```

## Custom Fix Recipes

### Create Custom Fix
```yaml
# custom-fixes.yaml
fixes:
  - error: CUSTOM_ERROR
    safety: moderate
    description: "Fix my custom error"
    steps:
      - action: config_set
        key: my.custom.setting
        value: "fixed"
      - action: restart
        service: gateway
```

### Load Custom Fixes
```bash
python3 scripts/error-fixer.py --load-recipes custom-fixes.yaml
```

## Safety Guardrails

### What Can Be Auto-Fixed
- ✓ Configuration changes
- ✓ Restarting services
- ✓ Installing packages (with confirmation)
- ✓ Fixing file permissions (with confirmation)
- ✓ Clearing caches

### What Cannot Be Auto-Fixed
- ✗ Modifying .env secrets
- ✗ Changing firewall rules
- ✗ Editing system files
- ✗ Account-level changes (billing, quotas)
- ✗ Data deletion

### Confirmation Required For
- ⚠ Killing processes
- ⚠ Installing system packages
- ⚠ Modifying file permissions
- ⚠ Regenerating tokens
- ⚠ Starting/stopping Docker

## Best Practices

1. **Always dry-run first**: Use `--dry-run` to preview changes
2. **Review backups**: Check backup before rollback
3. **Fix incrementally**: Don't batch-fix everything at once
4. **Test after fixing**: Run `openclaw doctor` after fixes
5. **Keep history**: Don't clear fix history logs
6. **Use safe fixes**: Only use `--auto-fix-safe` in automation
7. **Confirm risky**: Always review risky operations manually

## Related Files

- [Error Catalog](error-catalog.md) - All errors and fix availability
- [Diagnostic Commands](diagnostic-commands.md) - Manual fix commands
- [Troubleshooting Workflow](troubleshooting-workflow.md) - When to auto-fix vs manual
