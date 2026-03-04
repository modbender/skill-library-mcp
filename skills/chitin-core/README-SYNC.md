# ModelRouter 9001 - Provider Sync

## Overview

Automated nightly script that discovers live models from all authenticated providers and keeps the router pool current.

## Files

- **`scripts/provider-sync.js`** - Main sync script
- **`sync-report.json`** - Latest sync report with discovered/deprecated models
- **`sync.log`** - Cron output log

## What It Does

1. **Fetches live models** from all providers:
   - Anthropic API (`/v1/models`)
   - OpenAI API (`/v1/models`)
   - OpenRouter API (`/v1/models` with pricing)
   - Ollama Local (`localhost:11434`)
   - Ollama Forge (`100.118.158.58:11434`)
   - Static configs for Google, Groq, DeepSeek

2. **Cross-references** with current `config.json`:
   - Detects new models
   - Flags deprecated models
   - Identifies renamed models (fuzzy match)
   - Updates pricing from OpenRouter

3. **Updates config.json**:
   - Marks deprecated models with `"status": "deprecated"`
   - Updates pricing for OpenRouter models
   - Adds new models to `"discovered"` section (requires manual review to promote to active tiers)

4. **Generates sync report** (`sync-report.json`)

5. **Sends Telegram notification** if significant changes detected (new/deprecated/renamed models)

## Usage

### Manual Run
```bash
# Dry run (no changes)
node scripts/provider-sync.js --dry-run

# Live run (updates config)
node scripts/provider-sync.js
```

### Automated Schedule

**Cron:** Every day at 2:00 AM UTC

```cron
0 2 * * * /usr/bin/node /home/aaron/.openclaw/workspace/skills/modelrouter-9001/scripts/provider-sync.js >> sync.log 2>&1
```

## API Keys

Script loads API keys from:
1. Environment variables (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `OPENROUTER_API_KEY`)
2. Fallback: `.secrets/*.env` files

Providers without keys are skipped (won't crash).

## Telegram Notifications

- **Bot Token:** 8547915559:AAGqJlIiflFVBayXwT5GS5DsWyBTW_vlfw8
- **Chat ID:** 1156712793
- **Trigger:** New models found OR deprecated models detected OR renamed candidates

## First Run Results (2026-02-28)

✅ **All providers responded successfully**

- Anthropic: 9 models
- OpenAI: 96 models  
- OpenRouter: 343 models
- Ollama Local: 2 models
- Ollama Forge: 11 models
- Google: 2 models (static)
- Groq: 1 model (static)
- DeepSeek: 2 models (static)

### Discoveries

- **645 new models** discovered across all providers
- **0 deprecated** models (all config models still exist)
- **2 renamed candidates** detected:
  - `openai/gpt-5-mini` → `gpt-5`
  - `openai-responses/o3` → `o3-mini`

All new models added to `config.json` under `"discovered"` section for review.

### Notable Discoveries

**Anthropic:**
- claude-sonnet-4-6
- claude-opus-4-6
- claude-opus-4-5, claude-haiku-4-5, claude-sonnet-4-5 (dated releases)

**OpenAI:**
- gpt-5.2, gpt-5.2-pro, gpt-5.2-codex
- gpt-5.1, gpt-5.1-codex, gpt-5.1-codex-mini, gpt-5.1-codex-max
- o3, o3-mini, o3-pro
- gpt-4.1, gpt-4.1-mini, gpt-4.1-nano

**OpenRouter:**
- Hundreds of third-party models with pricing data
- Qwen 3 series, DeepSeek v3.2, GLM-5, Gemini 2.5/3.0

**Ollama (Forge/teseract):**
- qwen3:4b, qwen2.5:7b
- phi4-mini, phi3:mini
- llama3.2:1b, llama3.2:3b

## Next Steps

1. **Review `config.json` → `"discovered"` section**
2. **Promote worthy models** to active tiers (LIGHT/MEDIUM/HEAVY)
3. **Set pricing** for newly promoted models
4. **Test routing** with new models
5. **Archive/remove** unwanted discovered models

## Maintenance

- Check `sync-report.json` after each run
- Review Telegram notifications for significant changes
- Update tier boundaries in `config.json` if model distribution shifts
- Add new providers by extending fetch functions in `provider-sync.js`
