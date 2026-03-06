---
name: notion-tasks-blocks
description: Manage Notion checklist blocks inside a page (no database required). Use when the user has plain to-do blocks and wants to list tasks, add tasks, and mark tasks done/undone.
---

# notion-tasks-blocks

Use this skill for Notion pages that contain `to_do` blocks (checklist items), not databases.

## Required env vars

- `NOTION_TOKEN` (`secret_...`)
- `NOTION_TASKS_PAGE_ID` (page id that contains the task blocks)

## Command wrapper

```bash
bash {baseDir}/scripts/notion_tasks_blocks.sh <command> [args]
```

Commands:

- `list` → list current to-do blocks with index and done status
- `add "<text>"` → append new unchecked to-do block to the page
- `done <index>` → mark indexed task as checked
- `undo <index>` → mark indexed task as unchecked

## Notes

- Indexes come from `list`.
- Works only for top-level `to_do` blocks on the page.
- If Notion returns permission errors, share the page with your integration.
