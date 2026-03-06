---
name: openclaw-todo
description: OpenClaw plugin providing TODO commands for a markdown TODO.md file.
---

# openclaw-todo

Adds commands to manage a local markdown TODO list (default: `~/.openclaw/workspace/TODO.md`).

## Commands

- `/todo-list` - list open TODO items (overdue items shown first)
- `/todo-add <text>` - add a new TODO item (supports `@due(YYYY-MM-DD)`, `#tag`, `!priority`)
- `/todo-done <index>` - mark an open TODO item done (index from `/todo-list`)
- `/todo-edit <index> <new text>` - edit an existing TODO item's text
- `/todo-remove <index>` - remove a TODO item entirely
- `/todo-search <query>` - search TODOs by text, `#tag`, `!priority`, `@due`, `@overdue`, or `@today`

## Inline Markers

- **Tags:** `#tag-name` - categorize items (e.g., `#dev`, `#ops`)
- **Priority:** `!high`, `!medium`, `!low` - set urgency level
- **Due date:** `@due(YYYY-MM-DD)` - set a deadline; overdue items appear first in listings

## Install

```bash
clawhub install openclaw-todo
```

## Notes

- This plugin is safe for public repos (no secrets required).
- Customize file paths via plugin config in your local `openclaw.json`.
