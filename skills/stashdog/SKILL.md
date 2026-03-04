---
name: stashdog
version: 1.0.0
description: |
  Connect to Raz's StashDog inventory MCP server (OAuth via mcp-remote) and run
  common inventory actions: list items, search items, and add items.
---

# StashDog MCP Skill

StashDog is Raz's item inventory app. This skill documents how to connect to the
StashDog MCP server and includes helper commands for common tasks.

## MCP Connection

- **Endpoint:** `https://gmchczeyburroiyzefie.supabase.co/functions/v1/mcp-server/mcp`
- **Auth:** OAuth (via `mcp-remote` proxy)
- **Tools:** `list_items`, `search_items`, `get_item`, `add_item`, `edit_item`, `delete_item`

### Recommended MCP server config

Use this server entry in your MCP client config:

```json
{
  "mcpServers": {
    "stashdog": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://gmchczeyburroiyzefie.supabase.co/functions/v1/mcp-server/mcp"
      ]
    }
  }
}
```

After the first connection attempt, complete the OAuth browser flow.

## Helper Commands (mcporter)

You can invoke tools directly with `mcporter`:

```bash
# 1) Trigger OAuth and connect
mcporter auth "https://gmchczeyburroiyzefie.supabase.co/functions/v1/mcp-server/mcp"

# 2) List items
mcporter call "https://gmchczeyburroiyzefie.supabase.co/functions/v1/mcp-server/mcp/list_items" limit=25 offset=0 include_archived=false include_deleted=false

# 3) Search items
mcporter call "https://gmchczeyburroiyzefie.supabase.co/functions/v1/mcp-server/mcp/search_items" query="wrench" limit=20

# 4) Add an item
mcporter call "https://gmchczeyburroiyzefie.supabase.co/functions/v1/mcp-server/mcp/add_item" name="Socket Set" description="Metric sockets" tags='["tools","garage"]'
```

## Tool Reference

- `list_items(limit, offset, include_archived, include_deleted)`
- `search_items(query, limit)`
- `get_item(item_id)`
- `add_item(name, description?, tags?, container_id?, is_storage?)`
- `edit_item(item_id, name?, description?, tags?, is_archived?)`
- `delete_item(item_id)`
