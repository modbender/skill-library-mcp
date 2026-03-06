# Wallabag API Notes Used By This Skill

This skill targets Wallabag's OAuth and entries endpoints.

## Authentication

- Method: `POST /oauth/v2/token`
- Body fields:
  - `grant_type=password`
  - `client_id`
  - `client_secret`
  - `username`
  - `password`
- Expected success response fields:
  - `access_token`
  - `expires_in`
  - `token_type`

## Entry Endpoints

- `GET /api/entries.json`
  - Optional query params used by this skill: `search`, `tags`, `archive`, `starred`, `page`, `perPage`
- `POST /api/entries.json`
  - Form fields used: `url`, `title`, `tags`
- `GET /api/entries/{id}.json`
- `PATCH /api/entries/{id}.json`
  - Form fields used: `title`, `tags`, `archive`, `starred`
- `DELETE /api/entries/{id}.json`

## Tag Operations Strategy

This skill handles tag add/remove by:

1. Reading current tags from `GET /api/entries/{id}.json`
2. Building updated CSV tags in-memory
3. Sending `PATCH /api/entries/{id}.json` with the recalculated `tags` field

This avoids hardcoding undocumented tag-specific entry mutations.

## Error Handling Expectations

- Non-2xx responses are surfaced as stderr + non-zero exit code.
- OAuth failure prints status and response payload.
- Network-level failures return curl exit code.

## Security Notes

- Credentials are supplied only via env vars.
- No token is written to disk.
