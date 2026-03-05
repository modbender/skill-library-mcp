WHOOP Connector

Summary
- CLI: `./bin/whoop --date YYYY-MM-DD`
- Auth helper: `./bin/whoop-auth` (prints auth URL; can exchange code for tokens)
- Reads credentials from 1Password item **"OpenClaw Whoop"** (recommended) or env vars.
  - Access token: field `token` or env `WHOOP_ACCESS_TOKEN`
  - Refresh token: field `refresh_token` (back-compat: `refresh_password`) or env `WHOOP_REFRESH_TOKEN`
  - Client creds (for refresh): fields `client_id` / `client_secret` or env `WHOOP_CLIENT_ID` / `WHOOP_CLIENT_SECRET`
- If no access token is available, falls back to sample data.

Credentials
WHOOP uses OAuth 2.0 (authorization code flow).

1) In the WHOOP developer dashboard, create an OAuth app and set the redirect URI.
   - Default redirect URI used by this repo: `http://127.0.0.1:8787/callback`
2) Run the helper to get tokens (includes `offline` by default so refresh works for cron):
   - `./bin/whoop-auth --client-id <...> --client-secret <...>`
   - Open the printed URL, approve, and let it capture the `code`.
3) Store tokens in 1Password (your vault):
   - Item title: `OpenClaw Whoop`
   - Field `token`: `<access_token>`
   - Field `refresh_token`: `<refresh_token>` (requires requesting the `offline` scope)
   - Field `client_id`: `<WHOOP_CLIENT_ID>`
   - Field `client_secret`: `<WHOOP_CLIENT_SECRET>`

Alternate: set env var `WHOOP_ACCESS_TOKEN`.

Output
- Prints JSON payload for the given date and writes nothing by default.
- Intended for composition by `./bin/health-brief`.

Notes
- When an access token is present, the connector performs live WHOOP API calls.
- On HTTP 401, it will attempt an OAuth refresh **if** `refresh_token`, `client_id`, and `client_secret` are available.
- WHOOP refresh responses may rotate the refresh token; if that happens, the connector annotates the payload with a note so you can update 1Password.
- The `--live` flag is deprecated (live is the default when credentials are present).

