# EVE ESI Skill for OpenClaw

An [OpenClaw](https://openclaw.ai) skill for interacting with the [EVE Online ESI API](https://developers.eveonline.com/api-explorer) (EVE Swagger Interface).

## Features

- **Authentication** — PKCE OAuth2 flow via EVE SSO, auto-refreshing tokens
- **ESI Queries** — reusable Python helper with pagination, error limits, and caching
- **Multi-character** — store and manage tokens for multiple characters
- **Dashboard Config** — modular alert/report/market-tracking config schema
- **Reference docs** — full scope list, endpoint index, auth flow details

## Structure

```
eve-esi/
├── SKILL.md                        # OpenClaw skill instructions
├── README.md                       # This file
├── scripts/
│   ├── auth_flow.py                # One-time EVE SSO OAuth2 authentication
│   ├── get_token.py                # Token refresh helper (auto-rotates)
│   ├── esi_query.py                # ESI query helper with pagination
│   └── validate_config.py          # Dashboard config validator
├── config/
│   ├── schema.json                 # JSON Schema for dashboard config
│   └── example-config.json         # Ready-to-use template
└── references/
    ├── authentication.md           # EVE SSO OAuth2 + PKCE details
    └── endpoints.md                # All character endpoints + scopes
```

## Installation

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/burnshall-ui/openclaw-eve-skill eve-esi
```

## Authentication Setup

**Prerequisites:**
1. Register an app at [developers.eveonline.com](https://developers.eveonline.com/applications)
2. Set callback URL to `http://127.0.0.1:8080/callback`
3. Note your **Client ID**

**One-time auth per character** (requires browser access):

```bash
# If on a remote server, set up an SSH tunnel first:
ssh -L 8080:127.0.0.1:8080 user@your-server -N

# Run the auth flow:
python3 scripts/auth_flow.py --client-id <YOUR_CLIENT_ID> --char-name main

# Open the shown URL in your browser and log in with your EVE account
```

Tokens are stored in `~/.openclaw/eve-tokens.json` (chmod 600).

**Authenticate additional characters:**
```bash
python3 scripts/auth_flow.py --client-id <CLIENT_ID> --char-name alt1
```

## Quick Start

```bash
SKILL=~/.openclaw/workspace/skills/eve-esi

# Get a fresh access token (auto-refreshes on every call)
TOKEN=$(python3 $SKILL/scripts/get_token.py --char main)

# List all authenticated characters
python3 $SKILL/scripts/get_token.py --list

# Wallet balance
python3 $SKILL/scripts/esi_query.py --token "$TOKEN" \
  --endpoint "/characters/<CHAR_ID>/wallet/" --pretty

# Skill queue
python3 $SKILL/scripts/esi_query.py --token "$TOKEN" \
  --endpoint "/characters/<CHAR_ID>/skillqueue/" --pretty

# All assets (paginated)
python3 $SKILL/scripts/esi_query.py --token "$TOKEN" \
  --endpoint "/characters/<CHAR_ID>/assets/" --pages --pretty
```

## Dashboard Config

Set up automated alerts, scheduled reports, and market price tracking:

```bash
# Copy example config
cp config/example-config.json ~/.openclaw/eve-dashboard-config.json

# Edit with your character IDs and preferences
# Use $ENV:VARIABLE_NAME for tokens — never store secrets in plain text

# Validate
python3 scripts/validate_config.py ~/.openclaw/eve-dashboard-config.json
```

See [config/schema.json](config/schema.json) for the full schema.

### Alert Types

| Alert | Description |
|-------|-------------|
| `war_declared` | New war declaration against your corp |
| `structure_under_attack` | Structure attacked |
| `structure_fuel_low` | Fuel below threshold (hours) |
| `skill_complete` | Skill training finished |
| `wallet_large_deposit` | ISK deposit above threshold |
| `industry_job_complete` | Manufacturing/research job done |
| `pi_extractor_expired` | Planetary extraction head expired |
| `killmail` | New killmail received |
| `contract_expired` | Contract expired |

### Report Templates

| Report | Description |
|--------|-------------|
| `net_worth` | Total ISK across wallet + assets |
| `skill_queue` | Current training status |
| `industry_jobs` | Active manufacturing/research jobs |
| `market_orders` | Open buy/sell orders |
| `wallet_summary` | Recent transaction summary |
| `assets_summary` | Top asset locations by value |

## Security

- Tokens stored in `~/.openclaw/eve-tokens.json` with `chmod 600`
- Refresh tokens rotate on every use (EVE SSO best practice)
- Dashboard config supports `$ENV:VARIABLE_NAME` to keep secrets out of files
- Never commit `eve-tokens.json` or configs with real tokens

## Requirements

- Python 3.8+ (stdlib only — no pip dependencies)
- OpenClaw gateway

## Links

- [EVE ESI API Explorer](https://developers.eveonline.com/api-explorer)
- [EVE Developer Portal](https://developers.eveonline.com/applications)
- [OpenClaw Docs](https://docs.openclaw.ai)
- [ClawHub Skill Page](https://clawhub.ai/burnshall-ui/eve-esi)
