---
name: upnote
description: Manage UpNote notes and notebooks via x-callback-url automation. Use when a user asks to create notes, open notes, create notebooks, view tags, or manage content in UpNote.
---

# UpNote

Manage UpNote notes and notebooks using x-callback-url automation.

## Overview

UpNote is installed and supports x-callback-url endpoints for automation. Use the bundled `upnote.sh` script for all UpNote operations.

## Quick Start

Create a note:
```bash
scripts/upnote.sh new --title "My Note" --text "Note content here"
```

Create a note with markdown:
```bash
scripts/upnote.sh new --title "Meeting Notes" --text "# Agenda\n- Item 1" --markdown
```

Create a note in a specific notebook:
```bash
scripts/upnote.sh new --title "Project Ideas" --text "Ideas..." --notebook "Work"
```

## Common Operations

### Create Note
```bash
scripts/upnote.sh new \
  --title "Note Title" \
  --text "Content here" \
  [--notebook "Notebook Name"] \
  [--markdown] \
  [--new-window]
```

### Create Notebook
```bash
scripts/upnote.sh notebook new "Notebook Name"
```

### Open Note (requires note ID)
```bash
scripts/upnote.sh open <noteId> [true|false]
```

To get a note ID, right-click a note in UpNote → Copy Link → extract the ID from the URL.

### Open Notebook (requires notebook ID)
```bash
scripts/upnote.sh notebook open <notebookId>
```

### View Tag
```bash
scripts/upnote.sh tag "tag-name"
```

### Search Notes
```bash
scripts/upnote.sh view all_notes --query "search term"
```

### View Modes
```bash
scripts/upnote.sh view <mode>
```

Available modes:
- `all_notes` - All notes
- `quick_access` - Quick access notes
- `templates` - All templates
- `trash` - Trash
- `notebooks` - Notebooks (use with `--notebook-id`)
- `tags` - Tags (use with `--tag-id`)
- `filters` - Filters (use with `--filter-id`)
- `all_notebooks` - All notebooks
- `all_tags` - All tags

## Notes

- All UpNote operations open the UpNote app
- Note and notebook IDs can be obtained by copying links from UpNote (right-click → Copy Link)
- The script handles URL encoding automatically
- For multi-line content, use `\n` for line breaks or pass content via heredoc

## Resources

### scripts/upnote.sh

Shell script wrapper for UpNote x-callback-url operations. Handles URL encoding and provides a clean CLI interface.
