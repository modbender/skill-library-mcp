---
name: home-assistant-control
description: Control and inspect Home Assistant via REST API for entities, states, services, scenes, scripts, and automations. Use when the user asks to turn devices on/off, set values like brightness or temperature, trigger scenes/scripts/automations, or check current home/sensor status.
homepage: https://github.com/Hogar23/home-assistant-control
metadata:
  {
    "openclaw": {
      "emoji": "🏠",
      "requires": {
        "bins": ["bash", "curl", "jq"],
        "env": ["HA_TOKEN", "HA_URL_PUBLIC"]
      }
    }
  }
---

# Home Assistant Control

Use Home Assistant REST API with a long-lived access token.

## Requirements

### For skill users (runtime)

- `bash`
- `curl`
- `jq`
- Home Assistant long-lived token (`HA_TOKEN`)
- Home Assistant public base URL (`HA_URL_PUBLIC`)

### For skill maintainers (packaging/validation)

- `python3`
- `pyyaml` (required by `skill-creator` validator/packager scripts)

## Required environment variables

- `HA_TOKEN` (required)
- `HA_URL_PUBLIC` (required; canonical target and fallback)
- Optional URL behavior:
  - if `HA_URL_LOCAL` is set (and no `HA_URL` override), local is tried first, then fallback to `HA_URL_PUBLIC`
  - `HA_URL` is an explicit override (if set, used directly)

## Secrets handling (publish-safe)

- Keep keys/URLs in an external file, not in the skill folder.
- Set `HA_ENV_FILE=/absolute/path/to/file.env` when you want file-based secret loading.
- If `HA_ENV_FILE` is not set, scripts only use environment variables already present in the shell.
- `scripts/ha_call.sh` and `scripts/self_check.sh` load env file only when `HA_ENV_FILE` is provided.

## Core workflow

1. Parse the user request into target entity/service + desired action.
2. Check `references/naming-context.md` for manual alias mappings first.
3. Verify entity exists before changing state.
4. Execute service call.
5. Re-check state and report outcome clearly.

## Useful endpoints

- List states: `GET /api/states`
- Single state: `GET /api/states/{entity_id}`
- Call service: `POST /api/services/{domain}/{service}`

Headers:

- `Authorization: Bearer $HA_TOKEN`
- `Content-Type: application/json`

## Scripts

- `scripts/ha_env.sh` — loads env file only when `HA_ENV_FILE` is explicitly set, using safe KEY=VALUE parsing (no `source`/`eval`).
- `scripts/ha_call.sh` — generic API caller for Home Assistant.
- `scripts/fill_entities_md.sh` — generate `references/entities.md` from `GET /api/states`.
  - Full map: `./scripts/fill_entities_md.sh`
  - Filter domains: `./scripts/fill_entities_md.sh --domains light,switch,climate,sensor`
- `scripts/save_naming_context.sh` — refresh `references/naming-context.md` for user-specific naming.
  - `./scripts/save_naming_context.sh`
- `scripts/ha_entity_find.sh` — search entities by partial entity id or friendly name.
  - `./scripts/ha_entity_find.sh kitchen`
  - `./scripts/ha_entity_find.sh temp --domains sensor,climate --limit 30`
- `scripts/ha_safe_action.sh` — execute service actions with safety checks and risk confirmation.
  - `./scripts/ha_safe_action.sh light turn_on light.kitchen '{"brightness_pct":60}'`
  - `./scripts/ha_safe_action.sh lock unlock lock.front_door --dry-run`
  - Add `--yes` to bypass interactive confirmation for risky domains.
- `scripts/self_check.sh` — verify prerequisites and API connectivity/auth before running actions.
  - `./scripts/self_check.sh`

## Safety

- Confirm before high-impact actions (locks, alarms, garage/doors, heating shutdown).
- Do not print raw token values.
- If target entity is ambiguous, ask a follow-up question.
- Keep API paths scoped to Home Assistant endpoints only (`/api/...`).
- Use only HTTP(S) Home Assistant base URLs (`HA_URL*`), prefer HTTPS for public access.
- Avoid code execution when loading env files: parse key/value pairs, do not use `source` on untrusted paths.

## Reference files

- `references/entities.md` — entity inventory
- `references/naming-context.md` — user alias memory for natural names (e.g. "living room light")

## Publishing notes

- Keep examples generic (`example_*` IDs), no personal hostnames/tokens.
- Do not commit `.env` or any private env file with real tokens.
- Keep the skill focused: API workflow + reusable scripts + entity reference.
