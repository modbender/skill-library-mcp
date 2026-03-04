# OpenClaw Health Skills

Daily health metrics from **WHOOP**, **Oura**, and **Withings** — normalized JSON + Markdown brief.

## What it does
- Fetches sleep, readiness, activity, HRV, weight, and body composition
- Normalizes into a stable JSON schema (provider differences abstracted away)
- Prints a concise Markdown brief (Green/Yellow/Red rating)
- Auto-persists rotated OAuth tokens so you only authorize once

## Quick start

### 0. Pick your providers

```bash
./bin/onboard
```

Interactive setup (~1 min) that asks:
- Which devices do you use? (WHOOP, Oura, Withings — pick any combo)
- How do you use them? (24/7, sleep-only, day-only, etc.)
- Source of truth for overlapping metrics (e.g. sleep from Oura or WHOOP?)

Writes a `config.json` so the brief knows what to pull and which source to trust.

### 1. Configure secrets

**Option A: 1Password (recommended)**
```bash
export OP_SERVICE_ACCOUNT_TOKEN="your-token"
export OPENCLAW_1P_VAULT="YourVault"   # your vault name
```

Create items in your vault (see `docs/1PASSWORD_CONVENTIONS.md` for field details):
- `OpenClaw Whoop` → `client_id`, `client_secret`, `token`, `refresh_token`
- `OpenClaw Oura` → `client_id`, `client_secret`, `token`, `refresh_token`
- `OpenClaw Withings` → `client_id`, `client_secret`, `access_token`, `refresh_token`, `user_id`

**Option B: Environment variables**
```bash
# WHOOP
export WHOOP_CLIENT_ID="..." WHOOP_CLIENT_SECRET="..." WHOOP_ACCESS_TOKEN="..." WHOOP_REFRESH_TOKEN="..."
# Oura
export OURA_CLIENT_ID="..." OURA_CLIENT_SECRET="..." OURA_PERSONAL_ACCESS_TOKEN="..."
# Withings
export WITHINGS_CLIENT_ID="..." WITHINGS_CLIENT_SECRET="..." WITHINGS_REFRESH_TOKEN="..." WITHINGS_USER_ID="..."
```

### 2. Authorize providers

```bash
python3 ./bin/health-reauth all
```

Opens your browser for each provider. Click authorize — tokens are saved to both 1Password and `~/.openclaw/secrets/health_tokens.json` automatically.

Re-auth individually if needed: `python3 ./bin/health-reauth whoop`

### 3. Run your first brief

```bash
./bin/health-brief --date "$(date +%F)" --sources whoop,oura,withings --out /tmp/daily_health.json
```

Outputs:
- Normalized JSON → `--out` path
- Markdown brief → stdout

**That's it.** Token rotation is handled automatically.

## Add to OpenClaw cron (daily morning brief)

Add a cron job so your health brief runs automatically each morning:

```bash
openclaw cron add \
  --name "morning-health-brief" \
  --schedule "0 8 * * *" \
  --tz "America/New_York" \
  --session-target isolated \
  --message 'Run the health brief and send results.

```bash
source ~/.openclaw/secrets/gateway.env
export OPENCLAW_1P_VAULT=YourVault
DATE="$(date +%F)"
cd /path/to/openclaw-health-skills
./bin/health-brief --date "$DATE" --sources whoop,oura,withings --out "/tmp/daily_health_${DATE}.json"
```

Read the output JSON. Only report metrics with non-null values. Present with a Green/Yellow/Red rating. Send a brief summary to the user.'
```

Or if you prefer to add it via the OpenClaw config directly, create an isolated `agentTurn` cron job that:
1. Runs `./bin/health-brief` with today's date
2. Reads the output JSON
3. Formats a brief with Green/Yellow/Red rating
4. Delivers via your preferred channel (Telegram, Discord, etc.)

See [OpenClaw cron docs](https://docs.openclaw.ai/automation/cron) for more options.

## Token persistence

Refreshed tokens persist to `~/.openclaw/secrets/health_tokens.json` (chmod 600). If a provider rotates your refresh token during a refresh, the new one is saved immediately. You should never need to re-auth unless you revoke access at the provider.

Override location: `OPENCLAW_LOCAL_SECRETS_PATH=/path/to/health_tokens.json`

## Troubleshooting

### Check individual providers
```bash
./bin/whoop --date "$(date +%F)"
./bin/oura --date "$(date +%F)"
./bin/withings --date "$(date +%F)"
```

### Common issues
| Symptom | Cause | Fix |
|---------|-------|-----|
| `has_token: false` | Credentials not found | Check 1Password item names or env vars |
| `refresh_failed` | Refresh token expired/revoked | `python3 ./bin/health-reauth <provider>` |
| `missing_credentials` | No client_id/client_secret | Add to 1Password or env vars |
| 403 on token exchange | Cloudflare blocking Python | `health-reauth` uses curl to bypass this |

### Validate output
```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Provider setup (one-time per provider)

Each provider requires a free developer account and an OAuth app. This takes ~5 minutes per provider.

### WHOOP

1. Go to [developer.whoop.com](https://developer.whoop.com) and create an account
2. Create a new OAuth application:
   - **Name:** anything (e.g. "OpenClaw Health")
   - **Redirect URI:** `http://127.0.0.1:8787/callback`
   - **Scopes:** enable all `read:*` scopes + `offline` (required for refresh tokens)
3. Copy your **Client ID** and **Client Secret**
4. Store in 1Password (item: `OpenClaw Whoop`, fields: `client_id`, `client_secret`) or export as env vars
5. Run `python3 ./bin/health-reauth whoop` — it opens your browser, you click authorize, done

### Oura

1. Go to [cloud.ouraring.com/v2/docs](https://cloud.ouraring.com/v2/docs) and sign in
2. Go to **My Applications** → create a new application:
   - **Name:** anything
   - **Redirect URI:** `http://localhost:8788/callback`
   - **Scopes:** `daily` and `personal` (required for sleep, readiness, activity)
3. Copy your **Client ID** and **Client Secret**
4. Store in 1Password (item: `OpenClaw Oura`, fields: `client_id`, `client_secret`) or export as env vars
5. Run `python3 ./bin/health-reauth oura`

> **Note:** Oura deprecated personal access tokens in Dec 2025. OAuth is now required.

### Withings

1. Go to [developer.withings.com](https://developer.withings.com) and create a developer account
2. Create a new application:
   - **Name:** anything
   - **Redirect URI:** `http://localhost:8791/callback`
   - **Scopes:** `user.metrics`, `user.activity`
3. Copy your **Client ID** and **Client Secret**
4. Store in 1Password (item: `OpenClaw Withings`, fields: `client_id`, `client_secret`) or export as env vars
5. Run `python3 ./bin/health-reauth withings`

### After setup

Once you've authorized all providers, you're done. The `health-reauth` script saves tokens to both 1Password and a local file. Token rotation is automatic — you shouldn't need to re-auth unless you revoke access at the provider.

For detailed per-provider API notes, see `docs/WHOOP.md`, `docs/OURA.md`, `docs/WITHINGS.md`, and `docs/1PASSWORD_CONVENTIONS.md`.

## Architecture

```
bin/                  CLI entrypoints (health-brief, health-reauth, per-provider)
connectors/           Provider-specific fetch + OAuth refresh logic
core/
  normalize/          Unified DailyHealth schema
  render/             Markdown brief renderer
  util/
    secrets.py        1Password + env var secret resolution
    local_secrets.py  Local file token persistence
docs/                 Per-provider API notes + 1Password field conventions
tests/                Unit tests
```
