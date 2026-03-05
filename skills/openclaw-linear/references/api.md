# api

> Make raw GraphQL API requests to Linear

## Usage

```text
linear api [query] [options]
```

**Prefer the CLI commands for all supported operations.** The `api` command should only be used as a fallback for queries not covered by the CLI.

## Options

| Flag | Description |
|---|---|
| `--variable <key=value>` | Variable in key=value format (coerces booleans, numbers, null; `@file` reads from path) |
| `--variables-json <json>` | JSON object of variables (merged with --variable, which takes precedence) |
| `--paginate` | Automatically fetch all pages using cursor pagination |
| `--silent` | Suppress response output (exit code still reflects errors) |

Query can also be read from stdin.

## Examples

### Simple queries

```bash
# Get current user info
linear api '{ viewer { id name email } }'

# Get first 5 issues
linear api '{ issues(first: 5) { nodes { identifier title state { name } } } }'
```

### Queries with variables

```bash
# String variable
linear api 'query($teamId: String!) { team(id: $teamId) { name } }' --variable teamId=abc123

# Numeric variable
linear api 'query($first: Int!) { issues(first: $first) { nodes { title } } }' --variable first=5

# Boolean variable
linear api 'query($includeArchived: Boolean) { issues(includeArchived: $includeArchived, first: 5) { nodes { title } } }' --variable includeArchived=true
```

### Complex filters via JSON

```bash
# Filter issues by state
linear api 'query($filter: IssueFilter!) { issues(filter: $filter) { nodes { identifier title } } }' \
  --variables-json '{"filter": {"state": {"name": {"eq": "In Progress"}}}}'

# Filter by assignee and state
linear api 'query($filter: IssueFilter!) { issues(filter: $filter) { nodes { identifier title assignee { name } } } }' \
  --variables-json '{"filter": {"and": [{"state": {"name": {"eq": "In Progress"}}}, {"assignee": {"isMe": {"eq": true}}}]}}'
```

### Pagination

```bash
# Fetch all issues (auto-paginate)
linear api '{ issues(first: 50) { nodes { identifier title } pageInfo { hasNextPage endCursor } } }' --paginate
```

### Piping and scripting

```bash
# Read query from stdin
echo '{ viewer { id } }' | linear api

# Pipe to jq for filtering
linear api '{ issues(first: 10) { nodes { identifier title } } }' | jq '.data.issues.nodes[].title'

# Get just issue identifiers
linear api '{ issues(first: 50) { nodes { identifier } } }' | jq -r '.data.issues.nodes[].identifier'

# Silent mode (check exit code only)
linear api '{ viewer { id } }' --silent && echo "authenticated" || echo "not authenticated"
```

### Using curl directly

For cases where you need full HTTP control:

```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: $(linear auth token)" \
  -d '{"query": "{ viewer { id name } }"}'
```

## Exploring the Schema

Before writing custom queries, explore the schema to discover available types and fields:

```bash
# Write schema to a temp file
linear schema -o "${TMPDIR:-/tmp}/linear-schema.graphql"

# Search for types
grep -i "cycle" "${TMPDIR:-/tmp}/linear-schema.graphql"

# View a specific type definition
grep -A 30 "^type Issue " "${TMPDIR:-/tmp}/linear-schema.graphql"

# Find available queries
grep -A 5 "^type Query " "${TMPDIR:-/tmp}/linear-schema.graphql"

# Find mutations
grep "Mutation" "${TMPDIR:-/tmp}/linear-schema.graphql" | head -20
```

## Common Patterns

### Mutations

```bash
# Update issue state via API (prefer `linear issue update -s` instead)
linear api 'mutation($id: String!, $stateId: String!) { issueUpdate(id: $id, input: {stateId: $stateId}) { success } }' \
  --variable id=<issue-uuid> --variable stateId=<state-uuid>
```

### Fetching related data

```bash
# Get issue with project, labels, and comments
linear api 'query($id: String!) {
  issue(id: $id) {
    identifier
    title
    state { name }
    project { name }
    labels { nodes { name } }
    comments { nodes { body createdAt user { name } } }
  }
}' --variable id=<issue-uuid>
```

## Authentication

The `api` command uses the same authentication as other commands. Manage auth with:

```bash
linear auth login       # Add credentials
linear auth whoami      # Check current user
linear auth token       # Print API token (for curl/scripts)
linear auth list        # List configured workspaces
linear auth default     # Set default workspace
```
