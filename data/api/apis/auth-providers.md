# Index

| API | Line |
|-----|------|
| Clerk | 2 |
| WorkOS | 185 |
| Stytch | 280 |

---

# Clerk

Drop-in authentication with user management, organizations, and session handling.

## Base URL
`https://api.clerk.com/v1`

## Authentication
Bearer token via `Authorization` header using secret key from Clerk Dashboard.

```bash
# Example auth
curl https://api.clerk.com/v1/users \
  -H "Authorization: Bearer $CLERK_SECRET_KEY"
```

Secret keys start with `sk_live_` (production) or `sk_test_` (development).

## Core Endpoints

### List Users
```bash
curl https://api.clerk.com/v1/users \
  -H "Authorization: Bearer $CLERK_SECRET_KEY"
```

### Get User
```bash
curl https://api.clerk.com/v1/users/{user_id} \
  -H "Authorization: Bearer $CLERK_SECRET_KEY"
```

### Create User
```bash
curl -X POST https://api.clerk.com/v1/users \
  -H "Authorization: Bearer $CLERK_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email_address": ["user@example.com"],
    "password": "securePassword123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Update User
```bash
curl -X PATCH https://api.clerk.com/v1/users/{user_id} \
  -H "Authorization: Bearer $CLERK_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{"first_name": "Jane"}'
```

### List Organizations
```bash
curl https://api.clerk.com/v1/organizations \
  -H "Authorization: Bearer $CLERK_SECRET_KEY"
```

### Create Organization
```bash
curl -X POST https://api.clerk.com/v1/organizations \
  -H "Authorization: Bearer $CLERK_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Acme Inc", "created_by": "user_xxx"}'
```

### Verify Session Token
```bash
curl https://api.clerk.com/v1/sessions/{session_id}/verify \
  -H "Authorization: Bearer $CLERK_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{"token": "session_token_here"}'
```

## Rate Limits
Based on plan. Check Clerk Dashboard for current limits.

## Gotchas
- **Backend API only** — use Clerk.js or SDKs for frontend authentication flows
- Secret key must never be exposed client-side
- `email_address` and `phone_number` are arrays, not strings
- User IDs prefixed with `user_`, org IDs with `org_`
- Sessions managed automatically via Clerk SDKs — rarely need direct API calls
- Webhooks available for real-time user events

## Links
- [Docs](https://clerk.com/docs)
- [Backend API Reference](https://clerk.com/docs/reference/backend-api)
- [SDK Reference](https://clerk.com/docs/references/backend/overview)
# Auth0

Enterprise-grade authentication and authorization platform.

## Base URL
`https://{your-tenant}.auth0.com` (or custom domain)

## Authentication
Two main APIs with different auth:
- **Authentication API**: OAuth flows, no API key needed
- **Management API**: Bearer token (Machine-to-Machine token)

```bash
# Get Management API token
curl -X POST https://{tenant}.auth0.com/oauth/token \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "$CLIENT_ID",
    "client_secret": "$CLIENT_SECRET",
    "audience": "https://{tenant}.auth0.com/api/v2/",
    "grant_type": "client_credentials"
  }'

# Use Management API
curl https://{tenant}.auth0.com/api/v2/users \
  -H "Authorization: Bearer $MGMT_TOKEN"
```

## Core Endpoints

### Authentication API - Get Token
```bash
curl -X POST https://{tenant}.auth0.com/oauth/token \
  -H "Content-Type: application/json" \
  -d '{
    "grant_type": "password",
    "username": "user@example.com",
    "password": "password",
    "client_id": "$CLIENT_ID",
    "client_secret": "$CLIENT_SECRET",
    "audience": "https://myapi.example.com"
  }'
```

### Management API - List Users
```bash
curl https://{tenant}.auth0.com/api/v2/users \
  -H "Authorization: Bearer $MGMT_TOKEN"
```

### Management API - Get User
```bash
curl https://{tenant}.auth0.com/api/v2/users/{user_id} \
  -H "Authorization: Bearer $MGMT_TOKEN"
```

### Management API - Create User
```bash
curl -X POST https://{tenant}.auth0.com/api/v2/users \
  -H "Authorization: Bearer $MGMT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "connection": "Username-Password-Authentication"
  }'
```

### Management API - Update User
```bash
curl -X PATCH https://{tenant}.auth0.com/api/v2/users/{user_id} \
  -H "Authorization: Bearer $MGMT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "user_metadata": {"preference": "dark"}}'
```

## Rate Limits
- Management API: Varies by endpoint and plan
- Authentication API: Based on plan
- Pagination: Max 50 results per page (use `page` and `per_page` params)

## Gotchas
- **Two separate APIs**: Authentication (user-facing) vs Management (admin)
- Management API token expires — cache and refresh as needed
- User IDs include connection prefix: `auth0|`, `google-oauth2|`, etc.
- `connection` field required when creating users
- `user_metadata` for user-editable data, `app_metadata` for app-controlled data
- Rate limits vary significantly by endpoint — check docs for specifics

## Links
- [Docs](https://auth0.com/docs)
- [Authentication API](https://auth0.com/docs/api/authentication)
- [Management API](https://auth0.com/docs/api/management/v2)
# WorkOS

Enterprise-ready features: SSO, Directory Sync, Audit Logs, and User Management.

## Base URL
`https://api.workos.com`

## Authentication
Bearer token via `Authorization` header using API key from WorkOS Dashboard.

```bash
# Example auth
curl https://api.workos.com/organizations \
  -H "Authorization: Bearer $WORKOS_API_KEY"
```

API keys prefixed with `sk_` (secret key). Never expose in client-side code.

## Core Endpoints

### List Organizations
```bash
curl https://api.workos.com/organizations \
  -H "Authorization: Bearer $WORKOS_API_KEY"
```

### Create Organization
```bash
curl -X POST https://api.workos.com/organizations \
  -H "Authorization: Bearer $WORKOS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Acme Inc", "domains": ["acme.com"]}'
```

### Get SSO Authorization URL
```bash
curl "https://api.workos.com/sso/authorize?client_id=$CLIENT_ID&redirect_uri=https://myapp.com/callback&response_type=code&connection=$CONNECTION_ID"
```

### Exchange Code for Profile (SSO)
```bash
curl -X POST https://api.workos.com/sso/token \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "$CLIENT_ID",
    "client_secret": "$CLIENT_SECRET",
    "grant_type": "authorization_code",
    "code": "$AUTH_CODE"
  }'
```

### List Directory Users (SCIM)
```bash
curl https://api.workos.com/directory_users?directory=$DIRECTORY_ID \
  -H "Authorization: Bearer $WORKOS_API_KEY"
```

### List Directory Groups (SCIM)
```bash
curl https://api.workos.com/directory_groups?directory=$DIRECTORY_ID \
  -H "Authorization: Bearer $WORKOS_API_KEY"
```

### Create Audit Log Event
```bash
curl -X POST https://api.workos.com/audit_logs/events \
  -H "Authorization: Bearer $WORKOS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "org_xxx",
    "event": {
      "action": "user.login",
      "actor": {"id": "user_123", "type": "user"},
      "targets": [{"id": "user_123", "type": "user"}],
      "context": {"location": "192.168.1.1"}
    }
  }'
```

## Rate Limits
- Default: Rate limited per endpoint
- Returns HTTP 429 when exceeded
- Use exponential backoff for retries

## Gotchas
- **Staging vs Production**: Separate environments with different API keys
- Pagination uses `after`/`before` cursors, not page numbers
- SSO requires connection setup per organization in Dashboard
- Directory Sync webhooks deliver user/group changes — poll sparingly
- Audit Logs require organization_id — scope events to orgs

## Links
- [Docs](https://workos.com/docs)
- [API Reference](https://workos.com/docs/reference)
- [SSO Guide](https://workos.com/docs/sso/guide)
# Stytch

Modern authentication with passwordless options: magic links, OTPs, OAuth, and more.

## Base URL
- **Test**: `https://test.stytch.com/v1`
- **Live**: `https://api.stytch.com/v1`

## Authentication
Basic authentication with `project_id` and `secret` from Stytch Dashboard.

```bash
# Example auth
curl https://test.stytch.com/v1/users \
  -u "$PROJECT_ID:$SECRET" \
  -H "Content-Type: application/json"
```

## Core Endpoints

### Create User
```bash
curl -X POST https://test.stytch.com/v1/users \
  -u "$PROJECT_ID:$SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": {"first_name": "Ada", "last_name": "Lovelace"}
  }'
```

### Send Magic Link
```bash
curl -X POST https://test.stytch.com/v1/magic_links/email/send \
  -u "$PROJECT_ID:$SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "login_magic_link_url": "https://myapp.com/authenticate",
    "signup_magic_link_url": "https://myapp.com/authenticate"
  }'
```

### Authenticate Magic Link Token
```bash
curl -X POST https://test.stytch.com/v1/magic_links/authenticate \
  -u "$PROJECT_ID:$SECRET" \
  -H "Content-Type: application/json" \
  -d '{"token": "magic_link_token_here"}'
```

### Send OTP via SMS
```bash
curl -X POST https://test.stytch.com/v1/otps/sms/send \
  -u "$PROJECT_ID:$SECRET" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+15551234567"}'
```

### Authenticate OTP
```bash
curl -X POST https://test.stytch.com/v1/otps/authenticate \
  -u "$PROJECT_ID:$SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "method_id": "phone_number_id_xxx",
    "code": "123456"
  }'
```

### OAuth Authentication
```bash
# Redirect user to:
https://test.stytch.com/v1/public/oauth/google/start?public_token=$PUBLIC_TOKEN

# Exchange token after redirect:
curl -X POST https://test.stytch.com/v1/oauth/authenticate \
  -u "$PROJECT_ID:$SECRET" \
  -H "Content-Type: application/json" \
  -d '{"token": "oauth_token_here"}'
```

### Get Session
```bash
curl -X POST https://test.stytch.com/v1/sessions/authenticate \
  -u "$PROJECT_ID:$SECRET" \
  -H "Content-Type: application/json" \
  -d '{"session_token": "session_token_here"}'
```

## Rate Limits
Based on plan. Check Stytch Dashboard for current limits.

## Gotchas
- **Two environments**: Test (`test.stytch.com`) vs Live (`api.stytch.com`)
- IDs include environment: `user-test-xxx` vs `user-live-xxx`
- Uses **Basic auth**, not Bearer tokens
- Magic links and OTPs require separate send + authenticate calls
- Sessions return `session_token` and `session_jwt` — use either for subsequent requests
- Phone numbers must include country code: `+1` for US

## Links
- [Docs](https://stytch.com/docs)
- [API Reference](https://stytch.com/docs/api)
- [SDK Reference](https://stytch.com/docs/sdks)
