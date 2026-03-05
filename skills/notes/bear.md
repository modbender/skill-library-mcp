# Bear — Notes Platform

## Overview

Manage Bear notes via the `grizzly` CLI. macOS only.

## Requirements

- macOS
- Bear app (installed and running)
- `grizzly` CLI
- Bear API token (for some operations)

## Installation

```bash
go install github.com/tylerwince/grizzly/cmd/grizzly@latest
```

## Getting Bear Token

Some operations (add-text, tags, open-note --selected) require authentication:

1. Open Bear → Help → API Token → Copy Token
2. Save it:
```bash
mkdir -p ~/.config/grizzly
echo "YOUR_TOKEN" > ~/.config/grizzly/token
```

## Common Operations

### Create Note

```bash
# With content piped in
echo "Note content here" | grizzly create --title "My Note" --tag work

# Empty note with tags
grizzly create --title "Quick Note" --tag inbox < /dev/null

# Multiple tags
echo "Content" | grizzly create --title "Title" --tag work --tag urgent
```

### Read Note

```bash
# By ID (get ID from callbacks)
grizzly open-note --id "NOTE_ID" --enable-callback --json
```

### Append to Note

```bash
# Requires token
echo "Additional content" | grizzly add-text --id "NOTE_ID" --mode append --token-file ~/.config/grizzly/token
```

### List Tags

```bash
# Requires token
grizzly tags --enable-callback --json --token-file ~/.config/grizzly/token
```

### Search by Tag

```bash
grizzly open-tag --name "work" --enable-callback --json
```

## Tag Organization

Map note types to Bear tags:

| Note Type | Suggested Tags |
|-----------|---------------|
| meetings | #meetings, #meetings/YYYY-MM |
| decisions | #decisions |
| projects | #projects, #projects/name |
| journal | #journal, #journal/YYYY-MM |
| quick | #inbox |

## Configuration

Create `~/.config/grizzly/config.toml`:

```toml
token_file = "~/.config/grizzly/token"
callback_url = "http://127.0.0.1:42123/success"
timeout = "5s"
```

## Important Flags

| Flag | Purpose |
|------|---------|
| `--dry-run` | Preview URL without executing |
| `--print-url` | Show the x-callback-url |
| `--enable-callback` | Wait for Bear's response (needed for reading) |
| `--json` | Output as JSON |
| `--token-file PATH` | Path to API token |

## Creating Formatted Notes

```bash
# Prepare markdown content
cat << 'EOF' | grizzly create --title "Meeting: Product Sync" --tag meetings --tag product
# Product Sync — 2026-02-19

**Attendees:** Alice, Bob

## Key Points
- Point 1
- Point 2

## Action Items
- [ ] @alice: Update doc — Due: 2026-02-20
EOF
```

## Limitations

- Bear must be running for commands to work
- Note IDs are Bear's internal identifiers
- Some operations require valid token
- No direct content editing via CLI (append only)

## Integration Notes

- Action items extracted from Bear → sync to `~/notes/actions.md`
- Search results include Bear with `bear:#tag/Title` format
- If `grizzly` unavailable or Bear not running → fall back to local
