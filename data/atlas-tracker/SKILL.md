---
name: atlas-tracker
description: Work with Atlas Tracker (RedForester) mindmaps via MCP tools. Use when reading, creating, or updating nodes and branches in Atlas Tracker maps — including navigating map structure, creating solution trees, updating node properties, and managing typed nodes. Requires at_read_branch, at_create_branch, at_update_branch, at_get_node_types, at_read_attachments tools (provided by the Atlas Tracker OpenClaw plugin).
---

# Atlas Tracker Skill

Atlas Tracker (app.redforester.com) is a graph-based knowledge system combining mindmaps, Kanban, and structured properties. This skill covers working with it via the OpenClaw AT plugin tools.

## Setup

This skill requires two components to be installed and running:

### 1. AT MCP Server

A local Node.js server that proxies requests to the Atlas Tracker REST API.

> The AT MCP server is maintained by the Atlas Tracker / RedForester team.  
> Contact **@gmdidro** (Telegram) or visit [app.redforester.com](https://app.redforester.com) to request access.

Once you have the server files:

```bash
cd at-mcp/
yarn install
yarn build

# Run directly
node build/index.js

# Or run as a systemd user service (recommended)
cp at-mcp.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now at-mcp
```

The server listens on `http://localhost:3222` by default.

Required environment variables (set in the service file or `.env`):
```
AT_BASE_URL=https://app.redforester.com/api
AUTH_HEADER=Basic <base64(username:md5(password))>
API_KEY=<your-local-api-key>
PORT=3222
```

### 2. OpenClaw Plugin

Copy the plugin file to your OpenClaw extensions directory:

```bash
mkdir -p ~/.openclaw/extensions/atlas-tracker/
cp index.ts ~/.openclaw/extensions/atlas-tracker/
cp openclaw.plugin.json ~/.openclaw/extensions/atlas-tracker/
```

Then configure the plugin in your `openclaw.json`:

```json
{
  "plugins": {
    "atlas-tracker": {
      "serverUrl": "http://localhost:3222",
      "apiKey": "<your-local-api-key>"
    }
  }
}
```

OpenClaw will hot-reload the plugin automatically. Verify with:
```bash
openclaw status
```
You should see `at_read_branch`, `at_create_branch`, `at_update_branch`, `at_get_node_types`, `at_read_attachments` listed as available tools.

---

## Core Concepts

- **Map** — a mindmap, identified by `mapId` (full UUID)
- **Node** — a single item in the map; has `id`, `title` (HTML), optional `typeId`, `typeProperties`, `children[]`
- **Branch** — a node + all its descendants
- **Node type** — a schema defining available properties (enum, text, htmltext, file, user, date, etc.)
- **Title format** — always HTML: `<p>My title</p>`, never plain text

## Tool URLs

All tools take a `nodeUrl` in format:
```
https://app.redforester.com/mindmap?mapid=<UUID>&nodeid=<UUID>
```
Both `mapid` and `nodeid` must be **full UUIDs** (e.g. `3d7340e8-c763-4c9e-b049-4e900b7cf565`), never partial.

## Workflow

### Reading a branch
Always read before modifying — never assume structure:
```
at_read_branch(nodeUrl) → returns node tree with children, types, properties
```

### Finding the right node
If you don't know a nodeId, search via AT REST API:
```bash
POST /api/search  body: {"query": "...", "map_ids": ["<mapId>"]}
# Returns hits[].id — then at_read_branch each candidate to verify title
```

### Creating branches
```
at_create_branch(parentNodeUrl, data)
```
`data` must include `children: []` even for leaf nodes — required field.

### Updating branches
```
at_update_branch(nodeUrl, delete[], update[], create[])
```
- `create` items: `{parentNodeId, data: {title, typeId?, typeProperties?, children: []}}`
- `update` items: `{id, title?, typeProperties?, customProperties?}`
- All three arrays required (pass `[]` if unused)

## Node Types

Call `at_get_node_types(nodeUrl)` once per map session — types vary per map.
Common types: Идея, Задача, Заметка, Категория, Проект, Этап, Заявка, Лид.

For typed nodes, `typeProperties` keys must exactly match the property names from `at_get_node_types`.

## Critical Rules

1. **Full UUIDs only** — partial IDs (e.g. `b319f356`) will return 404
2. **`children: []` required** — omitting it causes validation error on create
3. **HTML titles** — wrap in `<p>...</p>`; use `<ul><li>...</li></ul>` for lists
4. **Read before write** — always `at_read_branch` first to get current state and node IDs
5. **403 = permission denied** — you can only write nodes owned by your AT account; read access may be broader
6. **Large maps are slow** — avoid full subtree reads on large maps; use search + targeted node reads instead

## Common Patterns

### Add children to existing node
1. `at_read_branch` to get parent nodeId and confirm it exists
2. `at_update_branch` with `create: [{parentNodeId: "<id>", data: {..., children: []}}]`

### Batch create a solution tree
Use `at_create_branch` with nested `children[]` to create the full tree in one call.

### Update node content
1. `at_read_branch` to get current node id and properties
2. `at_update_branch` with `update: [{id, typeProperties: {key: "<html_value>"}}]`

## Reference Files

- **[api-patterns.md](references/api-patterns.md)** — REST API search, auth, node fetch patterns (read when you need to search nodes or call AT API directly)
- **[node-types-guide.md](references/node-types-guide.md)** — property type reference (htmltext, enum, file, user, date, etc.) and how to set them (read when creating/updating typed nodes)
