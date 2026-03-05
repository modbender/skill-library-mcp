---
name: meta
description: Meta Marketing CLI for authentication lifecycle, Graph API requests, campaign/ad/adset writes, insights reporting, and Instagram publishing. Use when handling Meta ads or Instagram operations from terminal commands with strict fail-closed behavior.
homepage: https://github.com/bilalbayram/metacli
metadata: {"clawdbot":{"emoji":"📣","requires":{"bins":["meta"]},"install":[{"id":"go","kind":"go","module":"github.com/bilalbayram/metacli/cmd/meta@latest","bins":["meta"],"label":"Install meta (go)"}]}}
---

# meta

Use `meta` for Meta Marketing API and Instagram workflows.
Fail closed: if required inputs are missing or any command fails, stop immediately and surface the error.

Install
- `go install github.com/bilalbayram/metacli/cmd/meta@latest`
- `meta --help`

Human-required auth bootstrap (must happen first)
- Human creates a Meta app and provides `APP_ID` and `APP_SECRET`.
- Human configures OAuth redirect allowlist in Meta Developer settings with the exact `REDIRECT_URI`.
- Redirect must resolve to the AI host callback endpoint. For a local AI host:
  - `cloudflared tunnel --url http://127.0.0.1:53682` (or similar, it must be HTTPS)
  - Set `REDIRECT_URI=https://<tunnel-domain>/oauth/callback`
- AI runs setup without auto-opening a local browser:
  - `meta auth setup --profile <PROFILE> --app-id <APP_ID> --app-secret <APP_SECRET> --redirect-uri <REDIRECT_URI> --mode both --scope-pack solo_smb --listen 127.0.0.1:53682 --timeout 180s --open-browser=false`
- Human opens returned `auth_url` on their own machine, logs in, and grants consent.
- OAuth redirect lands on the AI host and token exchange completes there.
- Validate immediately:
  - `meta auth validate --profile <PROFILE> --min-ttl 72h`

Common commands
- Schema sync (recommended before writes): `meta schema sync --schema-dir ~/.meta/schema-packs`
- Accounts list: `meta --profile <PROFILE> insights accounts list --active-only --output table`
- Graph read: `meta --profile <PROFILE> api get act_<AD_ACCOUNT_ID>/campaigns --fields id,name,status --limit 100 --follow-next`
- Campaign dry-run: `meta --profile <PROFILE> campaign create --account-id <AD_ACCOUNT_ID> --params "name=<NAME>,objective=OUTCOME_SALES,status=PAUSED" --schema-dir ~/.meta/schema-packs --dry-run`
- Campaign create: `meta --profile <PROFILE> campaign create --account-id <AD_ACCOUNT_ID> --params "name=<NAME>,objective=OUTCOME_SALES,status=PAUSED" --schema-dir ~/.meta/schema-packs`
- Campaign budget update: `meta --profile <PROFILE> campaign update --campaign-id <CAMPAIGN_ID> --params "daily_budget=<AMOUNT_IN_MINOR_UNITS>" --confirm-budget-change`
- Insights run: `meta --profile <PROFILE> insights run --account-id <AD_ACCOUNT_ID> --date-preset last_7d --level campaign --metric-pack quality --format jsonl`
- IG publish feed: `meta --profile <PROFILE> ig publish feed --media-url <HTTPS_MEDIA_URL> --caption "<CAPTION>" --idempotency-key <UNIQUE_KEY>`

Rules
- Never invent IDs, profile names, paths, redirect URIs, or payload fields.
- Require explicit confirmation before budget-changing mutations.
- Prefer machine-readable output (`--output json` or `--format jsonl`) for automation.
- Redact secrets (`APP_SECRET`, access tokens) when echoing commands/results.
