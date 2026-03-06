# Workspace layout

All state is stored under:
`<workspace>/.openclaw/taskwarrior/`

## Paths
- taskrc: `<workspace>/.openclaw/taskwarrior/taskrc`
- data: `<workspace>/.openclaw/taskwarrior/.task/`

## Environment variables used per command
- `TASKRC=<workspace>/.openclaw/taskwarrior/taskrc`
- `TASKDATA=<workspace>/.openclaw/taskwarrior/.task` (optional)

## Minimum taskrc
data.location=<workspace>/.openclaw/taskwarrior/.task
confirmation=off
verbose=off
