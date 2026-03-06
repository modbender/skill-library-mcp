# Linear API Reference

## Configuration

This skill uses:
- `LINEAR_API_KEY` (personal API key from `https://linear.app/settings/api`)
- `scripts/linear-cli.js`
- `@linear/sdk` in `scripts/package.json`

## Getting IDs

### Teams
Use:
`node ./scripts/linear-cli.js teams`

### Projects
Use:
`node ./scripts/linear-cli.js projects`

## Priority Levels

- `0`: No priority
- `1`: Urgent
- `2`: High
- `3`: Normal
- `4`: Low

## State Types

States are team-specific. Use:
`node ./scripts/linear-cli.js states "<teamId>"`

Common state types:
- `backlog`
- `unstarted`
- `started`
- `completed`
- `canceled`

## Filter Examples

### Issues by state
```json
{
  "state": {
    "name": { "eq": "In Progress" }
  }
}
```

### Issues by assignee
```json
{
  "assignee": {
    "id": { "eq": "user-id-here" }
  }
}
```

### Issues by project
```json
{
  "project": {
    "id": { "eq": "project-id-here" }
  }
}
```

### Issues by priority
```json
{
  "priority": { "eq": 1 }
}
```

## Common Workflows

### Create an issue for a project

1. Get team/project IDs (`teams`, `projects`).
2. Create issue with `teamId` and `projectId`:

```bash
node ./scripts/linear-cli.js createIssue "Task title" "Description here" "your-team-id" '{"projectId":"your-project-id","priority":2}'
```

### Update issue state

1. Get team states:

```bash
node ./scripts/linear-cli.js states "<teamId>"
```

2. Update issue:

```bash
node ./scripts/linear-cli.js updateIssue "issue-uuid" '{"stateId":"state-uuid"}'
```

### Assign issue to user

1. Get user info:

```bash
node ./scripts/linear-cli.js user
```

2. Apply assignment:

```bash
node ./scripts/linear-cli.js updateIssue "issue-uuid" '{"assigneeId":"user-uuid"}'
```
