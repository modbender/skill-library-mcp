# MCP Configuration — Apple Health

Use this server in MCP-compatible clients:

```json
{
  "mcpServers": {
    "apple-health": {
      "command": "npx",
      "args": ["@neiltron/apple-health-mcp"],
      "env": {
        "HEALTH_DATA_DIR": "/absolute/path/to/health-export"
      }
    }
  }
}
```

## Runtime Compatibility

- Prefer Node LTS (`18`, `20`, or `22`).
- If startup fails with `duckdb.node` missing, switch Node version and retry.
- Validate once with: `npx -y @neiltron/apple-health-mcp`

## Minimum Validation Checklist

- Path is absolute and exists.
- Folder contains `HK*` CSV files.
- `HEALTH_DATA_DIR` points to unzipped export root, not a parent folder.
- `health_schema` returns at least one table.

## Optional Environment Variables

- `MAX_MEMORY_MB` (default `1024`)
- `CACHE_SIZE` (default `100`)

Only increase memory if large exports actually require it.
