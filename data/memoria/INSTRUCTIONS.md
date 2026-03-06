# Memoria -- Usage Instructions

Structured memory system for AI agents. Local markdown vault with two-way Notion sync.

---

## 1. Installation

```bash
npm install -g @kitakitsune/memoria
```

Verify the install:

```bash
memoria --version
```

### Requirements

- Node.js 18 or later

---

## 2. Initialize a Vault

Create a new vault directory with category folders and configuration:

```bash
memoria init ~/memory --name my-brain
```

This creates the following structure:

```
~/memory/
  .memoria.json           # vault configuration
  decisions/
  preferences/
  lessons/
  facts/
  commitments/
  people/
  projects/
  inbox/
  sessions/
    handoffs/
  observations/
```

You can also set the `MEMORIA_VAULT` environment variable so commands find your vault automatically:

```bash
export MEMORIA_VAULT=~/memory
```

---

## 3. Storing Memories

### By type (recommended)

Use `remember` to store a typed memory. The type determines which category folder it goes into.

```bash
memoria remember <type> "<title>" --content "<body>" [--tags "tag1,tag2"]
```

Available types:

| Type           | Category folder | Use for                          |
|----------------|-----------------|----------------------------------|
| `fact`         | `facts/`        | Raw information, data points     |
| `decision`     | `decisions/`    | Choices made with reasoning      |
| `lesson`       | `lessons/`      | Insights, patterns learned       |
| `commitment`   | `commitments/`  | Promises, goals, obligations     |
| `preference`   | `preferences/`  | Likes, dislikes, preferences     |
| `relationship` | `people/`       | People, connections, dynamics    |
| `project`      | `projects/`     | Active work, ongoing efforts     |

Examples:

```bash
memoria remember decision "Use PostgreSQL" \
  --content "Chosen for JSONB support and reliability. Evaluated against MySQL and SQLite." \
  --tags "database,infrastructure"

memoria remember lesson "Cache invalidation" \
  --content "TTL-based expiry is simpler and more predictable than event-driven invalidation."

memoria remember fact "Node 22 LTS" \
  --content "Node.js 22 is the current LTS release as of 2026."

memoria remember commitment "Ship v2 by March" \
  --content "Committed to stakeholders for Q1 delivery."
```

### By explicit category

Use `store` to place a document in any category folder directly:

```bash
memoria store <category> "<title>" --content "<body>" [--tags "tag1,tag2"]
```

Example:

```bash
memoria store inbox "meeting-notes-feb" \
  --content "Discussed Q2 roadmap and hiring plan." \
  --tags "meetings,planning"
```

### Overwriting

By default, storing a document with the same title in the same category will fail. Add `--overwrite` to replace it:

```bash
memoria remember decision "Use PostgreSQL" \
  --content "Updated: switching to CockroachDB instead." \
  --overwrite
```

---

## 4. Retrieving Memories

### List all documents

```bash
memoria list
```

### List by category

```bash
memoria list decisions
memoria list lessons
```

### Filter by tag

```bash
memoria list --tags "database"
```

### Get a specific document

Use the path format `category/slug`:

```bash
memoria get decisions/use-postgresql
```

---

## 5. Searching

Full-text search across all documents using TF-IDF ranking:

```bash
memoria search "postgresql"
memoria search "cache invalidation"
```

Options:

```bash
# Limit results
memoria search "auth" --limit 5

# Filter by category
memoria search "token" --category decisions
```

---

## 6. Session Lifecycle

Sessions track what you are working on across agent interactions. The lifecycle is: **wake** -> **checkpoint** (repeat) -> **sleep**.

### Start a session

```bash
memoria wake
```

This loads recent handoffs and memories to restore context. If a session is already active, it will tell you.

### Save a checkpoint

Periodically save what you are working on:

```bash
memoria checkpoint --working-on "auth module" --focus "token refresh edge cases"
```

### End a session

Write a handoff document summarizing what was done and what comes next:

```bash
memoria sleep "Finished auth module planning" --next "Implement token refresh and deploy to staging"
```

The handoff is saved to `sessions/handoffs/YYYY-MM-DD.md` and will be shown on the next `wake`.

### Check status

```bash
memoria status
```

Shows vault stats, session state, and Notion connection status.

---

## 7. Notion Integration

Sync your local vault to Notion for a rich browsing and editing UI. Local files remain the source of truth.

### Step 1: Create a Notion integration

1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations).
2. Click "New integration".
3. Give it a name (e.g. "Memoria").
4. Copy the **Internal Integration Secret** (starts with `ntn_`).

### Step 2: Create a root page

1. Create a new page in Notion (e.g. "Memoria Vault").
2. Click the `...` menu in the top-right, then "Add connections", and select your integration.
3. Copy the page ID from the URL. It is the 32-character hex string after the workspace name:
   `https://notion.so/My-Page-`**`abc123def456...`**

### Step 3: Configure Memoria

```bash
memoria setup-notion --token ntn_your_token_here --page abc123def456789...
```

This enables **auto-sync**: every `memoria remember` and `memoria store` call will automatically push to Notion after saving locally. No separate sync step needed.

### Auto-sync behavior

Once Notion is configured, `remember` and `store` save locally **and** push to Notion in one step. You can control this per-call:

```bash
# Force sync even if auto-sync is off
memoria remember fact "something" --content "..." --sync

# Skip sync for this one call
memoria remember fact "draft" --content "..." --no-sync
```

### Manual sync

For bulk operations or pulling Notion edits back to local:

```bash
# Push all local changes to Notion
memoria sync --push

# Pull Notion changes to local
memoria sync --pull

# Two-way sync (push then pull)
memoria sync

# Preview what would change
memoria sync --dry-run
```

### Sync behavior

| Scenario | Default behavior |
|----------|-----------------|
| `remember` / `store` with Notion configured | Auto-pushes to Notion |
| New local file | Created as a Notion page |
| Updated local file | Notion page updated |
| New Notion page | Pulled to local as markdown |
| Updated Notion page | Local file updated |
| Both sides changed | Local wins (use `--prefer-notion` to override) |
| Local file deleted | Notion page kept (use `--delete-remote` to remove) |

### Notion data model

- One **Notion database** is created per category (decisions, lessons, facts, etc.) under your root page.
- Each document becomes a **Notion page** in the corresponding database.
- Frontmatter fields map to database properties:

| Frontmatter | Notion property | Type |
|-------------|----------------|------|
| `title`     | Title          | Title |
| `type`      | Type           | Select |
| `tags`      | Tags           | Multi-select |
| `created`   | Created        | Date |
| `updated`   | Updated        | Date |

- The markdown body is converted to Notion blocks (paragraphs, headings, lists, code blocks, quotes, dividers).

---

## 8. Agent Integration

Add the following block to your `AGENTS.md`, `.cursorrules`, or system prompt. It tells an AI agent how to use Memoria, what to capture, and when to do it.

```markdown
## Memoria

- Set `MEMORIA_VAULT=~/memory` (or pass `-v ~/memory` on every command).
- Run `memoria wake` at session start to restore context.
- Run `memoria checkpoint --working-on "<task>"` during long tasks.
- Run `memoria sleep "<summary>" --next "<next steps>"` before ending.
- Before complex decisions, run `memoria search "<query>"` first.
- Store important information immediately -- do not wait to be asked:
  - Facts the human shares (name, location, health, settings, credentials context)
  - Decisions made and why
  - Preferences expressed ("I prefer...", "I always...", "I never...")
  - Lessons learned from mistakes or discoveries
  - Commitments, goals, or deadlines
  - People mentioned with context
  - Projects being worked on
  - Use: `memoria remember <type> "<title>" --content "<details>"`
  - Types: `fact`, `decision`, `preference`, `lesson`, `commitment`, `relationship`, `project`
- After storing, always sync: `memoria sync --push`
- If in doubt whether something is worth storing, store it.

### Proactive capture triggers

Listen for these patterns and store immediately:

- "I always...", "I never...", "I prefer..." -> `preference`
- "Let's go with...", "We decided...", "The plan is..." -> `decision`
- "I learned that...", "Turns out...", "The trick is..." -> `lesson`
- "My name is...", "I take...", "I live in...", "I work at..." -> `fact`
- "I need to...", "I promised...", "By next week..." -> `commitment`
- "Talk to Alice about...", "Bob said..." -> `relationship`
- "We're building...", "The project is..." -> `project`
```

---

## 9. Document Format

Every document is a markdown file with YAML frontmatter:

```markdown
---
title: Use PostgreSQL
type: decision
tags:
  - database
  - infrastructure
created: 2026-02-21T10:00:00Z
updated: 2026-02-21T10:00:00Z
---
Chosen for JSONB support and reliability. Evaluated against MySQL and SQLite.
```

The filename is a slug of the title (e.g. `use-postgresql.md`) stored in the category folder.

---

## 10. CLI Quick Reference

```
memoria init <path> [--name <name>]              Initialize a vault
memoria remember <type> <title> [options]         Store typed memory (auto-syncs)
memoria store <category> <title> [options]        Store in category (auto-syncs)
memoria search <query> [options]                  Search documents
memoria list [category] [--tags <t>]              List documents
memoria get <id>                                  Get a document
memoria wake                                      Start session
memoria sleep <summary> [--next <steps>]          End session
memoria checkpoint [--working-on <t>]             Mid-session save
memoria status                                    Vault info
memoria setup-notion --token <t> --page <id>      Configure Notion + enable auto-sync
memoria sync [--push] [--pull] [--dry-run]        Manual sync with Notion
memoria --version                                 Show version
memoria --help                                    Show help
```

Global options available on most commands:

- `-v, --vault <path>` -- specify vault path (overrides `MEMORIA_VAULT`)
- `--sync` -- force push to Notion after this operation
- `--no-sync` -- skip auto-sync for this operation
