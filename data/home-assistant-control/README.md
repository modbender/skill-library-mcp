# OpenClaw Skill: Home Assistant Control

OpenClaw skill for controlling and inspecting Home Assistant via REST API.

## Features

- Safe service execution (`ha_safe_action.sh`) with guardrails
- Local-first URL routing with public fallback
- Entity discovery/search (`ha_entity_find.sh`)
- Entity map generation (`fill_entities_md.sh`)
- Naming-context aliases for natural commands (`references/naming-context.md`)
- Environment self-check (`self_check.sh`)

## Runtime Requirements

- bash
- curl
- jq

## Configuration

Use a private env file by explicitly pointing to it:

- set `HA_ENV_FILE=/absolute/path/to/env`
- example path: `~/.openclaw/private/home-assistant.env`

Required:

- `HA_TOKEN`
- `HA_URL_PUBLIC` (canonical target and fallback)
- Optional URL strategy:
  - optional `HA_URL_LOCAL` (tried first when override not set)
  - optional `HA_URL` (explicit override)

### Example private env file

Create a private file (example `~/.openclaw/private/home-assistant.env`), then set:

```bash
export HA_ENV_FILE="$HOME/.openclaw/private/home-assistant.env"
```

Example file content:

```env
HA_TOKEN=YOUR_LONG_LIVED_ACCESS_TOKEN
HA_URL_PUBLIC=https://your-home.example.com
# Optional local URL (tried first when HA_URL is not set)
# HA_URL_LOCAL=http://homeassistant.local:8123
# Optional explicit override (no fallback)
# HA_URL=http://homeassistant.local:8123
```

## Security model

- The scripts only call Home Assistant API paths under `/api/...`.
- Base URLs must be `http://` or `https://`.
- For remote/public access, use HTTPS.
- Secrets are loaded only when `HA_ENV_FILE` is explicitly set, and should never be committed.
- Env files are parsed as plain `KEY=VALUE` data (no `source`/shell execution).

## Main Scripts

- `scripts/self_check.sh`
- `scripts/ha_call.sh`
- `scripts/ha_safe_action.sh`
- `scripts/ha_entity_find.sh`
- `scripts/fill_entities_md.sh`
- `scripts/save_naming_context.sh`

## Package Artifact

This repo includes `home-assistant-control.skill` for direct distribution.
