# Cheatsheet (useful subset)

## Add
- `task add <description>`
- `task add project:<p> +tag1 +tag2 due:2026-03-01 priority:H <description>`

## List
- `task list`
- `task project:<p> list`
- `task due.before:eow list`
- `task +tag list`

## Modify
- `task <id> modify project:<p> +tag -tag due:2026-03-01 priority:M`
- Clear due: `task <id> modify due:`

## Complete
- `task <id> done`

## Annotate
- `task <id> annotate "note here"`
