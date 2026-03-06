---
name: ghost-catalog
description: >-
  Scan, tag, validate, and catalog files using the Ghost Catalog semantic file header system (SOM-XXX-NNNN-vX.X.X).
  Use when: discovering untagged files, onboarding to a new codebase, maintaining catalog compliance,
  searching for files by category/tag/agent, or generating compliance reports.
  Operates on the local file system with a SQLite catalog database.
user-invocable: true
disable-model-invocation: false
---

# Ghost Catalog Skill

Manage semantic file headers and maintain the Ghost Catalog database for any workspace.

## Header Format (SOM File ID)

Every cataloged file gets a semantic header in the first 20 lines:

```
# file_id: SOM-XXX-NNNN-vX.X.X
# name: filename.ext
# description: What this file does
# project_id: PROJECT-NAME
# category: script | doc | config | schema | component | test | data | style
# tags: [tag1, tag2, tag3]
# created: YYYY-MM-DD
# modified: YYYY-MM-DD
# version: X.X.X
# agent_id: AGENT-DROID-001
```

Comment style adapts to file type:
- Python/Shell/YAML/TOML: `#` prefix
- JavaScript/TypeScript/Go/Rust/C: `//` prefix inside `/* ... */` block
- HTML/XML: `<!-- ... -->` block
- Markdown: `<!-- ... -->` HTML comment block
- CSS: `/* ... */` block
- SQL: `--` prefix

### File ID Schema: `SOM-XXX-NNNN-vX.X.X`

| Segment | Meaning | Examples |
|---------|---------|----------|
| `SOM` | Somacosf namespace (constant) | `SOM` |
| `XXX` | 3-letter category code | `SCR` (script), `DOC` (doc), `CFG` (config), `SCH` (schema), `CMP` (component), `TST` (test), `DAT` (data), `STY` (style), `LIB` (library), `API` (api route), `UTL` (utility), `HKS` (hooks) |
| `NNNN` | 4-digit sequential number | `0001`, `0042`, `0338` |
| `vX.X.X` | Semantic version | `v1.0.0`, `v2.1.3` |

### Category Codes

| Code | Category | File Types |
|------|----------|------------|
| `SCR` | Script | `.py`, `.sh`, `.ps1`, `.bat` |
| `DOC` | Document | `.md`, `.txt`, `.rst` |
| `CFG` | Config | `.json`, `.yaml`, `.yml`, `.toml`, `.env`, `.ini` |
| `SCH` | Schema | `.prisma`, `.graphql`, `.sql` |
| `CMP` | Component | `.tsx`, `.jsx`, `.vue`, `.svelte` |
| `TST` | Test | `*.test.*`, `*.spec.*` |
| `DAT` | Data | `.csv`, `.json` (data files), `.db` |
| `STY` | Style | `.css`, `.scss`, `.less` |
| `LIB` | Library | `.ts`, `.js` (lib modules) |
| `API` | API Route | `route.ts`, `route.js` (Next.js API routes) |
| `UTL` | Utility | Helper/utility modules |
| `HKS` | Hooks | React hooks, git hooks |

## Catalog Database

The catalog lives at `data/ghost-catalog.db` (SQLite). Schema:

```sql
CREATE TABLE IF NOT EXISTS file_catalog (
    file_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    path TEXT NOT NULL,
    project_id TEXT,
    category TEXT,
    version TEXT,
    created TEXT,
    modified TEXT,
    agent_id TEXT,
    execution TEXT,
    checksum TEXT,
    last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS file_tags (
    file_id TEXT,
    tag TEXT,
    PRIMARY KEY (file_id, tag),
    FOREIGN KEY (file_id) REFERENCES file_catalog(file_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS agent_registry (
    id TEXT PRIMARY KEY,
    name TEXT,
    model TEXT,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_category ON file_catalog(category);
CREATE INDEX IF NOT EXISTS idx_project ON file_catalog(project_id);
CREATE INDEX IF NOT EXISTS idx_agent ON file_catalog(agent_id);
CREATE INDEX IF NOT EXISTS idx_tags ON file_tags(tag);
```

## Commands

When the user invokes `/ghost-catalog`, determine which operation to perform based on their request. Default to `scan` if no specific command is given.

### 1. `scan` (default)

Scan the workspace for all source files. For each file:
1. Check if it already has a SOM header (look for `file_id: SOM-` in first 20 lines)
2. If header exists: parse and validate it, update the catalog DB
3. If no header: report it as untagged

Output a summary table:
```
Scanned: 150 files
Tagged:   42 files (28%)
Untagged: 108 files
Errors:   0
```

**Ignore system** (layered, merged at scan time):

1. `.ghost_ignore` (primary) -- Ghost Catalog's own ignore file, lives at project root. Follows `.gitignore` syntax. This is the canonical source of what to skip.
2. `.gitignore` (inherited) -- automatically merged; anything git ignores, Ghost Catalog ignores too.
3. Hardcoded fallbacks -- if neither file exists, use: `.git/`, `node_modules/`, `.next/`, `.vercel/`, `__pycache__/`, `.venv/`, `dist/`, `build/`, `.factory/`

When scanning, parse `.ghost_ignore` and `.gitignore` into a combined exclusion set. Only scan files that survive both filters. The goal: **catalog project files only** -- no dependencies, no build artifacts, no binaries, no secrets, no lock files.

### 2. `tag <path|pattern>`

Apply a Ghost Catalog header to one or more files:

1. Read the file content
2. Determine the category from file extension and location
3. Query the catalog DB for the next available sequence number in that category
4. Generate the header with appropriate comment syntax
5. Prepend the header to the file (preserve existing content)
6. Insert into the catalog DB

When tagging multiple files, show a preview table first and ask for confirmation before applying.

### 3. `validate`

Check all tagged files for header compliance:
- Required fields present: `file_id`, `name`, `description`, `category`, `version`, `created`, `modified`
- File ID format valid: `SOM-XXX-NNNN-vX.X.X`
- Version in file_id matches version field
- Filename in header matches actual filename
- No duplicate file IDs

Output a validation report with pass/warn/fail for each file.

### 4. `search <query>`

Search the catalog by any field:
- `search proxy` - fuzzy match on name/description
- `search --category script` - filter by category
- `search --tag opentelemetry` - filter by tag
- `search --agent AGENT-CLAUDE-002` - filter by agent

Display results as a formatted table with file_id, name, category, and path.

### 5. `info <file_id>`

Show detailed metadata for a specific file from the catalog DB.

### 6. `stats`

Show catalog statistics:
- Total files, tagged vs untagged
- Breakdown by category
- Top tags
- Agent activity
- Last sync time

### 7. `report`

Generate a full compliance report in markdown format, saved to `docs/ghost-catalog-report.md`.

## Implementation Notes

- Use Python 3 with `sqlite3` stdlib for database operations
- For scanning, use the Glob and Read tools rather than spawning processes
- When generating headers, always check what comment style the file uses
- Sequence numbers are global per category (not per project)
- The catalog DB should be created at `data/ghost-catalog.db` if it doesn't exist
- Always use `AGENT-DROID-001` as the agent_id when this skill applies headers
- Version starts at `v1.0.0` for new files
- `modified` date is always today's date when applying or updating headers
- `created` date is preserved if already set, otherwise today's date

## Verification

After any write operation (tag, validate --fix), re-read the modified files to confirm headers were applied correctly. Report any failures.

## Auto-Invocation Guidance

This skill should be considered when:
- The user asks about file organization, cataloging, or headers
- A scan reveals many untagged files and the user wants to fix compliance
- The user creates new files and wants them cataloged
- The user asks "what files are in this project" or "show me the catalog"
