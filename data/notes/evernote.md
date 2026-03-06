# Evernote — Notes Platform

## Overview

Manage Evernote notes via the `clinote` CLI. Cross-platform.

## Requirements

- Evernote account
- `clinote` CLI

## Installation

```bash
go install github.com/TcM1911/clinote@latest
```

## Authentication

First run will prompt for Evernote credentials:

```bash
clinote login
```

This stores auth token locally.

## Common Operations

### List Notebooks

```bash
clinote notebook list
```

### List Notes

```bash
# All notes
clinote note list

# In specific notebook
clinote note list --notebook "Work"
```

### Create Note

```bash
# Create with title and content
clinote note create --title "Meeting Notes" --content "Content here" --notebook "Work"

# Create from file
clinote note create --title "My Note" --file note.md --notebook "Work"
```

### View Note

```bash
clinote note view --title "Meeting Notes"
```

### Search Notes

```bash
clinote note search "keyword"
```

### Delete Note

```bash
clinote note delete --title "Old Note"
```

## Notebook Organization

Map note types to Evernote notebooks:

| Note Type | Suggested Notebook |
|-----------|-------------------|
| meetings | Meetings |
| decisions | Decisions |
| projects | Projects |
| journal | Journal |
| quick | Inbox |

Create notebooks in Evernote first.

## Creating Formatted Notes

```bash
# Prepare markdown content
cat > /tmp/note.md << 'EOF'
# Product Sync — 2026-02-19

**Attendees:** Alice, Bob

## Key Points
- Point 1
- Point 2

## Action Items
- [ ] @alice: Update doc — Due: 2026-02-20
EOF

# Create in Evernote
clinote note create --title "Product Sync 2026-02-19" --file /tmp/note.md --notebook "Meetings"
```

## Limitations

- CLI functionality may be limited compared to native app
- Some formatting may not transfer perfectly
- Requires Go installation for CLI

## Integration Notes

- Action items extracted from Evernote → sync to `~/notes/actions.md`
- Search results include Evernote with `evernote:Note Title` format
- If `clinote` unavailable → fall back to local
