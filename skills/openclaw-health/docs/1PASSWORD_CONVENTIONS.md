1Password Conventions

Use a single 1Password vault accessible to your OpenClaw automations. Each connector has one item. Prefer these exact titles and field names to simplify automation.

General
- Store tokens under the field name `token` when a single token is sufficient. For OAuth2 (e.g., Withings), store the long-lived refresh token under `refresh_token`.
- Add optional `user_id` or `account` fields if you manage multiple profiles.
- CLI access: this project reads via `op item get "<TITLE>" --fields json`.

Items
- OpenClaw Whoop
  - token: Whoop OAuth access token (Bearer)
  - refresh_token: Whoop OAuth refresh token (requires requesting the `offline` scope)
  - refresh_password: Back-compat field name used in an early item (treated as `refresh_token`)
  - client_id: Whoop OAuth client id (required for refresh)
  - client_secret: Whoop OAuth client secret (required for refresh)

- OpenClaw Oura
  - client_id: Oura OAuth client id
  - client_secret: Oura OAuth client secret
  - token: Oura OAuth access token (Bearer)
  - refresh_token: Oura OAuth refresh token

- OpenClaw Withings
  - client_id: Withings app client id
  - client_secret: Withings app client secret
  - refresh_token: Withings OAuth refresh token
  - user_id: Optional user id (integer)

Environment Variable Fallbacks
- WHOOP_ACCESS_TOKEN
- WHOOP_REFRESH_TOKEN
- WHOOP_CLIENT_ID
- WHOOP_CLIENT_SECRET
- OURA_PERSONAL_ACCESS_TOKEN
- WITHINGS_CLIENT_ID, WITHINGS_CLIENT_SECRET, WITHINGS_REFRESH_TOKEN, WITHINGS_USER_ID

Tips
- Rotate tokens periodically and update the item.
- Oura refresh tokens are rotation-sensitive (single-use): if you refresh and don’t save the *new* refresh_token, subsequent refresh attempts will fail.
- Service accounts require a vault filter for most `op` commands. Set `OPENCLAW_1P_VAULT` (e.g. `Assistant`) so this repo can pass `--vault` automatically.
- For local dev without `op`, set env vars in a `.env.local` (not committed) and export them in your shell.
