# Decision Topology Schema v2

## Tree File

Each exploration is stored as a JSON file in the trees directory.

**Filename format:** `{YYYY-MM-DD}-{short-topic-slug}.json`

### Top-Level Structure

```json
{
  "version": "2",
  "topic": "Short description of the core question",
  "created": "2026-02-24T14:30:00.000Z",
  "updated": "2026-02-24T15:45:00.000Z",
  "root_id": "a1b2c3",
  "active_id": "d4e5f6",
  "nodes": { }
}
```

| Field | Type | Description |
|---|---|---|
| `version` | string | Schema version, currently `"2"` |
| `topic` | string | One-line description of the exploration |
| `created` | string (ISO 8601) | When the tree was initialized |
| `updated` | string (ISO 8601) | Last modification timestamp |
| `root_id` | string | ID of the root node |
| `active_id` | string | ID of the currently active node |
| `nodes` | object | Map of node ID to node object |

## Node Schema

```json
{
  "id": "a1b2c3",
  "parent_id": null,
  "type": "root",
  "summary": "What business to build?",
  "reasoning": "Core question driving the exploration",
  "killed_by": null,
  "children": ["d4e5f6"],
  "sources": [],
  "concepts": ["business", "software", "ai"],
  "weight": 1,
  "timestamp": "2026-02-24T14:30:00.000Z",
  "status": "active"
}
```

| Field | Type | Description |
|---|---|---|
| `id` | string | 6-char hex hash, unique within tree |
| `parent_id` | string or null | Parent node. Null only for root. |
| `type` | enum | `root`, `proposal`, `pivot`, `merge` |
| `summary` | string | One-line description |
| `reasoning` | string | 1-2 sentences on why |
| `killed_by` | string or null | Rejection reason when branch killed |
| `children` | string[] | Child node IDs |
| `sources` | string[] | For merge nodes: contributing node IDs |
| `concepts` | string[] | Short keyword tags for cross-tree linking |
| `weight` | number | Auto-set to number of distinct trees sharing this node's concepts (1 = single-tree, 2+ = cross-tree) |
| `timestamp` | string (ISO 8601) | Creation time |
| `status` | enum | `active`, `dead`, `merged` |

## Node Types

- **root** — core topic, one per tree, always active
- **proposal** — a direction or idea proposed by the agent
- **pivot** — new direction emerging from a rejection or redirection
- **merge** — insight combining elements from multiple branches

## Status Transitions

```
active --> dead       (kill-branch)
active --> merged     (merge)
dead   --> (terminal, but can be forked)
merged --> (terminal)
```

## Commands

| Command | Args | Description |
|---|---|---|
| `init` | `{topic}` | Create new tree |
| `add-node` | `{file, parent_id, type, summary, reasoning?, concepts?}` | Add node |
| `kill-branch` | `{file, node_id, reason}` | Kill branch + descendants |
| `merge` | `{file, source_ids, summary, reasoning?, concepts?}` | Merge branches |
| `render` | `{file}` | ASCII tree |
| `export` | `{file}` | Mermaid diagram |
| `fork` | `{file, node_id, summary?, reasoning?}` | Branch from any node |
| `list` | (none) | List all trees |
| `stats` | `{file}` | Tree statistics |
| `associate` | `{query}` | Find matching tree by topic similarity |
| `analyze` | (none) | Cross-tree concept analysis (rebuilds index, updates all companions) |
| `concept` | `{name}` or `{list:true}` or `{orphans:true}` | Query the concept index |
| `rebuild-index` | (none) | Rebuild concept index from all trees and update companions |

## Concept Index

Stored at `{trees_dir}/concepts.json`. Automatically maintained on every tree save. Maps concept names to all nodes across all trees that reference them.

- Updated incrementally on every `saveTree()` call
- Full rebuild via `rebuild-index` or `analyze`
- Enables instant reverse-lookup: concept -> nodes -> trees
- Drives `## Related trees` section in companion `.md` files (uses `[[wikilinks]]`)
- Drives `weight` field on nodes (set to cross-tree count)
