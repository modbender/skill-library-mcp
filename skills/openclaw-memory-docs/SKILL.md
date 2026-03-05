---
name: openclaw-memory-docs
description: "OpenClaw plugin for documentation-grade memory: explicit capture + local searchable store with safe redaction."
---

# openclaw-memory-docs

This is an **OpenClaw Gateway plugin** (not an agent skill) that provides a conservative, audit-friendly memory store.

It is designed for project documentation and long-lived notes where you care about:
- explicit control over what gets stored
- no accidental storage of secrets
- deterministic, local-first behavior
- tag and project metadata for organization

## What it does

- Adds commands: `/remember-doc`, `/search-docs`, `/list-docs`, `/forget-doc`, `/export-docs`, `/import-docs`
- Adds a search tool: `docs_memory_search`
- Stores entries in a local **JSONL file** (one record per line)
- Uses a deterministic local embedder to enable semantic-ish search without external services
- Optional redaction for common secret formats (API keys, tokens, private key blocks)
- Supports tag and project metadata for filtering and organization

## Install

### ClawHub

```bash
clawhub install openclaw-memory-docs
```

### Dev

```bash
openclaw plugins install -l ~/.openclaw/workspace/openclaw-memory-docs
openclaw gateway restart
```

## Commands

### `/remember-doc` - Save a documentation memory

```
/remember-doc [--tags t1,t2] [--project name] <text>
```

Stores a note as a documentation memory item. Secrets are automatically redacted if `redactSecrets` is enabled (default: true).

- `--tags t1,t2` - Comma-separated tags, merged with `defaultTags` from config
- `--project name` - Associate this item with a project

Examples:

```
/remember-doc Dubai: decide A vs B, then collect facts, then prepare a tax advisor briefing.
/remember-doc --tags legal,tax --project dubai Tax advisor meeting scheduled for March.
/remember-doc --tags=api --project=backend The /users endpoint requires Bearer auth.
```

### `/search-docs` - Search documentation memories

```
/search-docs [--tags t1,t2] [--project name] <query> [limit]
```

Searches stored memories using semantic similarity. Returns scored results showing IDs, tags, and project badges.

- `query` - Search text (required)
- `limit` - Max results, 1-20 (default: 5)
- `--tags t1,t2` - Filter to items matching these tags
- `--project name` - Filter to items with this project

Examples:

```
/search-docs Dubai plan
/search-docs --project=dubai tax advisor 10
/search-docs --tags=api,backend endpoint auth
```

### `/list-docs` - List recent documentation memories

```
/list-docs [--tags t1,t2] [--project name] [limit]
```

Lists the most recent documentation memory items with IDs, dates, tags, and project badges.

- `limit` - Max items, 1-50 (default: 10)
- `--tags t1,t2` - Filter to items matching these tags
- `--project name` - Filter to items with this project

Examples:

```
/list-docs
/list-docs 20
/list-docs --project=dubai
/list-docs --tags=legal --project=dubai 5
```

### `/forget-doc` - Delete a documentation memory

```
/forget-doc <id>
```

Deletes a memory item by its full ID (shown by `/list-docs`). Requires auth.

### `/export-docs` - Export as markdown files

```
/export-docs [--tags t1,t2] [--project name] [path]
```

Exports documentation memories as individual markdown files for git-first workflows. Each file has YAML frontmatter (id, kind, createdAt, tags, project) and the memory text as body.

- `path` - Target directory (default: `exportPath` config or `~/.openclaw/workspace/memory/docs-export`)
- `--tags t1,t2` - Export only items matching these tags
- `--project name` - Export only items with this project

File naming: `YYYY-MM-DD_<shortid>.md`

Examples:

```
/export-docs
/export-docs ~/docs/memories
/export-docs --project=dubai
/export-docs --tags=api --project=backend ~/exports
```

### `/import-docs` - Import from markdown files

```
/import-docs [path]
```

Imports documentation memories from a directory of exported markdown files. Each `.md` file must have YAML frontmatter with `id`, `kind`, and `createdAt` fields (the format produced by `/export-docs`). Requires auth.

Duplicate items (matching by ID) and invalid files are skipped automatically.

- `path` - Source directory (default: `exportPath` config or `~/.openclaw/workspace/memory/docs-export`)

Examples:

```
/import-docs
/import-docs ~/docs/memories
/import-docs /path/to/exported/docs
```

## Tool: `docs_memory_search`

Available to agents and automations as a tool call. Searches documentation memories by query with optional tag and project filtering.

**Input schema:**

```json
{
  "query": "Dubai plan A vs B",
  "limit": 5,
  "tags": ["legal"],
  "project": "dubai"
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | yes | Search query text |
| `limit` | number | no | Max results, 1-20 (default: 5) |
| `tags` | string[] | no | Filter results to items matching all given tags |
| `project` | string | no | Filter results to items with this project name |

**Returns** a `hits` array with `score`, `id`, `createdAt`, `tags`, `project`, and `text` for each match.

## Configuration

```json
{
  "plugins": {
    "entries": {
      "openclaw-memory-docs": {
        "enabled": true,
        "config": {
          "storePath": "~/.openclaw/workspace/memory/docs-memory.jsonl",
          "dims": 256,
          "redactSecrets": true,
          "defaultTags": ["docs"],
          "maxItems": 5000,
          "exportPath": "~/.openclaw/workspace/memory/docs-export"
        }
      }
    }
  }
}
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable or disable the plugin |
| `storePath` | string | `~/.openclaw/...docs-memory.jsonl` | Path to the JSONL storage file |
| `dims` | number | `256` | Embedding dimensions (32-2048) |
| `redactSecrets` | boolean | `true` | Redact detected secrets before storage |
| `defaultTags` | string[] | `["docs"]` | Tags automatically added to every saved item |
| `maxItems` | number | `5000` | Maximum items in the store (100-100000) |
| `exportPath` | string | `~/.openclaw/...docs-export` | Default directory for `/export-docs` and `/import-docs` |

### Notes

- This plugin intentionally does **not** auto-capture messages.
- If you want automatic capture, use `openclaw-memory-brain`.
- Export/import uses a git-friendly format: one markdown file per memory item, with deterministic filenames (`YYYY-MM-DD_<shortid>.md`). Frontmatter contains all metadata, making diffs clean and merge-friendly.
