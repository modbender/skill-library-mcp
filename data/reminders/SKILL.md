---
name: reminders
description: Search, create, complete, edit, and delete macOS Reminders. Use proactively — when the user asks to be reminded of something, mentions a task or to-do, or wants to check upcoming reminders.
---

# macOS Reminders

Manage macOS Reminders via the `reminders` script. Returns JSON. Zero dependencies — uses built-in macOS tools.

## When to Use This Skill

Use this skill **proactively**, not only when the user explicitly asks:

- **"Remind me to..."** — create a reminder with a due date.
- **User mentions a task or to-do** — create a reminder or search for existing ones.
- **"What do I need to do?"** — list upcoming/incomplete reminders.
- **"I finished X"** or **"Done with X"** — mark the matching reminder as complete.
- **User explicitly asks** to look up, add, complete, edit, or delete reminders.

## Running Commands

All commands use the `reminders` script in this skill's `references/` directory. Determine the path relative to this SKILL.md file:

```bash
REMINDERS="$(dirname "<path-to-this-SKILL.md>")/references/reminders.sh"
```

On first run, macOS will prompt for Reminders access — click **Allow**.

## Commands

### Lists

```bash
$REMINDERS lists
```

Shows all reminder lists with total and incomplete counts.

### List Reminders

```bash
$REMINDERS ls [<list-name>] [--all]
```

List reminders. By default shows only incomplete. If no list name given, shows across all lists.

| Flag | Description |
|------|-------------|
| `--all` | Include completed reminders |

```bash
$REMINDERS ls
$REMINDERS ls "Shopping"
$REMINDERS ls "Work" --all
```

### Search (default)

```bash
$REMINDERS search <query> [--all]
$REMINDERS <query>                   # search is the default command
```

Search reminders by name and notes across all lists. By default excludes completed.

```bash
$REMINDERS search "buy milk"
$REMINDERS "dentist"
$REMINDERS search "groceries" --all
```

### Add

```bash
$REMINDERS add --name <text> [--list <name>] [--due <datetime>] [--remind <datetime>] [--notes <text>] [--priority high|medium|low] [--flagged]
```

`--name` is required. If `--list` is omitted, uses the default list. If `--due` is provided without `--remind`, the remind-me date is set to the same value.

**Dates must be ISO 8601 with time** (e.g. `2025-02-15T10:00:00`). Convert relative dates (e.g. "tomorrow at 9am") to absolute ISO 8601 before calling.

```bash
$REMINDERS add --name "Buy milk"
$REMINDERS add --name "Call dentist" --due 2025-02-15T09:00:00 --priority high
$REMINDERS add --name "Pick up package" --list "Errands" --notes "At the post office"
```

### Complete

```bash
$REMINDERS complete <query> [--list <name>]
```

Mark a reminder as complete. Searches incomplete reminders by name. If multiple match, lists them.

```bash
$REMINDERS complete "Buy milk"
$REMINDERS complete "Buy milk" --list "Shopping"
```

### Edit

```bash
$REMINDERS edit <query> [--list <name>] [options]
```

Find a reminder by name and apply changes. If multiple match, lists them.

| Option | Description |
|--------|-------------|
| `--list <name>` | Narrow search to a specific list |
| `--name <text>` | Set new name |
| `--due <datetime>` | Set due date (`clear` to remove) |
| `--remind <datetime>` | Set remind-me date (`clear` to remove) |
| `--notes <text>` | Set notes (`clear` to remove) |
| `--priority <level>` | Set priority (high, medium, low, none) |
| `--flagged` | Set flagged |
| `--unflagged` | Remove flag |
| `--uncomplete` | Mark as incomplete |

```bash
$REMINDERS edit "Buy milk" --name "Buy almond milk"
$REMINDERS edit "Call dentist" --due 2025-02-20T14:00:00
$REMINDERS edit "Old task" --uncomplete
```

### Delete

```bash
$REMINDERS delete <query> [--list <name>] [--yes]
```

Find a reminder by name and delete it. Asks for confirmation unless `--yes` is passed. Always use `--yes` to skip the interactive prompt.

```bash
$REMINDERS delete "Buy milk" --yes
$REMINDERS delete "Old task" --list "Shopping" --yes
```

### Add List

```bash
$REMINDERS add-list --name <text>
```

Create a new reminder list.

```bash
$REMINDERS add-list --name "Projects"
```

## Output

All commands return JSON:

```json
// lists
[
  { "name": "Reminders", "count": 12, "incomplete": 5 },
  { "name": "Shopping", "count": 3, "incomplete": 2 }
]

// ls, search
[
  {
    "name": "Buy milk",
    "body": "Get whole milk",
    "completed": false,
    "dueDate": "2025-02-15T10:00:00.000Z",
    "remindMeDate": "2025-02-15T10:00:00.000Z",
    "completionDate": null,
    "priority": "high",
    "flagged": false,
    "list": "Shopping"
  }
]

// add
{ "created": true, "name": "Buy milk", "list": "Shopping", ... }

// complete, edit
{ "updated": true, "name": "Buy milk", "completed": true, "list": "Shopping", ... }

// delete
{ "deleted": true, "name": "Buy milk", "list": "Shopping" }

// add-list
{ "created": true, "name": "Projects" }
```

## Workflow

```
- [ ] 1. Set REMINDERS path relative to this SKILL.md
- [ ] 2. Run the appropriate command
- [ ] 3. If permission error → tell user to grant Reminders access in System Settings > Privacy & Security > Reminders
- [ ] 4. Parse and present results to the user
```

### Proactive behaviors

- **"Remind me to...":** Create a reminder immediately. Parse the due date from context (e.g., "tomorrow morning" → next day at 9:00 AM). Confirm what you created.
- **Task mentioned in conversation:** If the user mentions needing to do something, offer to create a reminder or do it proactively if the intent is clear.
- **"Done with X" / "I finished X":** Search for matching reminders and mark them complete. Confirm what was completed.
- **"What's on my list?":** List incomplete reminders. Summarize by list if there are many.
