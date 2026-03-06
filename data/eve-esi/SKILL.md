---
name: eve-esi
description: "Query and manage EVE Online characters via the ESI (EVE Swagger Interface) REST API. Use when the user asks about EVE Online character data, wallet balance, ISK transactions, assets, skill queue, skill points, clone locations, implants, fittings, contracts, market orders, mail, industry jobs, killmails, planetary interaction, loyalty points, or any other EVE account management task."
env:
  - name: EVE_CLIENT_ID
    description: "EVE Developer Application Client ID (from https://developers.eveonline.com/applications). Optional: only needed if using $ENV: references in your dashboard config instead of passing --client-id to auth_flow.py directly."
    required: false
    sensitive: false
  - name: EVE_TOKEN_MAIN
    description: "ESI OAuth2 access token for the main character. Optional: scripts auto-manage tokens via ~/.openclaw/eve-tokens.json (written by auth_flow.py). Only set this if using $ENV: references in your dashboard config."
    required: false
    sensitive: true
  - name: EVE_REFRESH_MAIN
    description: "ESI OAuth2 refresh token for automatic access token renewal. Optional: scripts auto-manage tokens via ~/.openclaw/eve-tokens.json. Only set this if using $ENV: references in your dashboard config."
    required: false
    sensitive: true
  - name: TELEGRAM_BOT_TOKEN
    description: "Telegram Bot API token for sending alerts and reports."
    required: false
    sensitive: true
  - name: TELEGRAM_CHAT_ID
    description: "Telegram chat ID where notifications are sent."
    required: false
    sensitive: false
  - name: DISCORD_WEBHOOK_URL
    description: "Discord webhook URL for sending alerts and reports."
    required: false
    sensitive: true
---

# Data Handling

This skill communicates exclusively with the official EVE Online ESI API (`esi.evetech.net`) and EVE SSO (`login.eveonline.com`).
No character data is exfiltrated to third-party servers.
Optional integrations (Telegram, Discord) are user-configured via environment variables and only transmit alerts defined by the user.

# EVE Online ESI

The ESI (EVE Swagger Interface) is the official REST API for EVE Online third-party development.

- Base URL: `https://esi.evetech.net/latest`
- Spec: `https://esi.evetech.net/latest/swagger.json`
- API Explorer: <https://developers.eveonline.com/api-explorer>

## Skill Location

All scripts live at: `~/.openclaw/workspace/skills/eve-esi/scripts/`

Always use full paths when calling scripts:
```bash
SKILL=~/.openclaw/workspace/skills/eve-esi
```

## Authentication

Tokens are stored in `~/.openclaw/eve-tokens.json` (created by auth_flow.py, chmod 600).
All scripts (`get_token.py`, `esi_query.py`) read from this file directly — **no env vars are required for normal operation.**

**First-time setup** (once per character):
```bash
# 1. Set up SSH tunnel on your local PC:
#    ssh -L 8080:127.0.0.1:8080 user@your-server -N
# 2. Run auth flow on server (pass Client ID directly):
python3 ~/.openclaw/workspace/skills/eve-esi/scripts/auth_flow.py --client-id <YOUR_CLIENT_ID> --char-name main
# 3. Open the shown URL in browser, log in with EVE account
```

**Get a fresh access token** (tokens expire after ~20min, refresh is automatic):
```bash
TOKEN=$(python3 ~/.openclaw/workspace/skills/eve-esi/scripts/get_token.py --char main)
```

**List authenticated characters:**
```bash
python3 ~/.openclaw/workspace/skills/eve-esi/scripts/get_token.py --list
```

For full OAuth2/PKCE details: see `references/authentication.md`.

## Public endpoints (no auth)

```bash
# Character public info
curl -s "https://esi.evetech.net/latest/characters/2114794365/" | python -m json.tool

# Portrait URLs
curl -s "https://esi.evetech.net/latest/characters/2114794365/portrait/"

# Corporation history
curl -s "https://esi.evetech.net/latest/characters/2114794365/corporationhistory/"

# Bulk affiliation lookup
curl -s -X POST "https://esi.evetech.net/latest/characters/affiliation/" \
  -H "Content-Type: application/json" \
  -d '[2114794365, 95538921]'
```

## Character info (authenticated)

```bash
TOKEN="<your_access_token>"
CHAR_ID="<your_character_id>"

# Online status (scope: esi-location.read_online.v1)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://esi.evetech.net/latest/characters/$CHAR_ID/online/"
```

## Wallet

```bash
# Balance (scope: esi-wallet.read_character_wallet.v1)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://esi.evetech.net/latest/characters/$CHAR_ID/wallet/"

# Journal (paginated)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://esi.evetech.net/latest/characters/$CHAR_ID/wallet/journal/?page=1"

# Transactions
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://esi.evetech.net/latest/characters/$CHAR_ID/wallet/transactions/"
```

## Assets

```bash
# All assets (paginated; scope: esi-assets.read_assets.v1)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://esi.evetech.net/latest/characters/$CHAR_ID/assets/?page=1"

# Resolve item locations
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '[1234567890, 9876543210]' \
  "https://esi.evetech.net/latest/characters/$CHAR_ID/assets/locations/"

# Resolve item names
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '[1234567890]' \
  "https://esi.evetech.net/latest/characters/$CHAR_ID/assets/names/"
```

## Skills

```bash
# All trained skills + total SP (scope: esi-skills.read_skills.v1)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://esi.evetech.net/latest/characters/$CHAR_ID/skills/"

# Skill queue (scope: esi-skills.read_skillqueue.v1)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://esi.evetech.net/latest/characters/$CHAR_ID/skillqueue/"

# Attributes (intelligence, memory, etc.)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://esi.evetech.net/latest/characters/$CHAR_ID/attributes/"
```

## Location and ship

```bash
# Current location (scope: esi-location.read_location.v1)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://esi.evetech.net/latest/characters/$CHAR_ID/location/"

# Current ship (scope: esi-location.read_ship_type.v1)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://esi.evetech.net/latest/characters/$CHAR_ID/ship/"
```

## Clones and implants

```bash
# Jump clones + home station (scope: esi-clones.read_clones.v1)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://esi.evetech.net/latest/characters/$CHAR_ID/clones/"

# Active implants (scope: esi-clones.read_implants.v1)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://esi.evetech.net/latest/characters/$CHAR_ID/implants/"
```

## More endpoints

For contracts, fittings, mail, industry, killmails, market orders, mining, planetary interaction, loyalty points, notifications, blueprints, standings, and all other character endpoints, see [references/endpoints.md](references/endpoints.md).

## Dashboard Config

The skill supports a modular dashboard config for alerts, reports, and market tracking. Each user defines what they need in a JSON config file.

- **Schema**: [config/schema.json](config/schema.json) — full JSON Schema with all fields, types, and defaults
- **Example**: [config/example-config.json](config/example-config.json) — ready-to-use template

### Features

| Module | Description |
|--------|-------------|
| **Alerts** | Real-time polling for war decs, structure attacks, skill completions, wallet changes, industry jobs, PI extractors, killmails, contracts, clone jumps, mail |
| **Reports** | Cron-scheduled summaries: net worth, skill queue, industry, market orders, wallet, assets |
| **Market** | Price tracking with absolute thresholds and trend detection |

### Security

Tokens should **not** be stored in plain text. Use environment variable references:

```json
{
  "token": "$ENV:EVE_TOKEN_MAIN",
  "refresh_token": "$ENV:EVE_REFRESH_MAIN"
}
```

The config file should live outside the workspace (e.g. `~/.openclaw/eve-dashboard-config.json`).

### Validate a config

```bash
python scripts/validate_config.py path/to/config.json

# Show example config
python scripts/validate_config.py --example

# Show JSON schema
python scripts/validate_config.py --schema
```

## Using the query script

```bash
SKILL=~/.openclaw/workspace/skills/eve-esi
TOKEN=$(python3 $SKILL/scripts/get_token.py --char main)
CHAR_ID=$(python3 $SKILL/scripts/get_token.py --char main --json | python3 -c "import sys,json; print(json.load(sys.stdin))" 2>/dev/null)

# Simple query
python3 $SKILL/scripts/esi_query.py --token "$TOKEN" --endpoint "/characters/$CHAR_ID/wallet/" --pretty

# Fetch all pages of assets
python3 $SKILL/scripts/esi_query.py --token "$TOKEN" --endpoint "/characters/$CHAR_ID/assets/" --pages --pretty

# POST request (e.g. asset names)
python3 $SKILL/scripts/esi_query.py --token "$TOKEN" --endpoint "/characters/$CHAR_ID/assets/names/" \
  --method POST --body '[1234567890]' --pretty
```

## Best practices

- **Caching**: respect the `Expires` header; do not poll before it expires.
- **Error limits**: monitor `X-ESI-Error-Limit-Remain`; back off when low.
- **User-Agent**: always set a descriptive User-Agent with contact info.
- **Rate limits**: some endpoints (mail, contracts) have internal rate limits returning HTTP 520.
- **Pagination**: check the `X-Pages` response header; iterate with `?page=N`.
- **Versioning**: use `/latest/` for current stable routes. `/dev/` may change without notice.

## Resolving type IDs

ESI returns numeric type IDs (e.g. for ships, items, skills). Resolve names via:

```bash
# Single type
curl -s "https://esi.evetech.net/latest/universe/types/587/"

# Bulk names (up to 1000 IDs)
curl -s -X POST "https://esi.evetech.net/latest/universe/names/" \
  -H "Content-Type: application/json" \
  -d '[587, 638, 11393]'
```
