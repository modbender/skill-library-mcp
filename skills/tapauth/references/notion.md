# Notion via TapAuth

## Provider Key

Use `notion` as the provider name.

## Scope Model: Integration-Level

Like Vercel, Notion uses **integration-level scopes** — the token gets whatever permissions the user grants during the OAuth consent flow. You cannot request specific scopes per grant.

The user will be asked to select which pages/databases to share with TapAuth. The token only has access to content the user explicitly selected.

## Example: Create a Grant

```bash
./scripts/tapauth.sh notion "" "Note Taker"
```

## Example: Get Current User

```bash
curl -H "Authorization: Bearer <token>" \
  -H "Notion-Version: 2022-06-28" \
  https://api.notion.com/v1/users/me
```

## Example: Search Pages

```bash
curl -X POST -H "Authorization: Bearer <token>" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  https://api.notion.com/v1/search \
  -d '{"query": "Meeting Notes"}'
```

## Example: Query a Database

```bash
curl -X POST -H "Authorization: Bearer <token>" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  https://api.notion.com/v1/databases/DATABASE_ID/query \
  -d '{}'
```

## Example: Create a Page

```bash
curl -X POST -H "Authorization: Bearer <token>" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  https://api.notion.com/v1/pages \
  -d '{
    "parent": {"database_id": "DATABASE_ID"},
    "properties": {"Name": {"title": [{"text": {"content": "New page"}}]}}
  }'
```

## Available Capabilities

| Capability | Description |
|------------|-------------|
| `read_content` | Read pages & databases |
| `update_content` | Update existing content |
| `insert_content` | Create new content |
| `read_user_with_email` | Read user info with email |

## Gotchas

- **Notion-Version header:** Every API request **must** include `Notion-Version: 2022-06-28` (or the latest version). Requests without it will fail.
- **Page selection:** Users choose which pages/databases to share during OAuth. If you can't find content, the user may not have shared it. Ask them to re-authorize with the relevant pages selected.
- **Integration-level scopes:** Cannot request granular scopes per grant.
- **Rate limits:** 3 requests per second. Notion returns `429` with a `Retry-After` header.
- **Rich text:** Notion content uses a block-based rich text format. The API returns structured objects, not plain text.

## Common Use Cases

| Use Case | API Endpoint |
|----------|-------------|
| Search | `POST /v1/search` |
| Read a page | `GET /v1/pages/{id}` |
| Read page content | `GET /v1/blocks/{id}/children` |
| Query database | `POST /v1/databases/{id}/query` |
| Create page | `POST /v1/pages` |
| Get current user | `GET /v1/users/me` |
