---
name: add-top-openrouter-models
description: Sync OpenRouter models used by OpenClaw into this installation's config. Fetches the OpenClaw app leaderboard from OpenRouter, verifies model IDs against the API catalog, and adds missing models with correct specs and aliases. Use when asked to "sync openrouter models", "add missing models", "update openrouter config", or "check openrouter models".
---

# OpenRouter Model Sync

Syncs models from the OpenClaw app leaderboard on OpenRouter into this openclaw installation.

## Workflow

### Step 1: Extract Model IDs via Browser

The app page is a React SPA -- must use browser tool, not web_fetch.

1. Open `https://openrouter.ai/apps?url=https%3A%2F%2Fopenclaw.ai%2F` in browser (profile: openclaw)
2. Take a snapshot, find and click "Show more" to expand full leaderboard
3. Take another snapshot after expansion
4. Extract model IDs from link hrefs -- they follow the pattern `/<provider>/<model-name>` (e.g. `/moonshotai/kimi-k2.5`)
5. Filter out non-model links (navigation links to `/docs`, `/chat`, `/rankings`, `/pricing`, `/enterprise`, `/about`, etc.)
6. Collect the model IDs (without leading slash)

### Step 2: Run Sync Script

```bash
python3 scripts/sync-openrouter-models.py --models "model/id1,model/id2,..."
```

Options:
- `--dry-run` — preview changes without writing files
- `--json` — machine-readable JSON output on stdout
- stdin also accepted (one model ID per line)

The script:
1. Verifies each ID against the OpenRouter `/api/v1/models` catalog (rejects unverified)
2. Converts verified models to openclaw format (context window, pricing, reasoning, modalities)
3. Creates timestamped backups before writing any config file
4. Adds missing models to `~/.openclaw/agents/<agent>/agent/models.json` and `~/.openclaw/openclaw.json`
5. Generates aliases (from `references/aliases.json` or auto-derived)

### Step 3: Restart Gateway

```bash
openclaw gateway restart
```

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `OPENCLAW_DIR` | Override openclaw directory | `~/.openclaw` |
| `OPENCLAW_AGENT_DIR` | Override agent directory | auto-detected |
| `OPENROUTER_API_KEY` | API key (falls back to config) | from config |

## Maintaining Aliases

Edit `references/aliases.json` to add or update short aliases for model IDs. The script loads this file at runtime. If missing, built-in defaults are used.

## What Gets Updated

- `~/.openclaw/agents/main/agent/models.json` — openrouter provider models
- `~/.openclaw/openclaw.json` — openrouter provider models + aliases
- Backups created as `<file>.bak.<timestamp>` before each write

## Limitations

- Additive only (does not remove delisted models)
- Reasoning detection uses heuristics (architecture field + known model families)
- Requires browser tool for Step 1 (app page is JS-rendered)
