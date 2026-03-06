# Apple Notes — Notes Platform

## Overview

Manage Apple Notes via the `memo` CLI. macOS only.

## Requirements

- macOS
- Apple Notes.app
- `memo` CLI

## Installation

```bash
brew tap antoniorodr/memo
brew install antoniorodr/memo/memo
```

First run: grant Automation access to Notes.app when prompted (System Settings > Privacy & Security > Automation).

## Common Operations

### List Notes

```bash
# All notes
memo notes

# Filter by folder
memo notes -f "Work"

# Search (fuzzy)
memo notes -s "keyword"
```

### Create Note

```bash
# Interactive (opens editor)
memo notes -a

# With title
memo notes -a "Note Title"
```

### Edit Note

```bash
# Interactive selection
memo notes -e
```

### Delete Note

```bash
# Interactive selection
memo notes -d
```

### Move Note

```bash
# Move to different folder
memo notes -m
```

### Export Note

```bash
# Export to HTML/Markdown
memo notes -ex
```

## Folder Organization

Map note types to Apple Notes folders:

| Note Type | Suggested Folder |
|-----------|-----------------|
| meetings | Meetings |
| decisions | Decisions |
| projects | Projects |
| journal | Journal |
| quick | Quick Notes |

Create folders manually in Apple Notes first.

## Limitations

- Cannot edit notes containing images/attachments via CLI
- Interactive prompts require terminal access
- No API access to note content programmatically (only via CLI)

## Creating Formatted Notes

Since `memo` uses interactive editor, prepare content first:

```bash
# Create temp file with content
cat > /tmp/note.md << 'EOF'
# Meeting: Product Sync — 2026-02-19

**Attendees:** Alice, Bob

## Key Points
- Point 1
- Point 2

## Action Items
- [ ] @alice: Update doc — Due: 2026-02-20
EOF

# Copy to clipboard
cat /tmp/note.md | pbcopy

# Then run memo and paste
memo notes -a "Product Sync 2026-02-19"
```

## Integration Notes

- Action items extracted from Apple Notes → sync to `~/notes/actions.md`
- Search results include Apple Notes with `apple-notes:` prefix
- If `memo` unavailable → fall back to local
