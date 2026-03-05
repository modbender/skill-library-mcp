# Nemo — OpenClaw Skill

Search engine for MCP tools and agent skills. Search 790+ MCP server tools and 760+ agent skills in one place, call remote MCP tools, and get full skill instructions via MCP or HTTP API.

**Base URL:** `https://nemo.25chenghua.workers.dev`

## Install

Copy this folder into your OpenClaw skills directory:

```bash
cp -r openclaw/ ~/.openclaw/skills/nemo/
```

Or symlink it:

```bash
ln -s "$(pwd)/openclaw" ~/.openclaw/skills/nemo
```

Then update `skill.yaml` with your actual Nemo endpoint URL.

## Verify

```bash
openclaw skills list        # should show "nemo"
openclaw skills test nemo   # run a quick test
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `search_tools` | Search for MCP tools and agent skills by keyword. Returns compact results by default (tool name, server, title). Set detail='full' to include descriptions and input schemas. |
| `call_tool` | Call a tool on a remote MCP server by endpoint, tool name, and arguments. Tracks latency and logs usage. |
| `get_skill` | Get full instructions for an agent skill. Returns the complete SKILL.md content and install command. |

## HTTP API (Alternative Access)

You can also access Nemo's features directly via HTTP without MCP:

### Search

Find MCP tools and agent skills by keyword.

```bash
curl "https://nemo.25chenghua.workers.dev/api/search?q=QUERY"
```

| Param | Default | Description |
|-------|---------|-------------|
| `q` | required | Search query |
| `limit` | 5 | Max results (1-20) |
| `detail` | compact | `compact` or `full` (includes descriptions, schemas) |
| `source` | all | `all`, `mcp`, or `skills` |

Each result has a `type` field: `"mcp_tool"` or `"skill"`.

### Get Skill Instructions

Load full SKILL.md content for a skill found via search.

```bash
curl "https://nemo.25chenghua.workers.dev/api/skill/SKILL_NAME"
```

Add `?repo=owner/repo` if multiple skills share the same name.

Returns the complete instructions, install command, and metadata.

### Call a Remote MCP Tool

Proxy a tool call to any indexed MCP server.

```bash
curl -X POST "https://nemo.25chenghua.workers.dev/api/call" \
  -H "Content-Type: application/json" \
  -d '{"endpoint": "SERVER_URL", "tool": "TOOL_NAME", "args": {}}'
```

Use the `serverEndpoint` and `toolName` from search results.

## Workflow

1. Search: `curl ".../api/search?q=file+conversion"`
2. If result is `type: "skill"` → get instructions: `curl ".../api/skill/SKILL_NAME"` → follow them
3. If result is `type: "mcp_tool"` → call it: `POST .../api/call` with `endpoint`, `tool`, `args`
