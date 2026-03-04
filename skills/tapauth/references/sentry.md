# Sentry OAuth Provider

## Overview

Sentry uses OAuth 2.0 with authorization code flow. Tokens are **organization-scoped** — each token is tied to the specific Sentry organization the user selects during authorization. PKCE is supported and recommended.

## Key Gotchas

### Organization-Scoped Tokens
A token is tied to the org the user selected during OAuth. To access multiple orgs, the user must authorize separately for each. The `/api/0/organizations/` endpoint returns only the connected organization.

### Scope Hierarchy
Sentry uses a `resource:action` permission model where higher levels include lower ones: `admin` includes `write`, `write` includes `read`. Request the minimum level needed.

### No Dedicated Revoke Endpoint
Tokens are invalidated by uninstalling the integration from the Sentry org settings. There is no `POST /revoke` endpoint.

### User Info in Token Response
The token exchange response includes basic user info (`id`, `name`, `email`), so a separate user info call is usually unnecessary.

### Rate Limits
Sentry enforces rate limits on API requests. Check `X-Sentry-Rate-Limit-*` response headers for current limits and retry timing.

### 30-Day Access Tokens
Access tokens expire after ~30 days (`expires_in: 2591999` seconds). Refresh tokens are provided and must be used to obtain new access tokens.

## Scopes

### Default (Read-Only)
- `org:read` — View organization details
- `project:read` — View project details
- `team:read` — View team details
- `member:read` — View organization members
- `event:read` — View events and issues

### Write Scopes (Request Only When Needed)
- `org:write` — Modify organization settings
- `project:write` — Modify project settings
- `project:releases` — Manage releases
- `team:write` — Modify teams
- `member:write` — Invite/modify members
- `event:write` — Modify events (resolve, merge, etc.)

### Admin Scopes (Use With Caution)
- `org:admin`, `project:admin`, `team:admin`, `member:admin`, `event:admin` — Full control including deletion

Scopes are space-separated (Sentry convention).

## Example Usage

```bash
# List issues for an organization
curl -H "Authorization: Bearer {access_token}" \
  "https://sentry.io/api/0/organizations/{org_slug}/issues/"

# Get project details
curl -H "Authorization: Bearer {access_token}" \
  "https://sentry.io/api/0/projects/{org_slug}/{project_slug}/"

# Get authenticated user info
curl -H "Authorization: Bearer {access_token}" \
  "https://sentry.io/api/0/"
```

## API Reference
- Base URL: `https://sentry.io/api/0/`
- Docs: https://docs.sentry.io/api/
