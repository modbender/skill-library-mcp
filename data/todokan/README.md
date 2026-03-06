# Todokan Skill for OpenClaw

Connect [Todokan](https://todokan.com) to OpenClaw so your agent can read/write tasks and run polling workflows.

## Quick Install (ClawHub)

```bash
clawhub install todokan
```

When prompted, set:
- `TODOKAN_API_KEY` = your Todokan API key (`kb_live_...`)
- `TODOKAN_MCP_URL` = MCP endpoint (default: `https://todokan.com/mcp`)

If your setup uses environment files, export the same variables in your OpenClaw runtime.

## Manual Setup

### 1. Create Todokan API key

1. Log in to [todokan.com](https://todokan.com)
2. Go to **Settings > API Keys**
3. Create a key for planner or worker usage
4. Copy the key

### 2. Configure MCP server

Add a Todokan MCP server entry to your OpenClaw configuration. The skill requires:
- **Transport**: `streamable-http`
- **URL**: `https://todokan.com/mcp` (planner, full CRUD) or `https://todokan.com/mcp-worker` (read + comments)
- **Authentication**: Pass `TODOKAN_API_KEY` via the `Authorization: Bearer` header

Refer to the [OpenClaw MCP docs](https://openclaw.dev/docs/mcp) for how to configure MCP servers in your runtime.

## Recommended Agent Loop

Use `get_events_since` on an interval (for example every 15 minutes):
1. Persist last checkpoint timestamp (`since`)
2. Call `get_events_since`
3. Process returned events
4. Save returned `until` as next checkpoint

For cross-board discovery, use `search_across_habitats` first instead of multiple `list_tasks` calls.

## Key Tools

- `search_across_habitats`: one-call full-text search across habitats/boards/tasks
- `get_events_since`: unified feed (task events, comments, documents)
- `list_tasks`, `get_task`, `update_task`, `add_comment`, `create_document`, `add_document_to_task`

## Endpoints

| Endpoint | Access |
|----------|--------|
| `https://todokan.com/mcp` | Planner (full CRUD) |
| `https://todokan.com/mcp-worker` | Worker (read + comments) |
| `https://staging--todokan.netlify.app/mcp` | Staging planner |

## Troubleshooting

### Authorization required
- Ensure `Authorization: Bearer <key>` is set
- Confirm key and endpoint are from same environment
- Verify key is not revoked

### Tools missing
- Restart OpenClaw after config changes
- Verify MCP connectivity:

```bash
curl -s https://todokan.com/mcp \
  -H "Authorization: Bearer kb_live_..." \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

### Staging
Use `https://staging--todokan.netlify.app/mcp` with a staging key.
