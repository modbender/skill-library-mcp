# openclaw-memory-docs

OpenClaw plugin: **Documentation Memory**.

A conservative, audit-friendly memory store for project documentation and long-lived notes.

- No automatic capture - only explicit `/remember-doc` commands store data
- Local JSONL store with local deterministic embeddings (no external services)
- Optional secret redaction (API keys, tokens, private key blocks)
- Tag and project metadata for organization and filtering

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

### `/remember-doc` - Save a memory

```
/remember-doc [--tags t1,t2] [--project name] <text>
```

Stores a documentation memory item. If secrets are detected, they are redacted before storage.

**Flags:**

| Flag | Description |
|------|-------------|
| `--tags t1,t2` | Comma-separated tags (merged with `defaultTags` from config) |
| `--project name` | Associate this item with a project name |

**Examples:**

```
/remember-doc Dubai: decide A vs B, then collect facts, then prepare a tax advisor briefing.
/remember-doc --tags legal,tax --project dubai Tax advisor meeting scheduled for March.
/remember-doc --tags=api --project=backend The /users endpoint requires Bearer auth.
```

### `/search-docs` - Search memories

```
/search-docs [--tags t1,t2] [--project name] <query> [limit]
```

Searches stored memories using semantic-ish similarity. Returns scored results with IDs, tags, and project badges.

**Parameters:**

| Parameter | Description | Default |
|-----------|-------------|---------|
| `query` | Search query text (required) | - |
| `limit` | Max results to return (1-20) | 5 |
| `--tags t1,t2` | Filter results to items matching these tags | - |
| `--project name` | Filter results to items with this project | - |

**Examples:**

```
/search-docs Dubai plan
/search-docs --project=dubai tax advisor 10
/search-docs --tags=api,backend endpoint auth
```

### `/list-docs` - List recent memories

```
/list-docs [--tags t1,t2] [--project name] [limit]
```

Lists the most recent documentation memory items, with IDs, dates, tags, and project badges.

**Parameters:**

| Parameter | Description | Default |
|-----------|-------------|---------|
| `limit` | Max items to return (1-50) | 10 |
| `--tags t1,t2` | Filter to items matching these tags | - |
| `--project name` | Filter to items with this project | - |

**Examples:**

```
/list-docs
/list-docs 20
/list-docs --project=dubai
/list-docs --tags=legal --project=dubai 5
```

### `/forget-doc` - Delete a memory

```
/forget-doc <id>
```

Deletes a documentation memory item by its ID. Use `/list-docs` to find item IDs. Requires auth.

**Example:**

```
/forget-doc a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### `/export-docs` - Export as markdown files

```
/export-docs [--tags t1,t2] [--project name] [path]
```

Exports documentation memories as individual markdown files for git-first workflows. Each file gets YAML frontmatter (id, kind, createdAt, tags, project) and the memory text as body.

**Parameters:**

| Parameter | Description | Default |
|-----------|-------------|---------|
| `path` | Target directory for exported files | `exportPath` config or `~/.openclaw/workspace/memory/docs-export` |
| `--tags t1,t2` | Export only items matching these tags | - |
| `--project name` | Export only items with this project | - |

**File naming:** `YYYY-MM-DD_<shortid>.md` (e.g., `2026-01-15_abc12345.md`)

**Examples:**

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

**Parameters:**

| Parameter | Description | Default |
|-----------|-------------|---------|
| `path` | Source directory containing markdown files | `exportPath` config or `~/.openclaw/workspace/memory/docs-export` |

**Examples:**

```
/import-docs
/import-docs ~/docs/memories
/import-docs /path/to/exported/docs
```

## Tool

### `docs_memory_search`

Available to agents and automations as a tool call.

```json
{
  "query": "Dubai plan A vs B",
  "limit": 5,
  "tags": ["legal"],
  "project": "dubai"
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | yes | Search query text |
| `limit` | number | no | Max results (1-20, default 5) |
| `tags` | string[] | no | Filter results to items matching all given tags |
| `project` | string | no | Filter results to items with this project name |

Returns a `hits` array with `score`, `id`, `createdAt`, `tags`, `project`, and `text` for each match.

## Config

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

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable or disable the plugin |
| `storePath` | string | `~/.openclaw/workspace/memory/docs-memory.jsonl` | Path to the JSONL storage file |
| `dims` | number | `256` | Embedding dimensions (32-2048) |
| `redactSecrets` | boolean | `true` | Redact detected secrets before storage |
| `defaultTags` | string[] | `["docs"]` | Tags automatically added to every saved item |
| `maxItems` | number | `5000` | Maximum items in the store (100-100000) |
| `exportPath` | string | `~/.openclaw/workspace/memory/docs-export` | Default directory for `/export-docs` and `/import-docs` |

## Design Notes

- This plugin intentionally does **not** auto-capture messages.
- If you want automatic capture, use `openclaw-memory-brain` instead.
- Secret redaction covers common patterns: API keys, tokens, private key blocks.
- Embeddings are deterministic and local - no calls to external embedding services.
- Export/import uses a git-friendly format: one markdown file per memory item, with deterministic filenames (`YYYY-MM-DD_<shortid>.md`). Frontmatter contains all metadata, making diffs clean and merge-friendly.
