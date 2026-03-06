# Authentication Errors

Complete guide to diagnosing and fixing OpenClaw authentication issues.

## Error Types

### 401 Unauthorized

**Symptoms:**
- API requests return 401 status
- "Unauthorized" or "Invalid credentials" messages
- Gateway rejects AI provider requests

**Common Causes:**
- Missing API key in .env file
- Incorrect API key value
- API key not activated with provider
- Typo in environment variable name

**Diagnostic Commands:**
```bash
# Check if API keys are set
openclaw config get ai.provider.apiKey

# Verify environment variables
env | grep -i api_key

# Test provider connection
openclaw doctor --check-auth
```

**Fix:**
```bash
# Set API key via CLI
openclaw config set ai.openai.apiKey "sk-..."

# Or edit .env file
echo "OPENAI_API_KEY=sk-..." >> .env

# Restart gateway
openclaw restart
```

**Auto-Fix Available:** Yes
```bash
python3 scripts/error-fixer.py --error 401 --auto-fix
```

---

### INVALID_API_KEY

**Symptoms:**
- Error message: "API key format invalid"
- Provider returns authentication error
- Key validation fails

**Common Causes:**
- API key missing prefix (e.g., `sk-` for OpenAI)
- Extra whitespace or newlines in key
- Copy-paste truncation
- Wrong provider key used

**Diagnostic Commands:**
```bash
# Validate key format
python3 scripts/error-fixer.py --error INVALID_API_KEY --validate

# Check key length and prefix
openclaw config get ai.provider.apiKey | wc -c
```

**Fix:**
```bash
# Get new key from provider dashboard
# OpenAI: https://platform.openai.com/api-keys
# Anthropic: https://console.anthropic.com/settings/keys
# Google: https://makersuite.google.com/app/apikey

# Set correct key
openclaw config set ai.openai.apiKey "sk-proj-..."

# Clear any cached credentials
openclaw cache clear --auth
```

**Auto-Fix Available:** Yes (detects format issues)

---

### TOKEN_EXPIRED

**Symptoms:**
- "Token expired" error messages
- Authentication works initially then fails
- Intermittent 401 errors

**Common Causes:**
- Session token TTL exceeded
- Gateway token not refreshed
- Clock skew between client/server

**Diagnostic Commands:**
```bash
# Check token expiry
openclaw status --show-tokens

# Verify system time
date && curl -I https://www.google.com | grep Date
```

**Fix:**
```bash
# Refresh gateway token
openclaw auth refresh

# Or restart to get new token
openclaw restart

# Sync system time (if clock skew)
sudo ntpdate -s time.nist.gov  # Linux
```

**Auto-Fix Available:** Yes

---

### MISSING_ENV_VAR

**Symptoms:**
- Error: "Required environment variable not set"
- Config validation fails
- Provider initialization errors

**Common Causes:**
- .env file not loaded
- Variable name typo
- .env.example not copied to .env
- Running from wrong directory

**Required Variables:**
```
OPENAI_API_KEY          # For OpenAI
ANTHROPIC_API_KEY       # For Claude
GOOGLE_API_KEY          # For Gemini
GATEWAY_TOKEN           # For gateway auth
WHATSAPP_TOKEN          # For WhatsApp channel
TELEGRAM_BOT_TOKEN      # For Telegram
DISCORD_BOT_TOKEN       # For Discord
SLACK_BOT_TOKEN         # For Slack
```

**Diagnostic Commands:**
```bash
# Check which vars are missing
openclaw doctor --check-env

# List all expected vars
cat .env.example
```

**Fix:**
```bash
# Copy example and edit
cp .env.example .env
nano .env

# Or set individually
openclaw config set env.OPENAI_API_KEY "sk-..."

# Verify all required vars set
openclaw config validate
```

**Auto-Fix Available:** Partial (can template .env, user must add keys)

---

### GATEWAY_TOKEN_MISMATCH

**Symptoms:**
- Channel connections fail authentication
- Gateway rejects client requests
- "Token mismatch" error in logs

**Common Causes:**
- Different GATEWAY_TOKEN in .env vs running instance
- Gateway restarted with new token
- Multiple OpenClaw instances running
- Client using cached old token

**Diagnostic Commands:**
```bash
# Check running gateway token
openclaw status --show-gateway-token

# Compare with config
openclaw config get gateway.token

# Check for multiple instances
ps aux | grep openclaw
```

**Fix:**
```bash
# Stop all instances
killall openclaw

# Generate new token
openclaw auth generate-token

# Update all clients with new token
openclaw channels update-token

# Restart gateway
openclaw start
```

**Auto-Fix Available:** No (requires manual coordination)

---

## Prevention Best Practices

1. **Use .env file:** Don't hardcode keys in config
2. **Validate on start:** Enable `validateAuth: true` in config
3. **Rotate regularly:** Set up key rotation schedule
4. **Monitor expiry:** Use `openclaw status --watch` to track token TTL
5. **Secure storage:** Use secrets manager for production

## Quick Diagnostic Ladder

1. Run `openclaw doctor --check-auth`
2. Verify .env file exists and is loaded
3. Check API key format and prefix
4. Test provider connection directly
5. Review gateway logs: `openclaw logs --auth-only`
6. Validate system time sync
7. Clear auth cache and restart

## Related Files

- [Error Catalog](error-catalog.md) - All error types
- [Configuration Errors](configuration-errors.md) - Config issues
- [Diagnostic Commands](diagnostic-commands.md) - CLI reference
