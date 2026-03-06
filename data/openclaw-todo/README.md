# openclaw-todo

OpenClaw plugin to manage `TODO.md` via chat commands.

## Commands

- `/todo-list` - show open items (with priority indicators)
- `/todo-add <text>` - add an item (supports `#tag` and `!high`/`!medium`/`!low`)
- `/todo-done <index>` - mark item done
- `/todo-edit <index> <new text>` - edit an item's text
- `/todo-remove <index>` - remove an item
- `/todo-search <query>` - search items by text, `#tag`, or `!priority`

## Tags and Priority

Inline tags and priority markers are supported in todo text:

```
/todo-add Fix login page #dev #frontend !high
/todo-add Update README #docs !low
/todo-add Review PR #backend
```

- **Tags**: `#word` - categorize items (e.g. `#dev`, `#front-end`, `#ops`)
- **Priority**: `!high`, `!medium`, `!low` - set urgency level

Tags and priorities are parsed automatically and displayed in `/todo-list`:

```
Open TODOs (3):
1. [HIGH] Fix login page #dev #frontend !high
2. [LOW] Update README #docs !low
3. Review PR #backend
```

The `todo_status` tool also returns structured `tags` and `priority` fields per item.

## Tool

- `todo_status({ limit })` - structured TODO status for the agent

## Configuration

All options are set via `pluginConfig` in your OpenClaw config:

| Option | Type | Default | Description |
|---|---|---|---|
| `enabled` | boolean | `true` | Enable/disable the plugin |
| `todoFile` | string | `~/.openclaw/workspace/TODO.md` | Path to the TODO file |
| `sectionHeader` | string | _(none)_ | Section heading under which new todos are inserted (e.g. `"## Backlog"`). When omitted, new items are appended after the last existing todo. |
| `brainLog` | boolean | `true` | Log todo changes to memory brain |
| `brainStorePath` | string | `~/.openclaw/workspace/memory/brain-memory.jsonl` | Path to the brain memory store |
| `maxListItems` | number | `30` | Maximum items shown by `/todo-list` |

## Install (dev)

```bash
openclaw plugins install -l ~/.openclaw/workspace/openclaw-todo
openclaw gateway restart
```
