# Rotate OpenRouter Key

Safely rotate the OpenRouter API key across an entire OpenClaw installation.

## The Problem

OpenClaw stores the OpenRouter API key in up to three locations with a priority chain (`.env` > agent config > global config). Missing any one during rotation causes silent auth failures that are hard to diagnose.

## What It Does

1. Scans all config files to find every location where the key is stored
2. Reports the priority chain so you know which source actually controls the key
3. Updates all locations with the new key (with timestamped backups)
4. Restarts the gateway
5. Verifies the new key works against the OpenRouter API

## Install

```bash
clawhub install rotate-openrouter-key
```

Or copy the skill directory into your OpenClaw workspace `skills/` folder.

## Usage

Ask your agent:
- "Rotate my openrouter key"
- "Change my openrouter api key"
- "I'm getting 401 errors from openrouter"

### Script (standalone)

```bash
# Find where keys are stored
python3 scripts/update-openrouter-key.py --find

# Preview changes
python3 scripts/update-openrouter-key.py --key "sk-or-v1-NEW-KEY" --dry-run

# Update all locations
python3 scripts/update-openrouter-key.py --key "sk-or-v1-NEW-KEY"

# Verify key is valid
python3 scripts/update-openrouter-key.py --key "sk-or-v1-NEW-KEY" --verify
```

## Requirements

- OpenClaw installation (`~/.openclaw/`)
- Python 3.6+
- Internet access (for key verification)

## Key Priority Chain

| Priority | Source | Path |
|----------|--------|------|
| 1 (highest) | Environment / .env | `~/.openclaw/.env` |
| 2 | Agent config | `~/.openclaw/agents/<name>/agent/models.json` |
| 3 (lowest) | Global config | `~/.openclaw/openclaw.json` |

The highest-priority source wins. The skill updates all locations to prevent silent override issues.

## Reference

See `references/key-rotation-guide.md` for the complete guide covering corner cases, remote hosts, and troubleshooting.

## Future Work

- Support rotating keys for other providers (Anthropic, OpenAI)
- Auto-detect remote OpenClaw hosts and update via SSH
