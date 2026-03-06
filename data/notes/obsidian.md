# Obsidian — Notes Platform

## Overview

Work with Obsidian vaults (plain markdown) via `obsidian-cli`. Cross-platform.

## Requirements

- Obsidian app installed
- `obsidian-cli`

## Installation

```bash
brew install yakitrak/yakitrak/obsidian-cli
```

## Vault Configuration

Obsidian tracks vaults in:
- macOS: `~/Library/Application Support/obsidian/obsidian.json`

### Set Default Vault

```bash
# List available vaults
obsidian-cli print-default

# Set default
obsidian-cli set-default "VaultName"

# Get vault path
obsidian-cli print-default --path-only
```

## Common Operations

### Search

```bash
# By note name
obsidian-cli search "query"

# By content (shows snippets + lines)
obsidian-cli search-content "query"
```

### Create Note

```bash
# Create and optionally open in Obsidian
obsidian-cli create "Folder/Note Name" --content "Content here" --open

# Create without opening
obsidian-cli create "Meetings/2026-02-19 Product Sync" --content "..."
```

### Move/Rename (Safe Refactor)

```bash
# Updates [[wikilinks]] across vault
obsidian-cli move "old/path/note" "new/path/note"
```

### Delete

```bash
obsidian-cli delete "path/note"
```

## Folder Organization

Typical vault structure for notes:

```
MyVault/
├── Meetings/
│   └── YYYY-MM-DD Topic.md
├── Decisions/
│   └── YYYY-MM-DD Topic.md
├── Projects/
│   └── ProjectName/
│       └── Updates/
├── Journal/
│   └── YYYY/
│       └── MM/
│           └── YYYY-MM-DD.md
└── Inbox/
    └── Quick captures
```

## Creating Formatted Notes

```bash
# Prepare content
CONTENT=$(cat << 'EOF'
---
date: 2026-02-19
type: meeting
tags: [product, roadmap]
attendees: [alice, bob]
---

# Product Sync — 2026-02-19

## Key Points
- Point 1
- Point 2

## Action Items
- [ ] @alice: Update doc — Due: 2026-02-20
EOF
)

# Create in vault
obsidian-cli create "Meetings/2026-02-19 Product Sync" --content "$CONTENT"
```

## Direct File Editing

Since Obsidian vaults are plain markdown folders, you can:

```bash
# Get vault path
VAULT=$(obsidian-cli print-default --path-only)

# Edit directly
nano "$VAULT/Meetings/2026-02-19 Product Sync.md"

# Obsidian picks up changes automatically
```

## Wikilinks

Obsidian uses `[[wikilinks]]` for internal linking:

```markdown
See [[2026-02-15 Kickoff Meeting]] for context.
Related: [[Projects/Alpha/Roadmap]]
```

Use `obsidian-cli move` when renaming to preserve links.

## Limitations

- URI handler requires Obsidian installed
- Avoid creating notes in hidden dot-folders via URI
- Multiple vaults common — always verify which vault is active

## Integration Notes

- Action items extracted from Obsidian notes → sync to `~/notes/actions.md`
- Search results include Obsidian with `obsidian:[[Note]]` format
- If `obsidian-cli` unavailable → fall back to local
- Can edit vault files directly without CLI
