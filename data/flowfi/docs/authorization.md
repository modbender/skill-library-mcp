# Authorization

The user generates a JWT (e.g. via the app) and sends it to OpenClaw. Use that token for all API calls below.

**Long-lived API token (bearer):** **POST** `/auth/bearer-token`  
Requires existing JWT in `Authorization: Bearer <token>`.

| Field              | Type   | Required | Description        |
|--------------------|--------|----------|--------------------|
| `expiresInSeconds` | number | yes      | 60–31536000 (1 yr) |

Response: new JWT to use as `Authorization: Bearer <token>` for API clients.

**Revoke all bearer tokens:** **POST** `/auth/bearer-token/revoke` (with JWT). Session sign-in tokens are not affected.

**Using the token:** For all protected routes, send header:  
`Authorization: Bearer <your-jwt>`.
