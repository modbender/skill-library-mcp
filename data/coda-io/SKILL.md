---
name: coda
description: >
  Interact with Coda.io docs, tables, rows, pages, and automations via the Coda REST API v1.
  Use when the user wants to read, write, update, or delete data in Coda docs. Also use when
  they mention "Coda", "Coda doc", "Coda table", "Coda rows", "Coda API", "sync to Coda",
  "read from Coda", "write to Coda", "Coda automation", "Coda pages", "Coda formulas",
  "share Coda doc", or "Coda permissions". Covers docs, pages, tables, columns, rows,
  formulas, controls, folders, permissions, publishing, automations, and analytics.
metadata:
  env:
    - CODA_API_TOKEN (required): "Coda API token — get at https://coda.io/account → API settings"
---

# Coda API Skill

Interact with Coda.io via its REST API v1. Base URL: `https://coda.io/apis/v1`

## Setup

1. Get API token at https://coda.io/account → "API settings" → "Generate API token"
2. Set env var: `export CODA_API_TOKEN="<token>"`
3. Verify: `bash scripts/coda.sh whoami`

## Helper Script

`scripts/coda.sh` wraps common operations. Run `bash scripts/coda.sh help` for usage.

Examples:
```bash
# List docs
bash scripts/coda.sh list-docs | jq '.items[].name'

# List tables in a doc
bash scripts/coda.sh list-tables AbCDeFGH | jq '.items[] | {id, name}'

# List columns (discover IDs before writing)
bash scripts/coda.sh list-columns AbCDeFGH grid-abc | jq '.items[] | {id, name}'

# Read rows with column names
bash scripts/coda.sh list-rows AbCDeFGH grid-abc 10 true | jq '.items'

# Insert rows
echo '{"rows":[{"cells":[{"column":"c-abc","value":"Hello"}]}]}' | \
  bash scripts/coda.sh insert-rows AbCDeFGH grid-abc

# Upsert rows (match on key column)
echo '{"rows":[{"cells":[{"column":"c-abc","value":"Hello"},{"column":"c-def","value":42}]}],"keyColumns":["c-abc"]}' | \
  bash scripts/coda.sh upsert-rows AbCDeFGH grid-abc

# Share doc
bash scripts/coda.sh share-doc AbCDeFGH user@example.com write
```

## Workflow: Reading Data

1. `list-docs` → find the doc ID
2. `list-tables <docId>` → find the table ID
3. `list-columns <docId> <tableId>` → discover column IDs/names
4. `list-rows <docId> <tableId>` → read data

## Workflow: Writing Data

1. Discover column IDs first (step 3 above)
2. Build row JSON with `cells` array using column IDs
3. `insert-rows` (new data) or `upsert-rows` (with `keyColumns` for idempotent writes)
4. Write ops return HTTP 202 + `requestId` → poll with `mutation-status` if confirmation needed

## Key Concepts

- **IDs over names**: Use resource IDs (stable) rather than names (user-editable)
- **Eventual consistency**: Writes are async (HTTP 202). Poll `mutation-status` to confirm.
- **Pagination**: List endpoints return `nextPageToken`. Pass as `pageToken` for next page.
- **Rate limits**: Read 100/6s, Write 10/6s, Doc content write 5/10s. Respect 429 with backoff.
- **Fresh reads**: Add header `X-Coda-Doc-Version: latest` to ensure non-stale data (may 400).
- **valueFormat**: `simple` (default), `simpleWithArrays`, `rich` for structured data.
- **Doc ID from URL**: `https://coda.io/d/Title_d<DOC_ID>` → the part after `_d` is the doc ID.

## Direct curl (when script doesn't cover it)

```bash
curl -s -H "Authorization: Bearer $CODA_API_TOKEN" \
  "https://coda.io/apis/v1/docs/{docId}/tables/{tableId}/rows?useColumnNames=true&limit=50"
```

For writes:
```bash
curl -s -H "Authorization: Bearer $CODA_API_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST -d '{"rows":[...]}' \
  "https://coda.io/apis/v1/docs/{docId}/tables/{tableId}/rows"
```

## Full API Reference

See [references/api-endpoints.md](references/api-endpoints.md) for complete endpoint listing with parameters, body schemas, and response details.

Searchable by section: Account, Folders, Docs, Pages, Tables, Columns, Rows, Formulas, Controls, Permissions, Publishing, Automations, Analytics, Miscellaneous.
