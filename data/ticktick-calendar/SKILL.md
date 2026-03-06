---
name: ticktick
description: "TickTick task/project integration toolkit for OAuth2 authorization, token refresh, and typed task/project operations. Use when users need to authenticate with TickTick, run task/project CRUD workflows, or operate the OpenClaw/Codex wrapper via token.json."
metadata: {"openclaw":{"requires":{"env":["TICKTICK_CLIENT_ID","TICKTICK_CLIENT_SECRET","TICKTICK_REDIRECT_URI"]},"primaryEnv":"TICKTICK_CLIENT_SECRET"}}
---

# TickTick Skill

Operate TickTick task/project workflows with strict contracts, runtime token management, typed API access, and OpenClaw-ready action wrappers.

## Quick Reference

| Situation | Action |
|-----------|--------|
| First-time OAuth authorization needed | Run `npm run ticktick:cli -- auth-url`, then `auth-exchange` with callback URL |
| Token expired but refresh token exists | Use runtime/CLI auto-refresh path (`getAccessTokenWithAutoReauth`) |
| Token missing or refresh failed | Reauthorize from emitted URL and rerun command |
| Need task creation/update/complete | Use `runtime.useCases.createTask/updateTask/completeTask` or skill actions |
| Need task/project listing | Use `runtime.useCases.listTasks/listProjects` or CLI commands |
| Need OpenClaw action integration | Use `skill-entry/ticktick-skill.mjs` and expose 5 MVP actions |
| Need error categorization for UX/retry | Handle `TickTickDomainError` categories from `src/shared/error-categories.ts` |

## Capabilities

- OAuth2 contract + runtime token client
  - Authorization URL build/callback parse
  - Authorization-code exchange
  - Refresh-token renewal
- Typed API client with timeout/retry/error typing
  - HTTP timeout and exponential backoff for retryable failures
- Core usecases (MVP 5)
  - `create_task`
  - `list_tasks`
  - `update_task`
  - `complete_task`
  - `list_projects`
- OpenClaw/Codex wrapper entrypoints
  - `skill-entry/token-manager.mjs`
  - `skill-entry/ticktick-skill.mjs`
  - `scripts/ticktick-cli.mjs`

## Prerequisites

Required environment variables:

- `TICKTICK_CLIENT_ID`
- `TICKTICK_CLIENT_SECRET`
- `TICKTICK_REDIRECT_URI`

Optional runtime defaults:

- `TICKTICK_OAUTH_AUTHORIZE_URL` (default: `https://ticktick.com/oauth/authorize`)
- `TICKTICK_OAUTH_TOKEN_URL` (default: `https://ticktick.com/oauth/token`)
- `TICKTICK_API_BASE_URL` (default: `https://api.ticktick.com/open/v1`)
- `TICKTICK_API_TIMEOUT_MS` (default: `10000`)
- `TICKTICK_API_MAX_RETRIES` (default: `3`)
- `TICKTICK_API_RETRY_BASE_DELAY_MS` (default: `250`)
- `TICKTICK_OAUTH_SCOPE`
- `TICKTICK_USER_AGENT`

Token and notification options:

- `TICKTICK_TOKEN_PATH` (default: `~/.config/ticktick/token.json`)
- `TICKTICK_REAUTH_WEBHOOK_URL`
- `TICKTICK_REAUTH_NOTIFY_COOLDOWN_MS`
- `TICKTICK_REAUTH_NOTIFY_STATE_PATH`

## OpenClaw Setup (Recommended)

OpenClaw integration is provided through `createTickTickOpenClawSkill` in `skill-entry/ticktick-skill.mjs`.

### Skill action surface

Expose the following actions:

- `create_task`
- `list_tasks`
- `update_task`
- `complete_task`
- `list_projects`

### Runtime/token behavior

1. Parse env via `parseTickTickEnvFromRuntime`.
2. Resolve token path (`options.tokenPath` -> `TICKTICK_TOKEN_PATH` -> default path).
3. Load access token with auto refresh (`getAccessTokenWithAutoReauth`).
4. On missing/expired token without valid refresh token:
   - raise `ReauthRequiredError`
   - optionally notify via webhook
   - surface reauthorization URL to caller.

## CLI Workflow (Practical)

### 1) Generate OAuth URL

```bash
npm run ticktick:cli -- auth-url
```

### 2) Exchange callback for token file

```bash
npm run ticktick:cli -- auth-exchange --callbackUrl "http://localhost:3000/oauth/callback?code=...&state=..."
```

### 3) Run actions

```bash
npm run ticktick:cli -- list-projects
npm run ticktick:cli -- list-tasks --projectId <projectId> --limit 20
npm run ticktick:cli -- create-task --projectId <projectId> --title "Write docs" --priority 3
npm run ticktick:cli -- update-task --taskId <taskId> --priority 5
npm run ticktick:cli -- complete-task --taskId <taskId>
```

## Programmatic Workflow

1. Load env: `parseTickTickEnvFromRuntime()`
2. Build runtime: `createTickTickRuntime({ env, getAccessToken })`
3. Execute usecases via `runtime.useCases.*`
4. Handle category-mapped errors in caller for retry/UX behavior
5. Persist/rotate token outside process memory when used in production

## Error Mapping Contract

Normalize API/runtime errors to domain categories:

| Category | Typical Source |
|----------|----------------|
| `auth_401` | Invalid/expired access token |
| `auth_403` | Scope/permission denied |
| `not_found_404` | Missing task/project resource |
| `rate_limit_429` | TickTick rate-limited request |
| `server_5xx` | TickTick server-side failure |
| `network` | Timeout, transport, DNS, fetch failures |
| `validation` | Input contract or payload mismatch |
| `unknown` | Non-classified fallback |

## Verification Gates

Run after any implementation or integration change:

```bash
npm run typecheck
npm test
```

If either gate fails, do not finalize until fixed or explicitly accepted by user.

## Troubleshooting

### Token file not found

- Symptom: `ReauthRequiredError` with message about missing token file
- Action: run `auth-url` -> complete browser consent -> run `auth-exchange`

### Token expired and refresh unavailable

- Symptom: runtime/CLI asks for reauthorization URL
- Action: complete OAuth again and persist new token JSON

### 401/403 on valid token

- Verify OAuth app scopes and redirect URI alignment
- Confirm `.env` values match TickTick app configuration

### 429/5xx spikes

- Check retry settings:
  - `TICKTICK_API_MAX_RETRIES`
  - `TICKTICK_API_RETRY_BASE_DELAY_MS`
- Add higher-level caller backoff if workload is bursty

## References

- `README.md`
- `docs/openclaw-skill-guide.md`
- `skill-entry/token-manager.mjs`
- `skill-entry/ticktick-skill.mjs`
- `scripts/ticktick-cli.mjs`
- `src/core/ticktick-runtime.ts`
- `src/core/ticktick-usecases.ts`
- `src/api/ticktick-api-client.ts`
- `src/api/ticktick-gateway.ts`
- `src/shared/error-categories.ts`
