# Asana OAuth Provider

## Overview

Asana uses OAuth 2.0 with granular `<resource>:<action>` scopes. TapAuth supports PKCE and refresh tokens for Asana.

## Key Gotchas

### Granular Scopes Require Pre-Registration
All scopes must be registered in the [Asana Developer Console](https://app.asana.com/0/developer-console) before use. Requesting an unregistered scope causes an authorization error.

### Short-Lived Access Tokens
Access tokens expire in **1 hour**. TapAuth automatically handles refresh using long-lived refresh tokens.

### API Response Envelope
All Asana API responses are wrapped in a `{ data: ... }` envelope:
```json
{ "data": { "gid": "1234", "name": "My Task" } }
```

### Use `opt_fields`
Without `opt_fields`, Asana returns only `gid` and `name`. Always specify the fields you need:
```
GET /tasks/1234?opt_fields=name,assignee,due_on,completed
```

### Workspace-Scoped Data
A user may belong to multiple workspaces. The token grants access to all workspaces the user belongs to.

### Rate Limits
1,500 requests per minute per token. 429 responses include a `Retry-After` header.

## Scopes

### Default (Read-Only + Identity)
- `tasks:read` — Read tasks
- `projects:read` — Read projects
- `users:read` — Read user information
- `workspaces:read` — Read workspaces
- `openid` — OpenID Connect identity
- `email` — User email address
- `profile` — User profile info

### Write Scopes (Request Only When Needed)
- `tasks:write` — Create and update tasks
- `projects:write` — Create and update projects
- `stories:write` — Create and update comments
- `attachments:write` — Upload attachments
- `tags:write` — Create and update tags

### Delete Scopes
- `tasks:delete`, `projects:delete`, `attachments:delete`, `webhooks:delete`

## Example Usage

```bash
# List tasks in a project
curl -H "Authorization: Bearer {access_token}" \
  "https://app.asana.com/api/1.0/projects/{project_gid}/tasks?opt_fields=name,assignee,due_on"

# Get current user
curl -H "Authorization: Bearer {access_token}" \
  "https://app.asana.com/api/1.0/users/me?opt_fields=gid,name,email"
```

## API Reference
- Base URL: `https://app.asana.com/api/1.0/`
- Docs: https://developers.asana.com/reference
