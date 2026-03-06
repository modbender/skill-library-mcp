Oura Connector

Summary
- CLI: `./bin/oura --date YYYY-MM-DD`
- Reads OAuth credentials from 1Password item `OpenClaw Oura` or env.
- By default, if credentials are present, performs live API calls; otherwise falls back to samples.

Credentials
Personal access tokens were deprecated (Dec 2025). Use OAuth.

1) Create an Oura API application.
2) Register redirect URI (default used by this repo):
   - `http://127.0.0.1:8788/callback`
3) Run the helper (request the `daily` scope or the daily_* endpoints will 401):

```bash
./bin/oura-auth --client-id <OURA_CLIENT_ID> --client-secret <OURA_CLIENT_SECRET> --redirect-uri "http://localhost:8788/callback" --scope "daily personal"
```

4) Store in 1Password (your vault) under item `OpenClaw Oura` with fields:
- `client_id`
- `client_secret`
- `token` (access_token)
- `refresh_token`

Legacy env var support:
- `OURA_CLIENT_ID`, `OURA_CLIENT_SECRET`, `OURA_PERSONAL_ACCESS_TOKEN`, `OURA_REFRESH_TOKEN`

Behavior
- Live by default when credentials exist. Set `OPENCLAW_FORCE_SAMPLE=1` to force sample output (e.g., in offline/test envs).
- On 401, the connector attempts a refresh using `refresh_token + client_id + client_secret`.
- If a refresh rotates the refresh_token, the connector includes a non-sensitive note telling you to update your 1Password item (it never prints tokens).

Output
- JSON payload for the given date (consumed by `./bin/health-brief`).
