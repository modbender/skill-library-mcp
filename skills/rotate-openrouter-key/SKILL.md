---
name: rotate-openrouter-key
description: Safely rotate the OpenRouter API key across all config files in an OpenClaw installation. Finds every location where the key is stored, updates them, restarts the gateway, and verifies the new key works. Use when asked to "rotate openrouter key", "change openrouter api key", "update openrouter key", or "replace openrouter key".
---

# Rotate OpenRouter Key

Safely replace the OpenRouter API key across an entire OpenClaw installation, handling all config locations, priority chains, and verification.

## When to Use

- User says "rotate my openrouter key" or "change openrouter key"
- User reports 401 errors from OpenRouter
- User disabled an old key and needs to set a new one
- Periodic key rotation for security

## Key Priority Chain

OpenClaw reads the OpenRouter API key from three sources, highest priority first:

1. **`~/.openclaw/.env`** — environment file, overrides everything
2. **`~/.openclaw/agents/<name>/agent/models.json`** — per-agent config
3. **`~/.openclaw/openclaw.json`** — global config

If a higher-priority source has the old key, updating a lower-priority file has no effect. **You must update the key at whichever level it is actually being read from.**

## Workflow

### Step 1: Get the New Key

Ask the user for the new key. It must start with `sk-or-v1-`.

If the user doesn't have one yet, direct them to [openrouter.ai/keys](https://openrouter.ai/keys) to generate one.

### Step 2: Find All Key Locations

```bash
# Find every file containing an OpenRouter key
grep -r "sk-or-v1" ~/.openclaw/ --include="*.json" --include=".env" -l 2>/dev/null

# Also check for uncommented key in .env
grep -v '^#' ~/.openclaw/.env 2>/dev/null | grep OPENROUTER_API_KEY
```

Report what you found to the user before making changes.

### Step 3: Update All Locations and Verify

Run the helper script — it handles both `.env` and JSON files in one pass:

```bash
python3 scripts/update-openrouter-key.py --key "sk-or-v1-NEW-KEY" --verify
```

The script:
- Finds all config files (`.env` + JSON) containing an openrouter key
- Creates timestamped backups before each write
- Updates only the key value (minimal change)
- Verifies the new key against the OpenRouter API
- Reports what it changed

Preview first with `--dry-run`:
```bash
python3 scripts/update-openrouter-key.py --key "sk-or-v1-NEW-KEY" --dry-run
```

### Step 4: Restart Gateway

```bash
openclaw gateway restart
```

### Step 5: Remote Hosts (if applicable)

If the user manages OpenClaw on other machines, repeat Steps 2-5 via SSH:

```bash
ssh <host> "grep -r 'sk-or-v1' ~/.openclaw/ --include='*.json' --include='.env' -l"
```

Then run the update script remotely or copy it over.

### Step 6: Disable Old Key

**Only after verifying the new key works everywhere**, tell the user they can now safely disable/delete the old key at [openrouter.ai/keys](https://openrouter.ai/keys).

## Scope & Boundaries

**Handles:** Finding, updating, and verifying OpenRouter API keys in all OpenClaw config locations.

**Does NOT handle:** Other provider keys (Anthropic, OpenAI). Key generation (user does that on openrouter.ai). Billing or usage issues.

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| 401 after update | Missed a config location | Re-run Step 2 to find remaining old keys |
| Key works in curl but not in bot | `.env` has old key overriding JSON | Check and update `.env` |
| Gateway won't restart | Unrelated issue | `openclaw gateway stop && openclaw gateway start` |
| Remote host still failing | Forgot to update remote configs | SSH in and repeat Steps 2-5 |

## Limitations

- Cannot generate or revoke keys (user must do that on openrouter.ai)
- Cannot update keys on remote hosts without SSH access
- Does not handle keys stored outside `~/.openclaw/` (e.g., in systemd environment files)
