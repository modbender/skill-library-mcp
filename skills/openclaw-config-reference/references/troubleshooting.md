# Troubleshooting & Recovery

Common problems, their causes, and how to fix them.

---

## Table of Contents
1. [Emergency Recovery](#emergency-recovery)
2. [Gateway Won't Start](#gateway-wont-start)
3. [Config Validation](#config-validation)
4. [Doctor Command](#doctor-command)
5. [Common Pitfalls](#common-pitfalls)
6. [Channel-Specific Issues](#channel-specific-issues)
7. [Performance Issues](#performance-issues)

---

## Emergency Recovery

If the Gateway is down and you need to get it running again:

### Step 1: Restore Backup

```bash
cp ~/.openclaw/openclaw.json.bak ~/.openclaw/openclaw.json
```

### Step 2: Run Doctor

```bash
openclaw doctor --fix
```

### Step 3: Verify Config

```bash
openclaw config get
```

### Step 4: Start Gateway

```bash
openclaw gateway
```

If no backup exists, start with a minimal config:

```bash
cat > ~/.openclaw/openclaw.json << 'EOF'
{
  gateway: { port: 18789 },
  agents: { list: [{ agentId: "main", workspace: "~/.openclaw/workspace" }] }
}
EOF
```

---

## Gateway Won't Start

### "Unknown key" Error

**Cause:** Config contains a field not in the current schema. OpenClaw uses strict validation.

**Fix:**
```bash
# Check what key is unknown (error message will say)
openclaw doctor

# Remove the offending key
openclaw config unset the.unknown.key

# Or restore backup
cp ~/.openclaw/openclaw.json.bak ~/.openclaw/openclaw.json
```

**Prevention:** Always check field names against this reference or official docs before adding them.

### "Auth required for lan binding"

**Cause:** `gateway.bind` is set to `"lan"` but no authentication is configured.

**Fix:**
```bash
# Option A: Add auth
openclaw config set gateway.auth.mode token
openclaw config set gateway.auth.token "$(openssl rand -hex 32)"

# Option B: Switch to loopback
openclaw config set gateway.bind loopback
```

### "Port already in use"

**Cause:** Another process (or another Gateway instance) is using the port.

**Fix:**
```bash
# Find what's using the port
lsof -i :18789

# Kill the process or use a different port
openclaw config set gateway.port 19000
```

### "Docker not available" (Sandbox)

**Cause:** `sandbox.mode` is set to `"all"` or `"non-main"` but Docker isn't running.

**Fix:**
```bash
# Start Docker
systemctl start docker   # Linux
open -a Docker           # macOS

# Or disable sandbox
openclaw config set sandbox.mode off
```

---

## Config Validation

### Validate JSON Syntax

```bash
# Using Python (available on most systems)
cat ~/.openclaw/openclaw.json | python3 -m json.tool

# Note: This validates JSON but not JSON5.
# For JSON5, the Gateway itself is the validator.
```

### Validate Config Schema

```bash
# The best validator is OpenClaw itself
openclaw config get

# If this succeeds, config is valid
# If it fails, it will show the exact error
```

### Common JSON Syntax Errors

- Missing comma between fields
- Trailing comma after last field (valid in JSON5 but check format)
- Mismatched braces `{ }`
- Unquoted string values that aren't valid JSON5 identifiers
- Single quotes instead of double quotes for JSON (valid in JSON5)

---

## Doctor Command

`openclaw doctor` checks your setup for common issues.

```bash
# Check for issues
openclaw doctor

# Auto-fix what can be fixed
openclaw doctor --fix

# Verbose output
openclaw doctor --verbose
```

### What Doctor Checks

- Config file syntax and schema validity
- File permissions (openclaw.json, credentials, .env)
- Required binaries in PATH
- Environment variables for configured providers
- Channel credential validity
- Gateway health (if running)
- Workspace file existence (SOUL.md, AGENTS.md)

### When to Run Doctor

- After any manual config change
- After an upgrade
- When the Gateway won't start
- When channels stop connecting
- As part of regular maintenance

---

## Common Pitfalls

### 1. Editing Config While Gateway Watches

**Problem:** The Gateway watches `openclaw.json` for changes. If it reads the file while you're mid-edit (half-written JSON), it sees invalid config and may crash or revert.

**Solution:**
- Use `openclaw config set` instead of manual editing (atomic writes)
- If editing manually, save the file quickly (don't leave it open mid-edit)
- Consider `gateway.reload: "off"` while making extensive manual changes, then re-enable

### 2. gateway.bind: "lan" Without Auth

**Problem:** Gateway refuses to start. This is a safety feature - binding to all interfaces without auth exposes your agent to the network.

**Solution:** Always set auth when using lan binding:
```json5
gateway: {
  bind: "lan",
  auth: { mode: "token", token: "strong-random-token" }
}
```

### 3. commands.config: true

**Problem:** Allows anyone who can message your bot to modify `openclaw.json` from chat. This is a major security risk in multi-user setups.

**Solution:** Only enable for single-user, trusted setups. Never combine with `open` DM policy.

### 4. tools.elevated.enabled: true + Open DM Policy

**Problem:** Gives anyone who can message your bot admin/sudo access to your system.

**Solution:** Never enable elevated tools with open DM policy. Use `pairing` or `allowlist` policies, and consider keeping elevated disabled entirely.

### 5. Missing OPENCLAW_GATEWAY_TOKEN

**Problem:** Auth mode is set to `token` but no token is provided in config or environment. Gateway may start but refuse all connections.

**Solution:**
```bash
# Set in config
openclaw config set gateway.auth.token "your-token"

# Or set as env var
echo 'OPENCLAW_GATEWAY_TOKEN=your-token' >> ~/.openclaw/.env
```

### 6. sandbox.mode: "all" Requires Docker

**Problem:** Sandbox mode requires Docker to be running. If Docker isn't available, the Gateway fails.

**Solution:** Either start Docker or set `sandbox.mode: "off"`.

### 7. Hardcoded Secrets in Config

**Problem:** API keys and tokens in `openclaw.json` are visible to anyone with file access and may accidentally be committed to git.

**Solution:** Use `~/.openclaw/.env` for secrets:
```bash
# In .env (chmod 600)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
OPENCLAW_GATEWAY_TOKEN=your-token
```

---

## Channel-Specific Issues

### WhatsApp: E.164 Format

**Problem:** Phone numbers in `allowFrom` must be E.164 format. Incorrect format means the allowlist won't match.

**Correct:** `"+15551234567"`, `"+4915012345678"`
**Wrong:** `"555-123-4567"`, `"(555) 123-4567"`, `"015012345678"`

### Discord: Message Content Intent

**Problem:** Bot receives empty messages and can't respond.

**Cause:** "Message Content Intent" is not enabled in Discord Developer Portal.

**Fix:** Go to discord.com/developers > Your Application > Bot > Privileged Gateway Intents > Toggle "Message Content Intent" ON.

### Telegram: Stream Mode Differences

**Problem:** Streaming behavior differs from expected.

- `off` - No output until complete (user sees nothing for seconds/minutes)
- `partial` - Message sent then edited as content arrives (best UX but causes notification spam on some clients)
- `block` - Shows "typing..." then sends complete message

Choose based on your use case. `partial` is generally recommended.

### Slack: Socket vs HTTP Mode

**Problem:** Slack events not arriving.

**Socket Mode:** Requires `appToken` (starts with `xapp-`). Works behind firewalls.
**HTTP Mode:** Requires public URL and `signingSecret`. Needs network access from Slack servers.

---

## Performance Issues

### High Token Usage

- Check which skills have `always: true` - each adds tokens to every conversation
- Use `openclaw skills list` to see loaded skills
- Move verbose instructions from SKILL.md to references/
- Reduce `historyLimit` in channel config

### Slow Response Times

- Check model latency with `openclaw gateway probe`
- Consider switching to a faster model for non-critical agents
- Reduce `maxConcurrent` if agents are competing for API quota
- Check if sandbox mode is adding startup overhead

### Gateway Memory Usage

- Many connected channels increase memory
- Large session histories accumulate memory
- Set `session.reset.mode: "daily"` to automatically clear old sessions
- Restart Gateway periodically if running for weeks
