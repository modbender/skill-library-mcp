# Vercel via TapAuth

## Provider Key

Use `vercel` as the provider name.

## Scope Model: Integration-Level

Unlike most providers, Vercel scopes are **fixed at the integration level** — you cannot request specific scopes per grant. The user authorizes the full TapAuth integration, which includes access to deployments, projects, environment variables, domains, team info, and user profile.

Just omit scopes or pass any value — the token will have the integration's full permissions.

## Example: Create a Grant

```bash
./scripts/tapauth.sh vercel "" "Deploy Manager"
```

## Example: List Projects

```bash
curl -H "Authorization: Bearer <token>" \
  https://api.vercel.com/v9/projects
```

## Example: List Deployments

```bash
curl -H "Authorization: Bearer <token>" \
  "https://api.vercel.com/v6/deployments?limit=10"
```

## Example: Get Environment Variables

```bash
curl -H "Authorization: Bearer <token>" \
  https://api.vercel.com/v9/projects/PROJECT_ID/env
```

## Available Capabilities

| Capability | Description |
|------------|-------------|
| `deployment` | View and manage deployments |
| `project` | Access project details |
| `project-env-vars` | Manage environment variables |
| `domain` | Manage domains |
| `team` | Access team info |
| `user` | Read user profile |

## Gotchas

- **Integration-level scopes:** You can't request granular scopes per grant. The token gets whatever the TapAuth Vercel integration is configured for.
- **Team context:** If the user belongs to multiple teams, the token may be scoped to a specific team. Check `teamId` in API responses.
- **API versioning:** Vercel APIs are versioned in the URL path (e.g., `/v9/projects`). Use the latest version documented at [vercel.com/docs/rest-api](https://vercel.com/docs/rest-api).
- **Rate limits:** 100 requests per 60 seconds for most endpoints.

## Common Use Cases

| Use Case | API Endpoint |
|----------|-------------|
| List projects | `GET /v9/projects` |
| List deployments | `GET /v6/deployments` |
| Get env vars | `GET /v9/projects/{id}/env` |
| Manage domains | `GET /v5/domains` |
