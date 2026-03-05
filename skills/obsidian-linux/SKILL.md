---
name: obsidian
description: Work with Obsidian vaults (plain Markdown notes) and automate via notesmd-cli.
homepage: https://help.obsidian.md
metadata: {"clawdbot":{"emoji":"💎","requires":{"bins":["notesmd-cli"]},"install":[{"id":"brew","kind":"brew","formula":"yakitrak/yakitrak/notesmd-cli","bins":["notesmd-cli"],"label":"Install notesmd-cli (brew, macOS)"},{"id":"aur","kind":"aur","package":"notesmd-cli-bin","bins":["notesmd-cli"],"label":"Install notesmd-cli (AUR, Arch/Manjaro Linux)"}]}}
---

# Obsidian

Obsidian vault = a normal folder on disk with Markdown files.

Vault structure (typical):
- Notes: `*.md` (plain text Markdown; edit with any editor)
- Config: `.obsidian/` (workspace + plugin settings; don't touch from scripts)
- Canvases: `*.canvas` (JSON)
- Attachments: whatever folder you chose in Obsidian settings (images/PDFs/etc.)

## Setup

### Find active vault(s)

Obsidian desktop tracks vaults in a config file (source of truth):
- **macOS**: `~/Library/Application Support/obsidian/obsidian.json`
- **Linux**: `~/.config/obsidian/obsidian.json`

`notesmd-cli` resolves vaults from that file; vault name is the **folder name** (path suffix).

### Verify default vault

Always check before running commands:

```bash
notesmd-cli print-default --path-only 2>/dev/null && echo "OK" || echo "NOT_SET"
```

If `NOT_SET`, configure it:

```bash
notesmd-cli set-default "VAULT_NAME"
```

Don't guess vault paths — read the config file or use `print-default`.

## notesmd-cli quick reference

### Vault info

```bash
notesmd-cli print-default              # show default vault name + path
notesmd-cli print-default --path-only  # path only
notesmd-cli list                       # list notes and folders in vault
notesmd-cli list "Folder"              # list inside a folder
```

### Search

```bash
notesmd-cli search "query"             # fuzzy search note names
notesmd-cli search-content "query"     # search inside notes (shows snippets + lines)
```

### Read

```bash
notesmd-cli print "path/note"          # print note contents
notesmd-cli frontmatter "path/note"    # view or modify note frontmatter
```

### Create & edit

```bash
notesmd-cli create "Folder/Note" --content "..." --open    # create note
notesmd-cli create "Folder/Note" --content "..." --append  # append to existing note
notesmd-cli create "Folder/Note" --content "..." --overwrite  # overwrite note
```

Note: `create` requires Obsidian URI handler (Obsidian must be installed). Avoid hidden dot-folder paths.

### Move / delete

```bash
notesmd-cli move "old/path/note" "new/path/note"  # rename/move (updates [[wikilinks]])
notesmd-cli delete "path/note"
```

### Multi-vault

Add `--vault "Name"` to any command:

```bash
notesmd-cli print "2025-01-10" --vault "Work"
notesmd-cli search "meeting" --vault "Personal"
```

## Daily notes

```bash
notesmd-cli daily                      # open/create today's daily note
notesmd-cli daily --vault "Work"       # for a specific vault
```

### Get current date (cross-platform)

```bash
date +%Y-%m-%d                         # today
# Yesterday (GNU first, BSD fallback):
date -d yesterday +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d
# Last Friday:
date -d "last friday" +%Y-%m-%d 2>/dev/null || date -v-friday +%Y-%m-%d
# N days ago:
date -d "3 days ago" +%Y-%m-%d 2>/dev/null || date -v-3d +%Y-%m-%d
```

### Append to daily note

```bash
# Journal entry
notesmd-cli create "$(date +%Y-%m-%d)" --content "- Did the thing" --append

# Task
notesmd-cli create "$(date +%Y-%m-%d)" --content "- [ ] Buy groceries" --append

# Timestamped log
notesmd-cli create "$(date +%Y-%m-%d)" --content "- $(date +%H:%M) Meeting notes here" --append

# With custom folder (e.g. Daily Notes plugin folder)
notesmd-cli create "Daily Notes/$(date +%Y-%m-%d)" --content "- Entry" --append
```

### Read a daily note

```bash
notesmd-cli print "$(date +%Y-%m-%d)"  # today
notesmd-cli print "$(date -d yesterday +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d)"  # yesterday
notesmd-cli print "2025-01-10"         # specific date
```

## Common patterns

**Create a new note with content:**
```bash
notesmd-cli create "Projects/My Project" --content "# My Project\n\nNotes here." --open
```

**Find and read a note:**
```bash
notesmd-cli search "meeting"
notesmd-cli print "path/from/search/result"
```

**Safe rename preserving links:**
```bash
notesmd-cli move "old/note name" "new/folder/note name"
```

**Search inside notes:**
```bash
notesmd-cli search-content "TODO"
notesmd-cli search-content "project alpha"
```

Prefer direct file edits when appropriate (just edit the `.md` file); Obsidian picks them up automatically.
