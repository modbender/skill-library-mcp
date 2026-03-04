---
name: openclaw-health-brief
description: Generate a daily health brief from Oura, Whoop, and Withings. Unified re-auth script, local token persistence, Green/Yellow/Red morning summary.
---

# OpenClaw Health Brief

Daily health metrics from **Oura**, **WHOOP**, and **Withings** → normalized JSON + Markdown brief.

## Setup (3 steps)

### Step 1: Configure secrets

**Option A: 1Password (recommended)**
```bash
export OP_SERVICE_ACCOUNT_TOKEN="your-token"
export OPENCLAW_1P_VAULT="Assistant"  # or your vault name
```

Create items in your vault with these titles and fields:
- `OpenClaw Whoop` → `client_id`, `client_secret`, `token`, `refresh_token`
- `OpenClaw Oura` → `client_id`, `client_secret`, `token`, `refresh_token`
- `OpenClaw Withings` → `client_id`, `client_secret`, `access_token`, `refresh_token`, `user_id`

See `./docs/1PASSWORD_CONVENTIONS.md` for full field details.

**Option B: Environment variables**
```bash
# WHOOP
export WHOOP_ACCESS_TOKEN="..." WHOOP_REFRESH_TOKEN="..." WHOOP_CLIENT_ID="..." WHOOP_CLIENT_SECRET="..."
# Oura
export OURA_PERSONAL_ACCESS_TOKEN="..."  # or OAuth: OURA_REFRESH_TOKEN + OURA_CLIENT_ID + OURA_CLIENT_SECRET
# Withings
export WITHINGS_CLIENT_ID="..." WITHINGS_CLIENT_SECRET="..." WITHINGS_REFRESH_TOKEN="..." WITHINGS_USER_ID="..."
```

### Step 2: Authorize providers

```bash
python3 ./bin/health-reauth all
```

This opens your browser for each provider. Click authorize, and tokens are saved to both 1Password and `~/.openclaw/secrets/health_tokens.json` automatically.

You can also re-auth individually: `python3 ./bin/health-reauth whoop`

### Step 3: Run your first brief

```bash
./bin/health-brief --date "$(date +%F)" --sources whoop,oura,withings --out "./out/daily_health_$(date +%F).json"
```

**That's it.** Token rotation is handled automatically — refreshed tokens persist to the local file so you don't need to re-auth again.

## Add to OpenClaw cron

Wire it into your morning routine with an OpenClaw cron job:

```bash
openclaw cron add \
  --name "morning-health-brief" \
  --schedule "0 8 * * *" \
  --tz "America/New_York" \
  --session-target isolated \
  --message 'Run the health brief:
source ~/.openclaw/secrets/gateway.env
export OPENCLAW_1P_VAULT=YourVault
./bin/health-brief --date "$(date +%F)" --sources whoop,oura,withings --out "/tmp/daily_health_$(date +%F).json"
Read the JSON output. Report only non-null metrics with a Green/Yellow/Red rating.'
```

The cron job runs as an isolated agent session — it executes the brief, reads the output, and delivers a formatted summary to your preferred channel.

## Smoke test (no creds needed)

```bash
./bin/smoke
```

Runs in sample mode, validates JSON schema. Good for checking the skill is installed correctly.

## Troubleshooting

### Check individual providers
```bash
./bin/whoop --date "$(date +%F)"
./bin/oura --date "$(date +%F)"
./bin/withings --date "$(date +%F)"
```

### Common errors
- `has_token: false` → credentials not found. Check 1Password item names or env vars.
- `refresh_failed` → refresh token expired. Run `python3 ./bin/health-reauth <provider>`
- `missing_credentials` → client_id/client_secret not set.

### Validate output JSON
```bash
./bin/validate-json --in ./out/daily_health_YYYY-MM-DD.json
```

## References
- `./docs/1PASSWORD_CONVENTIONS.md` — field naming for 1Password items
- `./docs/OURA.md`, `./docs/WHOOP.md`, `./docs/WITHINGS.md` — provider API notes
- `./docs/MORNING_BRIEF.md` — morning brief intent and format
