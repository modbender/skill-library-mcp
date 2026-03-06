# OPERATIONS

## Start runtime (read/write enabled)

```bash
cd "$HOME/.openclaw/runtime/websites-mcp"
PROSPAIRROW_API_KEY="..." npm run mcp:writes
```

## Start runtime (read-only)

```bash
cd "$HOME/.openclaw/runtime/websites-mcp"
PROSPAIRROW_API_KEY="..." npm run mcp
```

## Smoke tests

List sites:

```bash
curl -sS http://127.0.0.1:8799 \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"websites.list_sites","params":{}}'
```

Run task:

```bash
curl -sS http://127.0.0.1:8799 \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $PROSPAIRROW_API_KEY" \
  -d '{"jsonrpc":"2.0","id":1,"method":"websites.run_task","params":{"siteId":"prospairrow","taskId":"extract_prospects","params":{}}}'
```
