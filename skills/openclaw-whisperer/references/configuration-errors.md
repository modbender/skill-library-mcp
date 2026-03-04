# Configuration Errors

Complete guide to OpenClaw configuration validation and common config issues.

## Error Types

### CONFIG_SCHEMA_INVALID

**Symptoms:**
- "Configuration schema validation failed" error
- Gateway won't start
- Config file rejected
- Schema mismatch messages

**Common Causes:**
- Invalid YAML/JSON syntax
- Wrong data types
- Missing required fields
- Unknown configuration keys

**Diagnostic Commands:**
```bash
# Validate config
openclaw config validate

# Show schema
openclaw config schema

# Check syntax
yamllint ~/.openclaw/config.yaml
jsonlint ~/.openclaw/config.json

# View config with validation
openclaw config show --validate
```

**Fix:**
```bash
# Auto-fix common issues
openclaw config fix --auto

# Reset to defaults
openclaw config reset

# Merge with defaults (keeps your values)
openclaw config merge --with-defaults

# Validate specific section
openclaw config validate --section gateway
```

**Common Syntax Errors:**
```yaml
# Wrong: mixing tabs and spaces
gateway:
	port: 18789  # tab used
  host: "0.0.0.0"  # spaces used

# Correct: consistent indentation
gateway:
  port: 18789
  host: "0.0.0.0"

# Wrong: unquoted special characters
description: Hello: World

# Correct: quoted strings
description: "Hello: World"

# Wrong: invalid boolean
enabled: yes  # use true/false

# Correct: proper boolean
enabled: true
```

**Auto-Fix Available:** Yes

---

### MISSING_REQUIRED_FIELD

**Symptoms:**
- "Required field missing" error
- Config validation fails
- Gateway fails to start
- Feature doesn't work

**Required Fields:**
```yaml
# Minimum required config
gateway:
  port: 18789          # Required
  host: "0.0.0.0"      # Required

ai:
  defaultProvider: "openai"  # Required
  providers:
    openai:
      apiKey: "sk-..."       # Required if provider enabled

channels: {}  # Can be empty but must exist
```

**Diagnostic Commands:**
```bash
# List missing fields
openclaw config validate --show-missing

# Check specific section
openclaw config validate --section ai.providers.openai

# Show required fields
openclaw config schema --required-only
```

**Fix:**
```bash
# Add missing field
openclaw config set gateway.port 18789

# Set from environment variable
openclaw config set ai.openai.apiKey "${OPENAI_API_KEY}"

# Use interactive wizard
openclaw config wizard --missing-only

# Generate complete config from template
openclaw config init --template full
```

**Auto-Fix Available:** Partial (can add with default values)

---

### INVALID_VALUE_TYPE

**Symptoms:**
- "Invalid value type" error
- Type mismatch in config
- Number passed as string or vice versa
- Array expected but object provided

**Common Type Errors:**
```yaml
# Wrong: port as string
gateway:
  port: "18789"

# Correct: port as number
gateway:
  port: 18789

# Wrong: boolean as string
channels:
  whatsapp:
    enabled: "true"

# Correct: boolean as boolean
channels:
  whatsapp:
    enabled: true

# Wrong: array as single value
ai:
  providers: "openai"

# Correct: array of values
ai:
  providers: ["openai", "anthropic"]

# Wrong: object as string
sandbox:
  memory: "2GB"

# Correct: object with proper structure
sandbox:
  memory:
    limit: "2GB"
```

**Diagnostic Commands:**
```bash
# Show type errors
openclaw config validate --show-types

# Get expected type
openclaw config schema --field gateway.port

# Show example values
openclaw config examples --field ai.timeout
```

**Fix:**
```bash
# Auto-convert types
openclaw config fix --convert-types

# Set with correct type
openclaw config set gateway.port 18789 --type number
openclaw config set channels.whatsapp.enabled true --type boolean

# View and fix interactively
openclaw config edit --validate-on-save
```

**Auto-Fix Available:** Yes

---

### DEPRECATED_KEY

**Symptoms:**
- "Deprecated configuration key" warning
- Feature still works but warns
- Migration needed message

**Common Deprecated Keys:**
```yaml
# Deprecated (old v1.x format)
ai:
  openai:
    key: "sk-..."

# New (v2.x format)
ai:
  providers:
    openai:
      apiKey: "sk-..."

# Deprecated
gateway:
  apiPort: 18789

# New
gateway:
  port: 18789

# Deprecated
channels:
  telegram:
    polling: true

# New
channels:
  telegram:
    mode: "polling"
```

**Diagnostic Commands:**
```bash
# List deprecated keys
openclaw config validate --show-deprecated

# Show migration path
openclaw config migrate --dry-run

# View changelog
openclaw changelog --config-changes
```

**Fix:**
```bash
# Auto-migrate to new format
openclaw config migrate --backup

# Manually remove deprecated keys
openclaw config unset ai.openai.key
openclaw config set ai.providers.openai.apiKey "sk-..."

# Use migration wizard
openclaw config migrate --interactive
```

**Auto-Fix Available:** Yes

---

### CONFIG_PARSE_ERROR

**Symptoms:**
- "Cannot parse configuration file" error
- YAML/JSON syntax error
- Gateway won't start
- Config file corrupted

**Common Parse Errors:**
```yaml
# Missing closing quote
description: "Hello World

# Extra comma (JSON)
{"port": 18789,}

# Tab instead of spaces in YAML
gateway:
→port: 18789

# Duplicate keys
gateway:
  port: 18789
gateway:
  host: "0.0.0.0"

# Invalid character
gateway:
  port: 18789@
```

**Diagnostic Commands:**
```bash
# Parse and show errors
openclaw config parse ~/.openclaw/config.yaml

# Validate syntax only
yamllint ~/.openclaw/config.yaml

# Pretty-print to find issues
openclaw config show --format json | jq .
```

**Fix:**
```bash
# Restore from backup
openclaw config restore --from-backup

# Reset to last known good
openclaw config reset --keep-backup

# Fix syntax errors
openclaw config fix --syntax

# Edit with validation
openclaw config edit --validate-on-save

# If all else fails, start fresh
mv ~/.openclaw/config.yaml ~/.openclaw/config.yaml.broken
openclaw config init
```

**Auto-Fix Available:** No (manual syntax fixing needed)

---

### ENV_VAR_NOT_FOUND

**Symptoms:**
- "Environment variable not found" error
- Config references ${VAR} but VAR not set
- Substitution fails

**Example:**
```yaml
# Config references env var
ai:
  providers:
    openai:
      apiKey: "${OPENAI_API_KEY}"  # Error if not set
```

**Diagnostic Commands:**
```bash
# Check which env vars are referenced
openclaw config show --show-env-refs

# Validate env vars
openclaw config validate --check-env

# List missing vars
openclaw doctor --check-env
```

**Fix:**
```bash
# Set environment variable
export OPENAI_API_KEY="sk-..."

# Or add to .env file
echo "OPENAI_API_KEY=sk-..." >> .env

# Use direct value instead
openclaw config set ai.providers.openai.apiKey "sk-..." --no-env

# Set default for missing var
openclaw config set-default OPENAI_API_KEY "default-value"
```

**Auto-Fix Available:** Partial

---

## Configuration Best Practices

### File Structure
```yaml
# ~/.openclaw/config.yaml
gateway:
  port: 18789
  host: "0.0.0.0"
  cors:
    enabled: true
    origins: ["*"]

ai:
  defaultProvider: "openai"
  providers:
    openai:
      apiKey: "${OPENAI_API_KEY}"
      model: "gpt-4"
      timeout: 60000

    anthropic:
      apiKey: "${ANTHROPIC_API_KEY}"
      model: "claude-3-sonnet-20240229"

  retryStrategy:
    enabled: true
    maxRetries: 3

channels:
  whatsapp:
    enabled: true
    sessionPath: ".openclaw/whatsapp-session"

  telegram:
    enabled: true
    botToken: "${TELEGRAM_BOT_TOKEN}"
    mode: "webhook"

sandbox:
  enabled: true
  image: "python:3.11-slim"
  memory:
    limit: "2GB"
  timeout:
    execution: 300000
```

### Environment Variables (.env)
```bash
# .env file
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
TELEGRAM_BOT_TOKEN=...
DISCORD_BOT_TOKEN=...
SLACK_BOT_TOKEN=...
GATEWAY_TOKEN=...
```

### Configuration Management

```bash
# View current config
openclaw config show

# Edit config
openclaw config edit

# Set single value
openclaw config set gateway.port 18790

# Get single value
openclaw config get gateway.port

# Unset value (use default)
openclaw config unset gateway.cors.enabled

# Validate before applying
openclaw config validate

# Backup config
openclaw config backup

# Restore from backup
openclaw config restore

# Export config
openclaw config export --output config-backup.yaml

# Import config
openclaw config import --input config-backup.yaml
```

### Config Validation Workflow

```
1. Edit config file
   ↓
2. Validate syntax: openclaw config validate
   ↓
3. Check required fields: openclaw config validate --show-missing
   ↓
4. Fix type errors: openclaw config fix --convert-types
   ↓
5. Migrate deprecated: openclaw config migrate
   ↓
6. Test config: openclaw config test
   ↓
7. Apply: openclaw restart
```

### Schema Documentation

```bash
# View full schema
openclaw config schema

# Get field description
openclaw config schema --field gateway.port

# Show examples
openclaw config examples

# Export schema
openclaw config schema --format json > schema.json
```

## Common Configuration Patterns

### Multi-Provider Setup
```yaml
ai:
  defaultProvider: "openai"
  fallback:
    enabled: true
    providers: ["anthropic", "google"]

  providers:
    openai:
      apiKey: "${OPENAI_API_KEY}"
      priority: 1

    anthropic:
      apiKey: "${ANTHROPIC_API_KEY}"
      priority: 2

    google:
      apiKey: "${GOOGLE_API_KEY}"
      priority: 3
```

### High Availability Setup
```yaml
gateway:
  cluster:
    enabled: true
    instances: 3
    loadBalancing: "round-robin"

  healthCheck:
    enabled: true
    interval: 10000
    timeout: 5000
```

### Development vs Production
```yaml
# config.dev.yaml
sandbox:
  enabled: true
  network:
    enabled: true  # Allow network in dev

# config.prod.yaml
sandbox:
  enabled: true
  network:
    enabled: false  # Isolate in prod
  memory:
    limit: "4GB"    # More resources
```

```bash
# Use specific config
openclaw start --config config.prod.yaml
```

## Related Files

- [Error Catalog](error-catalog.md) - All error types
- [Authentication Errors](authentication-errors.md) - Auth config
- [Channel Errors](channel-errors.md) - Channel config
- [Sandbox Errors](sandbox-errors.md) - Sandbox config
