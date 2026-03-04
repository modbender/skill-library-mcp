# Linear via TapAuth

## Available Scopes

| Scope | Access |
|-------|--------|
| `read` | Read issues, projects, teams, users |
| `write` | Create and update issues, comments, projects |
| `issues:create` | Create issues only |
| `comments:create` | Create comments only |
| `admin` | Workspace admin (team management, integrations) |

## Example: List Issues

```bash
# 1. Get a token
./scripts/tapauth.sh linear "read" "Issue Tracker"

# 2. Query via GraphQL
curl -X POST -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  "https://api.linear.app/graphql" \
  -d '{"query": "{ issues(first: 10) { nodes { id title state { name } priority assignee { name } } } }"}'
```

## Example: Create an Issue

```bash
curl -X POST -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  "https://api.linear.app/graphql" \
  -d '{"query": "mutation { issueCreate(input: { title: \"Bug report\", teamId: \"TEAM_ID\", priority: 2 }) { success issue { id identifier url } } }"}'
```

## Example: Add a Comment

```bash
curl -X POST -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  "https://api.linear.app/graphql" \
  -d '{"query": "mutation { commentCreate(input: { issueId: \"ISSUE_ID\", body: \"Working on this now.\" }) { success } }"}'
```

## Gotchas

- **GraphQL only:** Linear uses GraphQL, not REST. All queries go to `https://api.linear.app/graphql`.
- **Team IDs:** You'll need the team ID to create issues. Query `{ teams { nodes { id name } } }` first.
- **Token expiry:** Linear OAuth tokens expire. TapAuth handles refresh — re-call the token endpoint for a fresh one.
- **Rate limits:** 1,500 requests per hour per token. Linear returns `X-RateLimit-Remaining`.
- **Pagination:** Use `first`/`after` cursor pagination for large result sets.

## Recommended Minimum Scopes

| Use Case | Scopes |
|----------|--------|
| Read issues | `read` |
| Create issues | `read`, `issues:create` |
| Full project management | `read`, `write` |
