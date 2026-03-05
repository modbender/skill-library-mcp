# Add Top OpenRouter Models

Automatically sync the most-used OpenRouter models into your OpenClaw installation.

## What It Does

1. Scrapes the [OpenClaw app leaderboard](https://openrouter.ai/apps?url=https%3A%2F%2Fopenclaw.ai%2F) on OpenRouter to find which models are most used
2. Verifies every model ID against the OpenRouter `/api/v1/models` catalog (rejects invalid/stale IDs)
3. Adds missing models to your local config with correct specs (context window, pricing, reasoning flag, modalities)
4. Generates short aliases for quick model switching

## Install

```bash
clawhub install add-top-openrouter-models
```

Or copy the skill directory into your OpenClaw workspace `skills/` folder.

## Usage

Ask your agent:
- "Sync my openrouter models"
- "Add missing openrouter models"
- "Check which openrouter models I'm missing"

The agent will open the OpenRouter app page in a browser, extract model IDs, run the sync script, and restart the gateway.

## How It Works

The OpenRouter app page is a React SPA that requires a real browser to render. The skill uses a two-step process:

1. **Browser extraction** — Agent opens the leaderboard page, expands it, and collects model IDs from links
2. **Script verification & sync** — `scripts/sync-openrouter-models.py` verifies each ID against the API, converts to OpenClaw format, and updates config files

### Config Files Updated

- `~/.openclaw/agents/main/agent/models.json` — OpenRouter provider models
- `~/.openclaw/openclaw.json` — OpenRouter provider models + model aliases

Timestamped backups are created before any write.

## Requirements

- OpenClaw installation with OpenRouter provider configured
- Browser tool access (for leaderboard scraping)
- `OPENROUTER_API_KEY` (from env or existing config)
- Python 3.6+

## Customization

Edit `references/aliases.json` to add or change short aliases for model IDs.

## Future Work

- Auto-detect new models without browser scraping if OpenRouter adds an app API endpoint
- Support removing delisted models (currently additive only)
