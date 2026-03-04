# Task management

This section applies when `ORG_MEMORY_USE_FOR_HUMAN` is `true`. All commands operate against `$ORG_MEMORY_HUMAN_DIR` and `$ORG_MEMORY_HUMAN_DATABASE_LOCATION`.

## Read the human's state

**Start here.** `org today` is the most useful query — it returns all non-done TODOs that are scheduled for today or overdue:

```bash
org today -d "$ORG_MEMORY_HUMAN_DIR" -f json
```

For broader views:

```bash
org agenda today -d "$ORG_MEMORY_HUMAN_DIR" -f json   # all scheduled + deadlines for today
org agenda week -d "$ORG_MEMORY_HUMAN_DIR" -f json    # next 7 days
org agenda todo -d "$ORG_MEMORY_HUMAN_DIR" -f json    # all TODOs with scheduled dates
org agenda todo --tag work -d "$ORG_MEMORY_HUMAN_DIR" -f json
```

For rich filtering across all TODOs (scheduled or not):

```bash
org todos --state TODO -d "$ORG_MEMORY_HUMAN_DIR" -f json                    # all open TODOs
org todos --state TODO --unscheduled -d "$ORG_MEMORY_HUMAN_DIR" -f json      # unscheduled only
org todos --state TODO --overdue -d "$ORG_MEMORY_HUMAN_DIR" -f json          # overdue items
org todos --state TODO --due-before 2026-03-01 -d "$ORG_MEMORY_HUMAN_DIR" -f json  # due before date
org todos --search 'meeting' -d "$ORG_MEMORY_HUMAN_DIR" -f json              # search by title
org todos --state TODO --file 'work' -d "$ORG_MEMORY_HUMAN_DIR" -f json      # filter by file
org todos --state TODO --tag urgent -d "$ORG_MEMORY_HUMAN_DIR" -f json       # filter by tag
org todos --state TODO --priority A -d "$ORG_MEMORY_HUMAN_DIR" -f json       # filter by priority
org todos --state TODO --sort priority -d "$ORG_MEMORY_HUMAN_DIR" -f json    # sort by priority
org todos --state TODO --sort scheduled --reverse -d "$ORG_MEMORY_HUMAN_DIR" -f json  # reverse sort
```

The `todos` command returns full data in JSON: title, todo state, priority, tags, file, pos, scheduled, deadline, level, path (parent headlines), and custom_id. All filters are combinable.

## Make changes

```bash
# Add a headline (response includes the auto-assigned custom_id)
org add "$ORG_MEMORY_HUMAN_DIR/inbox.org" 'Review PR #42' --todo TODO --tag work --deadline 2026-02-10 --db "$ORG_MEMORY_HUMAN_DATABASE_LOCATION" -f json

# Subsequent commands use the custom_id — no file path needed
org todo k4t DONE -d "$ORG_MEMORY_HUMAN_DIR" --db "$ORG_MEMORY_HUMAN_DATABASE_LOCATION" -f json
org schedule a1b 2026-03-15 -d "$ORG_MEMORY_HUMAN_DIR" --db "$ORG_MEMORY_HUMAN_DATABASE_LOCATION" -f json
org note a1b 'Pushed back per manager request' -d "$ORG_MEMORY_HUMAN_DIR" --db "$ORG_MEMORY_HUMAN_DATABASE_LOCATION"
org append a1b 'Meeting notes from standup.' -d "$ORG_MEMORY_HUMAN_DIR" --db "$ORG_MEMORY_HUMAN_DATABASE_LOCATION" -f json

# Refile still requires explicit file paths
org refile "$ORG_MEMORY_HUMAN_DIR/inbox.org" 'Review PR #42' "$ORG_MEMORY_HUMAN_DIR/work.org" 'Code reviews' --db "$ORG_MEMORY_HUMAN_DATABASE_LOCATION" -f json
```

## Preview before writing

Use `--dry-run` to see what a mutation would produce without modifying the file:

```bash
org todo tasks.org 'Buy groceries' DONE --dry-run -f json
```

## Batch operations

Apply multiple mutations atomically. Commands execute sequentially against in-memory state. Files are written only if all succeed.

```bash
echo '{"commands":[
  {"command":"todo","file":"tasks.org","identifier":"Buy groceries","args":{"state":"DONE"}},
  {"command":"tag-add","file":"tasks.org","identifier":"Write report","args":{"tag":"urgent"}},
  {"command":"schedule","file":"tasks.org","identifier":"Write report","args":{"date":"2026-03-01"}},
  {"command":"append","file":"tasks.org","identifier":"Write report","args":{"text":"Include Q1 metrics."}}
]}' | org batch -d "$ORG_MEMORY_HUMAN_DIR" --db "$ORG_MEMORY_HUMAN_DATABASE_LOCATION" -f json
```

## Query shortcuts

When the human asks about their tasks or your knowledge, map natural language to the right query. Don't ask "what do you mean?" — just run the query.

| Human says | Action |
|---|---|
| "What do I need to do?" / "What's on my plate?" | `org today -d "$ORG_MEMORY_HUMAN_DIR" -f json` (today + overdue) |
| "What's overdue?" | `org todos --state TODO --overdue -d "$ORG_MEMORY_HUMAN_DIR" -f json` |
| "What's coming up this week?" | `org agenda week -d "$ORG_MEMORY_HUMAN_DIR" -f json` |
| "Show me everything tagged work" | `org todos --state TODO --tag work -d "$ORG_MEMORY_HUMAN_DIR" -f json` |
| "What do I have unscheduled?" | `org todos --state TODO --unscheduled -d "$ORG_MEMORY_HUMAN_DIR" -f json` |
| "Find all tasks about X" | `org todos --search 'X' -d "$ORG_MEMORY_HUMAN_DIR" -f json` |
| "What do you know about Sarah?" | `org roam node find 'Sarah'` → `org read <file> 'Sarah'` → `org roam backlinks <id>` (all with agent dir/db flags) |
| "What's the status of project X?" | `org fts 'X' -d "$ORG_MEMORY_AGENT_DIR"` + `org todos --search 'X' -d "$ORG_MEMORY_HUMAN_DIR"` |
| "Search my notes for Y" | `org fts 'Y' -d "$ORG_MEMORY_HUMAN_DIR" --db "$ORG_MEMORY_HUMAN_DATABASE_LOCATION" -f json` |

Present results in a clean, readable format. Don't dump raw JSON at the human — summarise it.
