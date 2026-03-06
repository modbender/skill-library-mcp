---
name: meegle-api-credentials
description: |
  Obtain Meegle API access credentials: domain, token, context (project_key, user_key), and request headers.
  Read this first before any other Meegle API skill; all call prerequisites are in this skill.
metadata: {"openclaw":{"requires":{"env":["MEEGLE_PLUGIN_ID","MEEGLE_PLUGIN_SECRET","MEEGLE_DOMAIN","MEEGLE_PROJECT_KEY","MEEGLE_USER_KEY"]}}}
---

# Meegle API — Credentials (domain, token, context, headers)

Generate **domain**, **access token** (plugin or user), **context** (project_key, user_key), and **request headers** for OpenAPI. Other Meegle API skills assume you have these before calling.

## Token caching

**Cache and reuse tokens in the same session.** `plugin_access_token` is valid 7200 seconds. Obtain once, store in memory/session, reuse until expiration — do not call the token API on every request.

## Credentials and resolution

**Resolution order:** For each credential: **env var** (from OpenClaw config) → ask user. Do not ask if already set in env. For OpenClaw, credentials **must** be set via the OpenClaw config file so they apply to all sessions; see [Environment variables](#environment-variables). Other configuration methods (e.g. shell export) are not recommended.

| Credential    | Env var             | Where to obtain |
|---------------|---------------------|-----------------|
| plugin_id     | MEEGLE_PLUGIN_ID    | Meegle Developer Platform → Plugin → Basic Information |
| plugin_secret | MEEGLE_PLUGIN_SECRET| Same as above |
| domain        | MEEGLE_DOMAIN       | See [Domain](#domain) below |
| project_key   | MEEGLE_PROJECT_KEY  | Double-click **project icon**; or project URL. Use in path/body as `{project_key}`. |
| user_key      | MEEGLE_USER_KEY     | Double-click **avatar**; or `user_key` in user_access_token response. Use in header `X-User-Key` with plugin_access_token. |

**When something is missing:** First check env; if not set, tell the user which credential(s) are missing and where to get them (table above), then ask for values and retry.

## Environment variables

To have credentials available in **every OpenClaw session**, you **must** configure them in OpenClaw’s config file. This is the only supported way for cross-session persistence; other methods (e.g. shell `export`, `.env`) are not recommended. OpenClaw reads this file on startup and injects the listed env into the skill runtime.

**Config path:** `~/.openclaw/openclaw.json`

**Required structure:** Under the skill entry for `meegle-api`, set `env` with the required variable names and values. The skill name must match the index skill `name: meegle-api`.

```json
{
  "skills": {
    "entries": {
      "meegle-api": {
        "env": {
          "MEEGLE_PLUGIN_ID": "<your_plugin_id>",
          "MEEGLE_PLUGIN_SECRET": "<your_plugin_secret>",
          "MEEGLE_DOMAIN": "project.feishu.cn",
          "MEEGLE_PROJECT_KEY": "<your_project_key>",
          "MEEGLE_USER_KEY": "<your_user_key>"
        }
      }
    }
  }
}
```

- **International region:** use `MEEGLE_DOMAIN`: `project.larksuite.com`.
- If the file already has other keys (e.g. skill source), only add or update the `env` object under `skills.entries["meegle-api"]`.

## Domain

| Region         | domain                 |
|----------------|------------------------|
| International  | `project.larksuite.com` |
| China (Feishu) | `project.feishu.cn`    |

Base URL: `https://{domain}`. Example: `https://project.larksuite.com/open_api/authen/plugin_token`.

---

## Obtain Access Token

When to use, capabilities, request/response, **headers for other APIs**, constraints, and strategy: see **API Spec** below.

### API Spec: obtain_access_token

```yaml
name: meegle.obtain_access_token
description: Meegle access credentials (plugin / virtual / user token) for OpenClaw.
when_to_use: [Before any Meegle OpenAPI, When plugin token expires (2h), On-behalf-of-user operations]
capabilities: [generate_plugin_token, generate_virtual_plugin_token, exchange_user_access_token, refresh_user_access_token]

flows:
  generate_plugin_token:
    description: plugin_access_token or virtual_plugin_token
    http: { method: POST, path: /open_api/authen/plugin_token }
    headers: { Content-Type: application/json }
    body:
      plugin_id: { type: string, required: true }
      plugin_secret: { type: string, required: true }
      type: { type: integer, required: false, default: 0, enum: [0, 1] }
    response: { token: string, expire_time: integer }
    notes: Token 7200s; cache and reuse (see Token caching).

  exchange_user_access_token:
    description: Exchange auth code for user_access_token (server-side).
    prerequisites: [plugin_access_token, authorization_code from getAuthCode]
    http: { method: POST, path: /open_api/authen/user_plugin_token }
    headers: { Content-Type: application/json, X-Plugin-Token: "{{plugin_access_token}}" }
    body: { code: string, grant_type: authorization_code }
    response: { token: user_access_token, refresh_token, expire_time, refresh_token_expire_time, user_key, saas_tenant_key }

  refresh_user_access_token:
    description: Refresh expired user_access_token
    prerequisites: [plugin_access_token, refresh_token]
    http: { method: POST, path: /open_api/authen/refresh_token }
    headers: { Content-Type: application/json, X-Plugin-Token: "{{plugin_access_token}}" }
    body: { refresh_token: string, type: 1 }
    response: { token, expire_time, refresh_token, refresh_token_expire_time }

usage_in_other_skills:
  plugin_access_token: { headers: { X-Plugin-Token: "{{plugin_access_token}}", X-User-Key: "{{user_key}}" } }
  user_access_token: { headers: { X-Plugin-Token: "{{user_access_token}}" } }
constraints: [user_access_token server-side only, no OpenAPI from front-end, permissions by scope/space/role]
recommended_openclaw_strategy: [Cache plugin token globally, Bind user token to session, Auto-refresh user token, Choose token type per API]
```

### Request headers (when calling OpenAPIs)

- **plugin_access_token:** `X-Plugin-Token: {{plugin_access_token}}` and **required** `X-User-Key: {{user_key}}`.
- **user_access_token:** `X-Plugin-Token: {{user_access_token}}` (user token value; do not send `X-User-Key`).

Base URL for all calls: `https://{domain}` (see Domain). Full header details in API Spec → `usage_in_other_skills`.

---

## Skill Pack (implementation details)

Auth, context, and headers for OpenClaw integration.

### Auth Layer

```yaml
# meegle.auth.get_plugin_token (internal) — cache and reuse
name: meegle.auth.get_plugin_token
type: internal
inputs: { plugin_id: { type: string, required: true, source: secret }, plugin_secret: { type: string, required: true, source: secret }, type: { type: integer, default: 0 } }
http: { method: POST, url: "https://{domain}/open_api/authen/plugin_token" }
headers: { Content-Type: application/json }
outputs: { token: plugin_access_token, expire_time: number }
# domain = project.larksuite.com | project.feishu.cn

---
# meegle.auth.get_user_token (flow) — auth code → user_access_token
name: meegle.auth.get_user_token
type: flow
inputs: { auth_code: { type: string, required: true }, plugin_access_token: { type: string, required: true } }
http: { method: POST, url: "https://{domain}/open_api/authen/user_plugin_token" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{plugin_access_token}}" }
body: { code: "{{auth_code}}", grant_type: authorization_code }
outputs: { user_access_token, refresh_token, expire_time, refresh_token_expire_time, user_key }

---
# meegle.auth.refresh_user_token (internal)
name: meegle.auth.refresh_user_token
type: internal
inputs: { refresh_token: { type: string, required: true }, plugin_access_token: { type: string, required: true } }
http: { method: POST, url: "https://{domain}/open_api/authen/refresh_token" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{plugin_access_token}}" }
body: { type: 1 }
outputs: { user_access_token, expire_time, refresh_token, refresh_token_expire_time }
```

### Context Layer

```yaml
# meegle.context.resolve_project — project_key
name: meegle.context.resolve_project
type: utility
inputs: { project_key: { type: string, required: false } }
behavior: MEEGLE_PROJECT_KEY → config default → ask user
outputs: { project_key: string }

---
# meegle.context.resolve_user_key — user_key
name: meegle.context.resolve_user_key
type: utility
inputs: { user_key: { type: string, required: true }, user_access_token: { type: string, required: false } }
behavior: MEEGLE_USER_KEY → user_key from user_access_token → ask user
outputs: { user_key: string }
```

### Header Decision Rule

**meegle.http.prepare_headers** — inputs: `operation_type` (read|write), `plugin_access_token`, `user_access_token?`, `user_key`.

| When | Headers |
|------|---------|
| write ∧ user_access_token 存在 | `X-Plugin-Token: {{user_access_token}}` |
| read | `X-Plugin-Token: {{plugin_access_token}}`, `X-User-Key: {{user_key}}` |

### Global Constraints

- Cache plugin_access_token (7200s); user_access_token server-side only; prefer user_access_token for write; respect 15 QPS per token.
