# Config + storage

This skill keeps secrets out of git by default.

## Files

For each `--profile <name>` it stores:

- `~/.openclaw/secrets/m365-calendar/<profile>.json`
  - `clientId` (public client)
  - `tenant` (`organizations|consumers|common` or explicit tenantId)
  - `email` (optional; informational)
  - `scopes` (calendar delegated scopes)
- `~/.openclaw/secrets/m365-calendar/<profile>-token-cache.json`
  - MSAL token cache (refresh token, access token, etc.)

## Why not workspace/secrets?

- Skills should be shareable (e.g. Stefan) without sharing Tom’s tokens.
- Storing under `~/.openclaw/secrets/` makes it per-machine.

## Tenant values

- `organizations` → work/school tenants
- `consumers` → personal Microsoft accounts (hotmail.com, outlook.com)
- `common` → both (interactive login decides)

Graph supports `Prefer: outlook.timezone="Europe/Vienna"` so returned times match local expectations.
