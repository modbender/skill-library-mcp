---
name: notion
description: Notion API for creating and managing pages, databases, blocks, relations, rollups, and multi-workspace profiles via the notioncli CLI tool.
homepage: https://github.com/JordanCoin/notioncli
metadata:
  openclaw:
    emoji: "📝"
    requires:
      env: ["NOTION_API_KEY"]
    primaryEnv: NOTION_API_KEY
    install: "npm install -g @jordancoin/notioncli"
---

# notioncli — Notion API Skill

A powerful CLI for the Notion API. Query databases, manage pages, add comments, and automate your workspace from the terminal. Built for AI agents and humans alike.

## Setup

```bash
npm install -g notioncli
notion init --key $NOTION_API_KEY
```

The `init` command saves your API key and **auto-discovers all databases** shared with your integration. Each database gets an alias (a short slug derived from the database title) so you never need to type raw UUIDs.

> **Tip:** In Notion, you must share each database with your integration first: open the database → ••• menu → Connections → Add your integration.

## Auto-Aliases

When you run `notion init`, every shared database is automatically assigned a slug alias:

```
Found 3 databases:

  ✅ projects                   → Projects
  ✅ tasks                      → Tasks  
  ✅ reading-list               → Reading List
```

You can then use `projects` instead of `a1b2c3d4-e5f6-...` everywhere. Manage aliases manually with:

```bash
notion alias list                  # Show all aliases
notion alias add mydb <db-id>     # Add a custom alias
notion alias rename old new        # Rename an alias
notion alias remove mydb           # Remove an alias
```

## Commands Reference

### Database Discovery

```bash
notion dbs                         # List all databases shared with your integration
notion alias list                  # Show configured aliases with IDs
```

### Querying Data

```bash
notion query tasks                                     # Query all rows
notion query tasks --filter Status=Active              # Filter by property
notion query tasks --sort Date:desc                    # Sort results
notion query tasks --filter Status=Active --limit 10   # Combine options
notion query tasks --output csv                        # CSV output
notion query tasks --output yaml                       # YAML output
notion query tasks --output json                       # JSON output
notion --json query tasks                              # JSON (shorthand)
```

**Output formats:**
- `table` — formatted ASCII table (default)
- `csv` — header row + comma-separated values
- `json` — full API response as JSON
- `yaml` — simple key/value YAML format

### Creating Pages

```bash
notion add tasks --prop "Name=Buy groceries" --prop "Status=Todo"
notion add projects --prop "Name=New Feature" --prop "Priority=High" --prop "Due=2026-03-01"
```

Multiple `--prop` flags for multiple properties. Property names are case-insensitive and matched against the database schema.

### Updating Pages

By page ID:
```bash
notion update <page-id> --prop "Status=Done"
notion update <page-id> --prop "Priority=Low" --prop "Notes=Updated by CLI"
```

By alias + filter (zero UUIDs):
```bash
notion update tasks --filter "Name=Ship feature" --prop "Status=Done"
notion update workouts --filter "Name=LEGS #5" --prop "Notes=Great session"
```

### Reading Pages & Content

By page ID:
```bash
notion get <page-id>               # Page properties
notion blocks <page-id>            # Page content (headings, text, lists, etc.)
```

By alias + filter:
```bash
notion get tasks --filter "Name=Ship feature"
notion blocks tasks --filter "Name=Ship feature"
```

### Deleting (Archiving) Pages

```bash
notion delete <page-id>                              # By page ID
notion delete tasks --filter "Name=Old task"         # By alias + filter
notion delete workouts --filter "Date=2026-02-09"    # By alias + filter
```

### Relations & Rollups

```bash
notion relations tasks --filter "Name=Ship feature"           # See linked pages with titles
notion relations projects --filter "Name=Launch CLI"          # Explore connections
```

Relations are automatically resolved to page titles in `get` output. Rollups are parsed into numbers, dates, or arrays instead of raw JSON.

### Blocks CRUD

```bash
notion blocks tasks --filter "Name=Ship feature"              # View page content
notion blocks tasks --filter "Name=Ship feature" --ids        # View with block IDs
notion append tasks "New paragraph" --filter "Name=Ship feature"  # Append block
notion block-edit <block-id> "Updated text"                   # Edit a block
notion block-delete <block-id>                                # Delete a block
```

Use `--ids` to get block IDs, then target specific blocks with `block-edit` or `block-delete`.

### Appending Content

```bash
notion append <page-id> "Meeting notes: discussed Q2 roadmap"
notion append tasks "Status update: phase 1 complete" --filter "Name=Ship feature"
```

Appends a paragraph block to the page.

### Users

```bash
notion users                       # List all workspace users
notion user <user-id>              # Get details for a specific user
```

### Comments

```bash
notion comments <page-id>                                      # By page ID
notion comments tasks --filter "Name=Ship feature"             # By alias + filter
notion comment <page-id> "Looks good, shipping this!"          # By page ID
notion comment tasks "AI review complete ✅" --filter "Name=Ship feature"  # By alias + filter
```

### Page Inspector

```bash
notion props tasks --filter "Name=Ship feature"    # Quick property dump
notion me                                          # Show bot identity and owner
```

### Database Management

```bash
notion db-create <parent-page-id> "New DB" --prop "Name:title" --prop "Status:select"
notion db-update tasks --add-prop "Rating:number"      # Add a column
notion db-update tasks --remove-prop "Old Column"      # Remove a column
notion db-update tasks --title "Renamed DB"            # Rename database
notion templates tasks                                 # List page templates
```

### Moving Pages

```bash
notion move tasks --filter "Name=Done task" --to archive     # Move by alias
notion move tasks --filter "Name=Done task" --to <page-id>   # Move to page
```

### File Uploads

```bash
notion upload tasks --filter "Name=Ship feature" ./report.pdf
notion upload <page-id> ./screenshot.png
```

Supports images, PDFs, text files, documents. MIME types auto-detected from extension.

### Search

```bash
notion search "quarterly report"   # Search across all pages and databases
```

### JSON Output

Add `--json` before any command to get the raw Notion API response:

```bash
notion --json query tasks
notion --json get <page-id>
notion --json users
notion --json comments <page-id>
```

## Common Patterns for AI Agents

### 1. Discover available databases

```bash
notion dbs
notion alias list
```

### 2. Query and filter data

```bash
notion query tasks --filter Status=Active --sort Date:desc
notion --json query tasks --filter Status=Active    # Parse JSON programmatically
notion query tasks --output csv                     # CSV for spreadsheet tools
```

### 3. Create a new entry

```bash
notion add tasks --prop "Name=Review PR #42" --prop "Status=Todo" --prop "Priority=High"
```

### 4. Update an existing entry (zero UUIDs)

```bash
# By alias + filter — no page ID needed
notion update tasks --filter "Name=Review PR #42" --prop "Status=Done"

# Or by page ID if you already have it
notion update <page-id> --prop "Status=Done"
```

### 5. Read page content (zero UUIDs)

```bash
# By alias + filter
notion get tasks --filter "Name=Review PR #42"
notion blocks tasks --filter "Name=Review PR #42"

# Or by page ID
notion get <page-id>
notion blocks <page-id>
```

### 6. Append notes to a page

```bash
notion append tasks "Status update: completed phase 1" --filter "Name=Review PR #42"
notion append <page-id> "Status update: completed phase 1"
```

### 7. Collaborate with comments

```bash
notion comments tasks --filter "Name=Review PR #42"              # Check existing
notion comment tasks "AI review complete ✅" --filter "Name=Review PR #42"  # Add comment

# Or by page ID
notion comments <page-id>
notion comment <page-id> "AI review complete ✅"
```

### 8. Delete by alias + filter

```bash
notion delete tasks --filter "Name=Old task"
notion delete workouts --filter "Date=2026-02-09"
```

### 9. Manage database schema

```bash
notion db-update tasks --add-prop "Priority:select"    # Add column
notion db-update tasks --remove-prop "Old Field"       # Remove column
notion db-create <parent-page-id> "New DB" --prop "Name:title" --prop "Status:select"
```

### 10. Move pages and upload files

```bash
notion move tasks --filter "Name=Done" --to archive
notion upload tasks --filter "Name=Ship feature" ./report.pdf
```

### 11. Inspect and debug

```bash
notion me                                       # Check integration identity
notion props tasks --filter "Name=Ship feature" # Quick property dump
notion templates tasks                          # List available templates
```

## Property Type Reference

When using `--prop key=value`, the CLI auto-detects the property type from the database schema:

| Type | Example Value | Notes |
|------|-------------|-------|
| `title` | `Name=Hello World` | Main title property |
| `rich_text` | `Notes=Some text` | Plain text content |
| `number` | `Amount=42.5` | Numeric values |
| `select` | `Status=Active` | Single select option |
| `multi_select` | `Tags=bug,urgent` | Comma-separated options |
| `date` | `Due=2026-03-01` | ISO 8601 date string |
| `checkbox` | `Done=true` | `true`, `1`, or `yes` |
| `url` | `Link=https://example.com` | Full URL |
| `email` | `Contact=user@example.com` | Email address |
| `phone_number` | `Phone=+1234567890` | Phone number string |
| `status` | `Status=In Progress` | Status property |

## Multi-Workspace Profiles

Manage multiple Notion accounts from one CLI:

```bash
notion workspace add work --key ntn_work_key       # Add workspace
notion workspace add personal --key ntn_personal    # Add another
notion workspace list                               # Show all
notion workspace use work                           # Switch active
notion workspace remove old                         # Remove one

# Per-command override
notion query tasks --workspace personal
notion -w work add projects --prop "Name=Q2 Plan"

# Init with workspace
notion init --workspace work --key ntn_work_key
```

Aliases are scoped per workspace. Old single-key configs auto-migrate to a "default" workspace.

## Notion API 2025 — Dual IDs

The Notion API (2025-09-03) uses dual IDs for databases: a `database_id` and a `data_source_id`. notioncli handles this automatically — when you run `notion init` or `notion alias add`, both IDs are discovered and stored. You never need to think about it.

## Troubleshooting

- **"No Notion API key found"** — Run `notion init --key ntn_...` or `export NOTION_API_KEY=ntn_...`
- **"Unknown database alias"** — Run `notion alias list` to see available aliases, or `notion init` to rediscover
- **"Not found" errors** — Make sure the database/page is shared with your integration in Notion
- **Filter/sort property not found** — Property names are case-insensitive; run `notion --json query <alias> --limit 1` to see available properties
