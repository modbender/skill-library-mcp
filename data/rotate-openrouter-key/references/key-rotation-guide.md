# Changing OpenRouter API Key for an Existing OpenClaw Installation

When you rotate, replace, or update your OpenRouter API key, there are multiple places it can live in an OpenClaw installation. Missing any one of them causes silent failover failures or 401 errors that are hard to diagnose.

## Where the Key Lives

OpenClaw can read the OpenRouter API key from **three sources**, in this priority order:

| Priority | Source | Path | Scope |
|----------|--------|------|-------|
| 1 (highest) | **Environment / .env** | `~/.openclaw/.env` | Overrides everything |
| 2 | **Agent config** | `~/.openclaw/agents/<name>/agent/models.json` | Per-agent override |
| 3 (lowest) | **Global config** | `~/.openclaw/openclaw.json` | Shared across all agents |

**The highest-priority source wins.** If `.env` has an active `OPENROUTER_API_KEY`, it overrides both JSON files. If not set in `.env`, the agent config wins over the global config. You must update the key at whichever level it is actually being read from -- updating a lower-priority file has no effect if a higher-priority one still has the old key.

### How to Find All Key Locations

```bash
# Find every file containing an OpenRouter key
grep -r "sk-or-v1" ~/.openclaw/ --include="*.json" -l
```

This will show exactly which files need updating. Common results:

```
~/.openclaw/openclaw.json
~/.openclaw/agents/main/agent/models.json
```

Multi-agent setups may have additional agent directories:

```
~/.openclaw/agents/research/agent/models.json
~/.openclaw/agents/writer/agent/models.json
```

**Every file listed must be updated.**

## Step-by-Step: Replace the Key

### 1. Get Your New Key

Generate a new key at [openrouter.ai/keys](https://openrouter.ai/keys). Copy it. It starts with `sk-or-v1-...`.

### 2. Find All Config Files with the Old Key

```bash
grep -r "sk-or-v1" ~/.openclaw/ --include="*.json" -l
```

### 3. Update Each File

For each file found, update only the `apiKey` field under the openrouter provider:

```bash
# Update global config
python3 -c "
import json, os
p = os.path.expanduser('~/.openclaw/openclaw.json')
c = json.load(open(p))
c['models']['providers']['openrouter']['apiKey'] = 'sk-or-v1-YOUR-NEW-KEY'
json.dump(c, open(p, 'w'), indent=2)
print('Updated:', p)
"

# Update agent config (repeat for each agent)
python3 -c "
import json, os
p = os.path.expanduser('~/.openclaw/agents/main/agent/models.json')
c = json.load(open(p))
c['providers']['openrouter']['apiKey'] = 'sk-or-v1-YOUR-NEW-KEY'
json.dump(c, open(p, 'w'), indent=2)
print('Updated:', p)
"
```

> **Do not copy entire files between installations.** Each machine may have different models, agents, or provider configs. Only change the `apiKey` value.

### 4. Restart the Gateway

```bash
openclaw gateway restart
```

### 5. Verify the Key Works

```bash
# Quick API test
curl -s https://openrouter.ai/api/v1/auth/key \
  -H "Authorization: Bearer sk-or-v1-YOUR-NEW-KEY" | python3 -m json.tool
```

Expected output includes `"is_free_tier": false` and your usage stats. If you see `"error"`, the key is invalid.

## Corner Cases

### Multiple Agents with Different Keys

Some setups use different OpenRouter keys per agent (e.g., separate billing). Each agent's `models.json` has its own `apiKey`. Update each one individually:

```bash
# List all agent configs
find ~/.openclaw/agents/*/agent/models.json -exec grep -l "openrouter" {} \;
```

### Key in Global Config but Not Agent Config

If the agent config has no `apiKey` for openrouter, it inherits from `openclaw.json`. In this case, you only need to update the global config. But verify:

```bash
python3 -c "
import json, os
p = os.path.expanduser('~/.openclaw/agents/main/agent/models.json')
c = json.load(open(p))
key = c.get('providers', {}).get('openrouter', {}).get('apiKey', 'NOT SET')
print('Agent key:', key[:12] + '...' if len(key) > 12 else key)
"
```

### Remote Machines (SSH)

If you manage OpenClaw on remote hosts (e.g., a Mac Mini, VPS), you must update keys there too:

```bash
# Find and update on remote host
ssh myhost "grep -r 'sk-or-v1' ~/.openclaw/ --include='*.json' -l"

# Update remote agent config
ssh myhost "python3 -c \"
import json, os
p = os.path.expanduser('~/.openclaw/agents/main/agent/models.json')
c = json.load(open(p))
c['providers']['openrouter']['apiKey'] = 'sk-or-v1-NEW-KEY'
json.dump(c, open(p, 'w'), indent=2)
\"" 

# Restart remote gateway
ssh myhost "openclaw gateway restart"
```

### Old Key Still Cached After Restart

OpenClaw supports hot-reload for some config changes. If the key doesn't take effect after `openclaw gateway restart`:

```bash
# Hard restart: stop then start
openclaw gateway stop
openclaw gateway start
```

If still failing, check if the gateway is supervised by launchd/systemd and respawning with stale config:

```bash
# macOS
launchctl bootout gui/$(id -u)/ai.openclaw.gateway
openclaw gateway start

# Linux (systemd)
systemctl --user restart openclaw-gateway
```

### Disabled or Expired Key

If you disable an old key before updating the config, all OpenRouter models will fail immediately. The failover cascade looks like this in the logs:

```
HTTP 401: User not found.
No available auth profile for openrouter (all in cooldown or unavailable)
```

**Always update the config first, then disable the old key.** The safe order:

1. Generate new key on openrouter.ai
2. Update all config files with the new key
3. Restart gateway
4. Verify new key works (test a message)
5. **Then** disable/delete the old key

### Environment Variable Override

If `OPENROUTER_API_KEY` is set in the shell environment, some tools (scripts, CLI) may use that instead of the config file. Check:

```bash
echo $OPENROUTER_API_KEY
```

If set, update it too:

```bash
# In your shell profile (~/.bashrc, ~/.zshrc)
export OPENROUTER_API_KEY="sk-or-v1-YOUR-NEW-KEY"
```

### Key in .env Files (Common Override Source)

OpenClaw loads `~/.openclaw/.env` at startup. If `OPENROUTER_API_KEY` is set there (even if it's also in the JSON configs), **the `.env` value takes priority**. This is the most common cause of "I updated the JSON but it still uses the old key."

```bash
# Check if .env has an active (uncommented) key
grep -v '^#' ~/.openclaw/.env 2>/dev/null | grep OPENROUTER

# If it shows a key, update it
sed -i 's|^OPENROUTER_API_KEY=.*|OPENROUTER_API_KEY=sk-or-v1-YOUR-NEW-KEY|' ~/.openclaw/.env

# Or if you prefer JSON config only, comment it out
sed -i 's|^OPENROUTER_API_KEY=|#OPENROUTER_API_KEY=|' ~/.openclaw/.env
```

Also check for `.env` files in workspace directories:

```bash
find ~/.openclaw/ -name ".env" -exec grep -l "OPENROUTER" {} \;
```

### Verifying After Key Change

After updating and restarting, send a test message through each channel (Telegram, Discord, etc.) to confirm the bot responds. Check logs for errors:

```bash
# macOS
tail -f /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log | grep -i "error\|401\|auth"

# Linux
journalctl --user -u openclaw-gateway -f | grep -i "error\|401\|auth"
```

## Quick Reference Checklist

- [ ] Generated new key on openrouter.ai/keys
- [ ] Found all config files: `grep -r "sk-or-v1" ~/.openclaw/ --include="*.json" -l`
- [ ] Updated `~/.openclaw/openclaw.json`
- [ ] Updated each `~/.openclaw/agents/*/agent/models.json`
- [ ] Updated remote hosts (if any)
- [ ] Updated `OPENROUTER_API_KEY` env var (if set)
- [ ] Updated `.env` files (if any)
- [ ] Restarted gateway: `openclaw gateway restart`
- [ ] Verified key works: `curl openrouter.ai/api/v1/auth/key`
- [ ] Tested a message through the bot
- [ ] Disabled old key on openrouter.ai (only after verifying new key works)
