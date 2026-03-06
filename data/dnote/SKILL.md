---
name: dnote
description: Save, retrieve, and manage notes using Dnote CLI. Use when the user wants to capture information, search existing notes, reference saved knowledge, or organize notes into books. Supports adding notes, searching with full-text, viewing books/notes, editing, and removing notes. Perfect for building a personal knowledge base.
metadata:
  openclaw:
    emoji: '📝'
    homepage: https://www.getdnote.com/docs/cli/
    requires:
      bins:
        - dnote
    primaryEnv: DNOTE_API_KEY
---

# Dnote Notes

Manage a personal knowledge base using Dnote CLI.

## Setup

### Installation

```bash
# macOS/Linux auto-install
curl -s https://www.getdnote.com/install | sh

# Or Homebrew
brew install dnote

# Or download from: https://github.com/dnote/dnote/releases
```

### Configuration

Dnote follows XDG directories:
- **Config**: `~/.config/dnote/dnoterc`
- **Database**: `~/.local/share/dnote/dnote.db`

```bash
# Example config file (~/.config/dnote/dnoterc)
editor: vim
apiEndpoint: https://api.dnote.io
enableUpgradeCheck: true

# Or use local-only (no sync)
# No config needed - works offline by default
```

### Sync Setup (Optional)

```bash
# To sync across devices
dnote login

# Or local-only mode (no setup required)
```

## Quick Start

```bash
# Add a note to a book
{baseDir}/scripts/dnote.sh add cli "git rebase -i HEAD~3"

# Pipe content to a note
echo "docker system prune" | {baseDir}/scripts/dnote.sh add docker

# Search all notes
{baseDir}/scripts/dnote.sh find "docker compose"

# View recent notes
{baseDir}/scripts/dnote.sh recent

# List all books
{baseDir}/scripts/dnote.sh books

# View notes in a book
{baseDir}/scripts/dnote.sh view cli

# Get a specific note
{baseDir}/scripts/dnote.sh get cli 1
```

## Commands

### Adding Notes

| Command | Description |
|---------|-------------|
| `add <book> <content>` | Add note to book |
| `add-stdin <book>` | Add from stdin (pipe-friendly) |
| `quick <content>` | Quick add to 'inbox' book |

### Retrieving Notes

| Command | Description |
|---------|-------------|
| `view [book]` | List books or notes in book |
| `get <book> <index>` | Get specific note by index |
| `find <query>` | Full-text search (use `-b <book>` to filter) |
| `recent [n]` | Show n most recent notes (default: 10) |
| `books` | List all books |
| `export [book]` | Export notes as JSON |
| `config` | Show config and paths |

### Managing Notes

| Command | Description |
|---------|-------------|
| `edit <id> [content]` | Edit note by ID |
| `move <id> <book>` | Move note to different book |
| `remove <id>` | Delete note |
| `remove-book <book>` | Delete entire book |

### Sync & Info

| Command | Description |
|---------|-------------|
| `sync` | Sync with Dnote server |
| `status` | Show status and stats |
| `config` | Show config file locations |
| `login` | Authenticate with server (native CLI) |
| `logout` | Remove credentials (native CLI) |

## Collection IDs / Books

- Use any book name (auto-created on first use)
- Common book names: `cli`, `docker`, `git`, `ideas`, `snippets`, `journal`, `inbox`
- Books are created automatically when you add the first note

## Examples

```bash
# Capture a shell one-liner
{baseDir}/scripts/dnote.sh add cli "grep -r pattern . --include='*.py'"

# Save from command output
git log --oneline -10 | {baseDir}/scripts/dnote.sh add git

# Quick capture to inbox
{baseDir}/scripts/dnote.sh quick "Remember to update README"

# Search for docker commands
{baseDir}/scripts/dnote.sh find "docker compose"

# Search within a specific book
{baseDir}/scripts/dnote.sh find "config" -b cli

# Get formatted note for AI context
{baseDir}/scripts/dnote.sh get cli 1 --format raw

# Export book for processing
{baseDir}/scripts/dnote.sh export cli --json | jq '.notes[].content'

# Recent notes across all books
{baseDir}/scripts/dnote.sh recent 20

# Search and export results
{baseDir}/scripts/dnote.sh find "postgres" --json
```

## Using Notes in AI Context

### Retrieve relevant notes for the current task:

```bash
# Search for related knowledge
{baseDir}/scripts/dnote.sh find "python argparse"

# Get full content of a specific note
{baseDir}/scripts/dnote.sh get cli 5

# Export entire book for context
{baseDir}/scripts/dnote.sh export python
```

### Auto-capture useful information:

```bash
# Save a discovered solution
{baseDir}/scripts/dnote.sh add docker "Multi-stage builds reduce image size"

# Save with timestamp
{baseDir}/scripts/dnote.sh add journal "$(date): Deployed v2.3 to production"
```

## Patterns

### Daily Journal

```bash
# Create dated entry
{baseDir}/scripts/dnote.sh add journal "$(date +%Y-%m-%d): Started work on feature X"

# Review recent entries
{baseDir}/scripts/dnote.sh view journal | head -20
```

### Code Snippets

```bash
# Save with description
{baseDir}/scripts/dnote.sh add python "List comprehension: [x for x in items if x > 0]"

# Search when needed
{baseDir}/scripts/dnote.sh find "list comprehension"
```

### Command Reference

```bash
# Build a CLI reference
curl -s https://api.example.com | {baseDir}/scripts/dnote.sh add api

# Quick lookup
{baseDir}/scripts/dnote.sh view api
```

## Integration with Workflows

The skill provides helper functions for common patterns:

| Function | Use Case |
|----------|----------|
| `dnote:search <query>` | Find relevant context before answering |
| `dnote:capture <book> <content>` | Save useful info discovered during task |
| `dnote:recent [n]` | Review recently captured notes |
| `dnote:export-book <book>` | Load entire book into context |

## Config File

Create `~/.config/dnote/dnoterc`:

```yaml
editor: code --wait      # or vim, nano, subl -w
apiEndpoint: https://api.dnote.io
enableUpgradeCheck: true
```

## Tips

- **Use specific book names**: `python`, `bash`, `docker`, `kubernetes`, `ideas`
- **Search is full-text**: Works across all note content
- **Indexes are 1-based**: First note is `1`, not `0`
- **Pipes work great**: Capture command output directly
- **Sync optional**: Works fully offline, sync when ready

## Direct Dnote CLI

For operations not covered:

```bash
# Interactive edit
dnote edit 5

# Rename book
dnote edit oldname -n newname

# Full sync
dnote sync --full

# Custom DB path
dnote --dbPath /path/to/custom.db view
```

Docs: https://www.getdnote.com/docs/cli/
