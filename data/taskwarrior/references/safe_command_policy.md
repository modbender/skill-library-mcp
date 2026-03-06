# Safe command policy

## Allowed by default
Read-only:
- `task --version`
- `task list`, `task <filter> list`
- `task <id> info`
- `task projects`, `task tags`

Write (safe):
- `task add ...`
- `task <id> modify ...`
- `task <id> done`
- `task <id> start|stop`
- `task <id> annotate "..."`

## Not allowed unless explicitly requested
- `task delete`
- `task purge`
- bulk changes without preview (e.g. `task project:X modify ...`)
- writing to global `~/.task` or `~/.taskrc`

## Bulk action policy
If user requests a bulk change:
1) Preview: `task <filter> list`
2) State how many tasks match
3) Proceed only if the request clearly implies bulk intent
