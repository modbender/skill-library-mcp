Withings Connector

Summary
- CLI: `./bin/withings --date YYYY-MM-DD`
- Reads OAuth details from 1Password item `OpenClaw Withings` or env vars.
- By default, if credentials are present, performs live API calls; otherwise falls back to samples.

Credentials
Withings uses OAuth2. For automation, you maintain a refresh token.

1) Create a Withings developer app and set a redirect URI.
   - Default used here: `http://localhost:8791/callback`
2) Run the helper:

```bash
./bin/withings-auth --client-id <WITHINGS_CLIENT_ID> --client-secret <WITHINGS_CLIENT_SECRET>

# If your app redirect differs:
# ./bin/withings-auth --client-id <...> --client-secret <...> --redirect-uri "http://localhost:8888/callback"
```

3) Store in 1Password (your vault):
- Item: `OpenClaw Withings`
- Fields (labels must match exactly):
  - `client_id`
  - `client_secret`
  - `refresh_token`
  - `user_id` (optional)

Why client_id + client_secret?
- Withings refresh flows require refresh_token + client_id + client_secret to mint a new access token.

Env var fallbacks:
- `WITHINGS_CLIENT_ID`, `WITHINGS_CLIENT_SECRET`, `WITHINGS_REFRESH_TOKEN`, `WITHINGS_USER_ID`

Behavior
- Live by default when credentials exist. Set `OPENCLAW_FORCE_SAMPLE=1` to force sample output (e.g., offline/test envs).
- On each run, the connector refreshes the access token using the refresh token and client credentials.
- If a refresh rotates the refresh_token, the connector prints a non-sensitive note in the output telling you to update your 1Password item (it never prints tokens).

Output
- JSON payload for the given date (consumed by `./bin/health-brief`).
