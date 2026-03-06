# Bitrix24 REST for AI Agents (Ultimate Guide)

Last reviewed against `bitrix24/b24restdocs` commit `66a5c0e8420a78c40b7fe7c7cf474d8bac8cb2be` (2026-02-14).

## Table of Contents

- [1. Scope of This Reference](#1-scope-of-this-reference)
- [2. Quick Architecture Decisions](#2-quick-architecture-decisions)
- [3. Auth, Identity, and Access](#3-auth-identity-and-access)
- [4. Request Patterns and Protocol](#4-request-patterns-and-protocol)
- [5. Scopes Strategy (Least Privilege)](#5-scopes-strategy-least-privilege)
- [6. High-Value Method Playbook](#6-high-value-method-playbook)
- [7. batch Without Shooting Yourself in the Foot](#7-batch-without-shooting-yourself-in-the-foot)
- [8. Limits and Throughput Engineering](#8-limits-and-throughput-engineering)
- [9. Error Handling Matrix](#9-error-handling-matrix)
- [10. Events: Reliability Patterns](#10-events-reliability-patterns)
- [11. Security Hardening Checklist](#11-security-hardening-checklist)
- [12. AI-Agent Design Patterns for Bitrix24](#12-ai-agent-design-patterns-for-bitrix24)
- [13. REST 3.0 for Agentic Integrations](#13-rest-30-for-agentic-integrations)
- [14. Production Runbook Templates](#14-production-runbook-templates)
- [15. Common Failure Modes and Fixes](#15-common-failure-modes-and-fixes)
- [16. Recommended Build Sequence for New Integrations](#16-recommended-build-sequence-for-new-integrations)
- [17. Contract Test Checklist](#17-contract-test-checklist)
- [18. Scripts Included in This Skill](#18-scripts-included-in-this-skill)
- [19. Primary Sources](#19-primary-sources)
- [20. Notes About External Recommendations](#20-notes-about-external-recommendations)

## 1. Scope of This Reference

Use this guide when building AI-agent integrations with Bitrix24 for:
- CRM operations (leads/deals/contacts/companies/activities),
- task automation,
- event-driven sync,
- robust webhook/OAuth pipelines,
- performance and reliability hardening.

This is an implementation guide, not a full API catalog.
For exact fields and method schemas, use official API method pages and OpenAPI (REST 3.0).

## 2. Quick Architecture Decisions

### 2.1 Auth model selection

| Scenario | Recommended model | Why |
|---|---|---|
| One portal, internal integration | Incoming webhook | Fastest setup, no OAuth dance |
| Multi-tenant app or marketplace app | OAuth 2.0 | Required for scalable app installs |
| Embedded local app with UI | OAuth 2.0 | App context + placements/events |
| Backend-only service for one portal | Webhook or OAuth | Choose webhook for simplicity, OAuth for stricter governance |

### 2.2 Event model selection

| Requirement | Use | Notes |
|---|---|---|
| React quickly to user actions | Online events | Delivery is async via queue; no retries |
| Guarantee recoverable sync | Offline events | Pull queue with `event.offline.get` and clear processed items |
| Hybrid wake-up + reliable fetch | `ONOFFLINEEVENT` + offline queue | Efficient and resilient |

### 2.3 REST version selection

| Need | Prefer |
|---|---|
| Stable broad coverage and SDK compatibility | REST v2 (`/rest/...`) |
| Unified response format, relations, OpenAPI endpoint | REST v3 (`/rest/api/...`) |

Important: official docs indicate SDKs may not fully support `/rest/api/` paths yet.

## 3. Auth, Identity, and Access

### 3.1 Incoming webhook

Webhook URL format:

```text
https://{portal}/rest/{user_id}/{webhook_code}/{method}
```

Key properties:
- bound to permissions of the user who created it,
- scopes configured at webhook creation time,
- no expiration by default (treat as long-lived secret),
- not suitable for broad marketplace distribution.

### 3.2 OAuth 2.0

Use for local and marketplace apps:
1. Redirect user to portal authorization endpoint with `client_id`.
2. Receive temporary `code` on `redirect_uri`.
3. Exchange `code` for `access_token` and `refresh_token` at `https://oauth.bitrix24.tech/oauth/token/`.
4. Refresh tokens on expiry.

Critical detail:
- authorization code lifetime is very short (30 seconds in docs), exchange immediately.

### 3.3 Effective permissions model

Request execution is constrained by:
1. auth mechanism (webhook or OAuth token),
2. granted scopes,
3. permissions of the acting Bitrix24 user.

If UI user cannot access entity X, API calls under that user context also fail.

### 3.4 Multi-tenant token and secret model

Never keep one global token or one global `application_token`.
Store credentials per tenant (portal/member) and per auth model.

Minimum schema:
- `tenant_id` (internal id),
- `member_id`,
- `domain`,
- `auth_mode` (`webhook` or `oauth`),
- `webhook_url` or OAuth token bundle,
- `application_token`,
- `scope`,
- `updated_at`.

Hard rules:
- resolve tenant from verified request context before calling Bitrix,
- use tenant-scoped encryption key or KMS envelope keying,
- rotate webhook/secret per tenant independently.

### 3.5 OAuth refresh race control (singleflight/lock)

In multi-worker systems, concurrent token refresh causes hard-to-debug auth flapping.
Use a lock keyed by tenant:
- lock key example: `b24:refresh:{tenant_id}`,
- only one worker calls refresh endpoint,
- others wait and then read updated tokens from storage.

Pseudo-flow:
1. request fails with `expired_token`/401,
2. attempt tenant lock acquisition,
3. if lock acquired: refresh token, persist, release lock,
4. if lock not acquired: wait briefly, reload token, retry once.

### 3.6 OAuth endpoint canonical source

Use `https://oauth.bitrix24.tech/oauth/token/` as the canonical OAuth token endpoint.
If you see `oauth.bitrix.info` in old snippets, treat it as legacy and verify against current official docs.

## 4. Request Patterns and Protocol

### 4.1 Endpoints

REST v2:
- Webhook: `https://{portal}/rest/{user_id}/{webhook}/{method}`
- OAuth: `https://{portal}/rest/{method}` with `"auth": "{access_token}"` in payload

REST v3:
- Webhook: `https://{portal}/rest/api/{user_id}/{webhook}/{method}`
- OAuth: `https://{portal}/rest/api/{method}` with `"auth": "{access_token}"`

### 4.2 Content and format

- Use HTTPS only.
- Prefer JSON request body for POST where supported.
- Default response format is JSON.

### 4.3 Example: webhook call

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"fields":{"TITLE":"Lead from AI agent"}}' \
  "https://{portal}/rest/{user_id}/{webhook}/crm.lead.add"
```

### 4.4 Example: OAuth call

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"fields":{"TITLE":"Lead from AI agent"},"auth":"{access_token}"}' \
  "https://{portal}/rest/crm.lead.add"
```

## 5. Scopes Strategy (Least Privilege)

Build scope list from required methods, not from guesswork.

Common scopes:
- `crm` for CRM methods,
- `task` for tasks (prefer this current scope; old `tasks*` scopes are legacy),
- `im`, `imbot`, `imopenlines` for chat/bot/open lines scenarios,
- `user` (`user_brief`, `user_basic`) for user data,
- `bizproc`, `catalog`, `sale`, `telephony`, etc. by module.

Failure signal for insufficient permissions:
- `insufficient_scope` or `INVALID_CREDENTIALS` depending on context.

## 6. High-Value Method Playbook

Use this as a practical starting set.

### 6.1 Core utility

- `user.current`
- `user.get`
- `department.get`

### 6.2 CRM (examples)

- `crm.lead.add`
- `crm.lead.list`
- `crm.lead.update`
- `crm.deal.add`
- `crm.deal.list`
- `crm.deal.update`

### 6.3 Tasks (examples)

- `tasks.task.add`
- `tasks.task.get`
- `tasks.task.list`
- `tasks.task.update`
- `tasks.task.complete`

### 6.4 Events and sync

- `event.bind`
- `event.get`
- `event.unbind`
- `event.offline.list`
- `event.offline.get`
- `event.offline.clear`
- `event.offline.error`

### 6.5 Dynamic event discovery (`events`)

Do not hardcode event catalogs for long-lived apps.
Use method `events` in app authorization context:
- `SCOPE` for module-specific events,
- `FULL=true` for broad inventory.

This reduces drift between environments (cloud/on-prem, app scopes, version differences).

### 6.6 Chat-bot integration constraints (high impact)

When implementing `imbot` flows, enforce these constraints:
- `imbot.command.register`: `COMMAND` must follow platform command format restrictions (no spaces/special chars).
- command localization payload must satisfy current platform validation rules.
- For multiple bot commands in one app, handler endpoint must be shared; route internally by event payload.
- `imbot.message.add` and `imbot.command.answer`: `ATTACH`, `KEYBOARD`, `MENU` have 30 KB limits each.
- `ONIMBOTMESSAGEADD`: auth tokens may be missing in some callbacks; keep previously stored app tokens.

### 6.7 Capability packs (thin skill model)

Keep runtime policy thin and expand by packs:
- `core`
- `comms`
- `automation`
- `collab`
- `content`
- `boards`
- `commerce`
- `services`
- `platform`
- `sites`
- `compliance`
- `diagnostics`

Companion docs in this skill:
- `references/packs.md`
- `references/catalog-core.md`
- `references/catalog-comms.md`
- `references/catalog-automation.md`
- `references/catalog-collab.md`
- `references/catalog-content.md`
- `references/catalog-boards.md`
- `references/catalog-commerce.md`
- `references/catalog-services.md`
- `references/catalog-platform.md`
- `references/catalog-sites.md`
- `references/catalog-compliance.md`
- `references/catalog-diagnostics.md`
- `references/chains-core.md`
- `references/chains-comms.md`
- `references/chains-automation.md`
- `references/chains-collab.md`
- `references/chains-content.md`
- `references/chains-boards.md`
- `references/chains-commerce.md`
- `references/chains-services.md`
- `references/chains-platform.md`
- `references/chains-sites.md`
- `references/chains-compliance.md`
- `references/chains-diagnostics.md`

## 7. `batch` Without Shooting Yourself in the Foot

`batch` lets you execute multiple method calls in one request.

Constraints and rules:
- max 50 commands per batch,
- nested `batch` calls are disallowed in modern REST versions,
- use `halt=1` for transactional-like stop-on-first-error behavior,
- for `cmd` URL fragments, apply proper URL encoding (can require double encoding in edge cases).

Template:

```json
{
  "halt": 1,
  "cmd": {
    "get_user": "user.current",
    "get_department": "department.get?ID=$result[get_user][UF_DEPARTMENT][0]"
  }
}
```

Response parsing checklist:
- `result.result` for successful command outputs,
- `result.result_error` for per-command errors,
- `result.result_total` and `result.result_next` for list pagination metadata,
- `time` and `result.result_time` for latency telemetry.

### 7.1 Pagination and full-sync safety

Do not stop after first page from `*.list` methods.
Always iterate until pagination cursor is exhausted.

Safe full-sync pattern:
1. initialize `start` (or equivalent cursor) to `0`,
2. request page with deterministic ordering,
3. append results,
4. continue while next cursor exists,
5. store checkpoint only after successful page persistence.

For large exports:
- split by date windows plus pagination,
- combine with `batch` only when you can still debug failures cleanly.

## 8. Limits and Throughput Engineering

### 8.1 Intensity limits (cloud)

Docs describe a leaky-bucket model with tariff-dependent parameters:
- Enterprise: drain ~5 req/s, block threshold ~250.
- Other plans: drain ~2 req/s, block threshold ~50.

On excess:
- HTTP `503`, error `QUERY_LIMIT_EXCEEDED`.

### 8.2 Resource/operating limits

Bitrix24 returns timing metadata under `time`.
For cloud, docs describe a method-level operating budget over a 10-minute window.
When exceeded, that method can be temporarily blocked.

Important fields:
- `time.operating`,
- `time.operating_reset_at`.

### 8.3 Backoff policy (recommended)

For transient overload (`503`, `QUERY_LIMIT_EXCEEDED`, `5xx`):
1. exponential backoff with jitter,
2. bounded retries,
3. circuit breaker on sustained overload.

Pseudo-policy:
- retry delays: `0.5s`, `1s`, `2s`, `4s`, `8s` + random jitter,
- cap total retries (for example, 5),
- log each retry with correlation id.

### 8.4 Distributed rate limiter for multi-worker deployments

Backoff alone is not enough when many workers share one portal quota.
Use a shared limiter (Redis/token bucket/leaky bucket) keyed by portal:
- limiter key example: `b24:rate:{domain}`,
- reserve token before call,
- release/adjust on response and error class.

Recommended behavior:
- soft budget below published threshold (for headroom),
- separate limits for heavy methods,
- dynamic slowdown after repeated `QUERY_LIMIT_EXCEEDED`.

## 9. Error Handling Matrix

| Error code | Typical reason | Action |
|---|---|---|
| `NO_AUTH_FOUND` | bad webhook/access token | verify secret/token source and env |
| `INVALID_CREDENTIALS` | user lacks permissions | adjust user role or run under correct account |
| `insufficient_scope` | missing scope | add scope and reinstall/reissue auth |
| `expired_token` | OAuth token expired | refresh via OAuth token endpoint |
| `QUERY_LIMIT_EXCEEDED` | request burst too high | backoff, queue, batch optimization |
| `ERROR_BATCH_LENGTH_EXCEEDED` | oversized batch payload | split batch |
| `ERROR_BATCH_METHOD_NOT_ALLOWED` | disallowed method in batch | call method directly |
| `OVERLOAD_LIMIT` | manual overload block | escalate to Bitrix24 support |
| `ACCESS_DENIED` | non-commercial plan limits | verify portal plan/subscription |
| `PAYMENT_REQUIRED` | app/payment status issue | verify subscription and app status |

## 10. Events: Reliability Patterns

### 10.1 Online events

Properties:
- asynchronous delivery via Bitrix queue server,
- can arrive with delay,
- no retry on failed handler response.

Implication:
- do not treat online event delivery as guaranteed exactly-once flow.

### 10.2 Offline events

Offline events are queue records consumed by your app.

Reliable pattern:
1. call `event.offline.get` with `clear=0`,
2. process batch,
3. call `event.offline.clear` with `process_id` (and optional message ids),
4. on processing failure, report via `event.offline.error` as needed.

Poison-message handling:
- keep bounded retry count per event/object key,
- after retry budget exhaustion, move item to DLQ,
- continue pipeline instead of blocking entire sync loop.

Minimum DLQ record:
- tenant/domain,
- event name,
- object id,
- payload hash,
- last error code/message,
- retry count,
- first_seen/last_seen timestamps.

Benefits:
- deduplicated object-level changes in queue,
- better control for sync pipelines.

### 10.3 Avoiding feedback loops

When your integration updates Bitrix after receiving Bitrix-originated changes, use `auth_connector` where supported:
- bind offline handler with `auth_connector`,
- send modifying calls with the same connector,
- this suppresses self-originated event noise.

Docs note tariff constraints for parts of this mechanism (for example, Pro+ conditions).

### 10.4 Event handler security

Always validate `application_token` against value stored at install time.
This is critical especially for uninstall callbacks where OAuth auth data may not be usable.

### 10.5 Installation completion gate (`installFinish`)

For apps with UI/install wizard flow:
- `event.bind`/placements may appear successful before finalization,
- but event delivery and app UI behavior can stay blocked until installation is finished.

Use `installFinish` from the install page flow where required and verify with `app.info`.

## 11. Security Hardening Checklist

- Store webhook URLs and OAuth secrets in secret manager/env, never in frontend bundles.
- Enforce TLS.
- Mask secrets in logs.
- Rotate compromised webhook immediately.
- Verify `application_token` on each event callback.
- Validate callback source using signed/token checks and strict parsing.
- Deny destructive operations without explicit user confirmation and audit trail.

For on-prem/networked installations, account for required outbound/inbound access:
- `oauth.bitrix24.tech`,
- Bitrix24 developer/market infrastructure domains listed in your official deployment docs,
- dynamic webhook source IP list from the official Bitrix24 webhook IP feed endpoint documented for your installation.

Operational note:
- some third-party guides cite other IP feed URLs; prefer the URL documented in official Bitrix24 network-access docs.

## 12. AI-Agent Design Patterns for Bitrix24

### 12.1 Recommended role split

- Planner: chooses methods, scopes, and fallback plan.
- Executor: performs API calls with retries, token refresh, and rate controls.
- Reconciler: handles offline sync queue and idempotent replay.

### 12.2 Write safety protocol

Before mutating operations:
1. fetch current object (`get/list`) and validate preconditions,
2. compute intended delta,
3. (optional but recommended) ask for confirmation if destructive/high-impact,
4. execute update,
5. re-read object to verify final state.

Add optimistic concurrency where possible:
- compare last known update timestamp/version before write,
- if object changed since read, abort and re-plan update,
- never blindly overwrite fields from stale snapshots.

### 12.3 Idempotency approach

Bitrix methods may not provide generic idempotency keys.
Implement idempotency in your service layer:
- external operation id,
- dedup table with TTL,
- replay-safe update semantics.

### 12.4 Observability minimum

Log fields per request:
- `portal`,
- `method`,
- `auth_mode` (`webhook`/`oauth`),
- `attempt`,
- `duration_ms`,
- `http_status`,
- `error_code`,
- entity id(s),
- correlation id.

Track SLO metrics:
- success rate per method,
- p95 latency,
- rate-limit incidents,
- token refresh failures,
- event lag and queue depth.

### 12.5 Policy enforcement layer (method allowlist)

AI agents must call Bitrix only through a policy gateway.
Enforce:
- method allowlist per tenant and environment,
- optional denylist for destructive endpoints,
- parameter validation (required/forbidden fields),
- confirmation gate for dangerous actions.

Example policy classes:
- `read_only`: only `*.get`, `*.list`, `user.current`,
- `crm_writer`: allow CRM create/update but block delete,
- `admin_ops`: explicit manual approval required.

## 13. REST 3.0 for Agentic Integrations

Highlights:
- endpoint prefix `/rest/api/`,
- unified result/error shape,
- relation selection in response,
- OpenAPI endpoint (`documentation` / `rest.documentation.openapi`).

Practical value for agents:
- simpler parsing logic,
- fewer follow-up calls for related entities,
- easier automatic tool generation from OpenAPI.

Adoption strategy:
1. prefer v3 where method exists,
2. use v2 fallback for unsupported areas,
3. isolate transport layer so version switch is configuration-driven.

## 14. Production Runbook Templates

### 14.1 Health check flow

1. `user.current` smoke test.
2. one read call in each critical module (`crm`, `task`, etc.).
3. one small write in sandbox/test entity.
4. event callback probe endpoint validation.
5. offline queue poll + clear cycle test.

### 14.2 Retry wrapper pseudocode (TypeScript)

```ts
async function callBitrixWithRetry(callFn: () => Promise<any>) {
  const maxAttempts = 5;
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await callFn();
    } catch (err: any) {
      const code = err?.error || err?.code;
      const retryable = code === "QUERY_LIMIT_EXCEEDED" || err?.status >= 500;
      if (!retryable || attempt === maxAttempts) throw err;
      const base = 500 * Math.pow(2, attempt - 1);
      const jitter = Math.floor(Math.random() * 250);
      await new Promise((r) => setTimeout(r, base + jitter));
    }
  }
}
```

### 14.3 Event callback skeleton (Node.js/Express)

```js
app.post("/bitrix/events", express.urlencoded({ extended: true }), (req, res) => {
  const event = req.body?.event;
  const auth = req.body?.auth || {};
  const appToken = auth.application_token;
  const memberId = auth.member_id;

  const tenant = tenantStore.findByMemberId(memberId);
  if (!tenant) {
    return res.status(404).json({ ok: false, reason: "unknown_tenant" });
  }

  if (!appToken || appToken !== tenant.applicationToken) {
    return res.status(403).json({ ok: false, reason: "invalid_application_token" });
  }

  // enqueue event for async processing
  queue.push({ tenantId: tenant.id, event, payload: req.body });
  return res.json({ ok: true });
});
```

### 14.4 Offline sync loop skeleton

```text
loop:
  batch = event.offline.get(clear=0)
  if empty -> sleep
  process every item idempotently with retry budget
  if retries exhausted -> move to DLQ
  on success -> event.offline.clear(process_id)
  on failure -> event.offline.error(...) and retry policy
```

### 14.5 OAuth refresh lock skeleton

```text
on request failure with expired token:
  if acquire(lock: tenant_refresh_lock):
    refreshed = oauth.refresh(refresh_token)
    save refreshed tokens
    release lock
  else:
    wait short delay
    reload tokens from store
  retry request once with latest token
```

## 15. Common Failure Modes and Fixes

1. Agent writes from frontend with webhook:
- Fix: move Bitrix calls to backend only.

2. Random 403 despite valid token:
- Fix: re-check user rights and scope grants separately.

3. Event losses under high burst:
- Fix: do not rely on online events only; shift to offline queue model.

4. Slow sync jobs timing out:
- Fix: reduce per-request payload, use list methods and controlled batch, honor operating limits.

5. Self-triggered infinite update loops:
- Fix: use `auth_connector` strategy and state-diff guard.

## 16. Recommended Build Sequence for New Integrations

1. Define business operations and required entities.
2. Map operations to exact Bitrix methods.
3. Derive minimal scopes.
4. Choose auth model.
5. Implement resilient API client (retry, refresh, metrics).
6. Add write safety protocol.
7. Add events/offline sync pipeline.
8. Add audit logs and dashboards.
9. Run load tests respecting limit model.
10. Roll out gradually with feature flags.

## 17. Contract Test Checklist

Run these tests before production rollout:

1. Auth isolation:
- tenant A token cannot access tenant B routes/state.

2. OAuth refresh race:
- N parallel expired-token requests produce one refresh call.

3. Scope enforcement:
- method outside allowlist is blocked before hitting Bitrix.

4. Pagination completeness:
- full-sync test fixture returns expected total count across pages.

5. Rate limit behavior:
- synthetic burst triggers limiter slowdown, not cascading failures.

6. Offline event reliability:
- crash after `event.offline.get(clear=0)` does not lose events.

7. DLQ flow:
- poison event lands in DLQ after bounded retries and does not block queue.

8. Idempotent writes:
- replayed command does not create duplicate side effects.

9. Observability:
- logs include tenant id, method, status, error code, correlation id.

## 18. Scripts Included in This Skill

- `scripts/bitrix24_client.py`:
  HTTP client with webhook/OAuth support, retries, and token-refresh hook.
- `scripts/offline_sync_worker.py`:
  Offline events worker with bounded retries, DLQ output, and safe clear flow.

Use them as a baseline; adapt storage, queues, and locks to your runtime.

## 19. Primary Sources

- Main docs repository: https://github.com/bitrix24/b24restdocs
- First call and webhook basics: https://github.com/bitrix24/b24restdocs/blob/main/first-steps/first-rest-api-call.md
- Access and scopes overview: https://github.com/bitrix24/b24restdocs/blob/main/first-steps/access-to-rest-api.md
- OAuth protocol: https://github.com/bitrix24/b24restdocs/blob/main/settings/oauth/index.md
- Limits and throttling: https://github.com/bitrix24/b24restdocs/blob/main/limits.md
- General call principles: https://github.com/bitrix24/b24restdocs/blob/main/settings/how-to-call-rest-api/general-principles.md
- Batch: https://github.com/bitrix24/b24restdocs/blob/main/settings/how-to-call-rest-api/batch.md
- System errors: https://github.com/bitrix24/b24restdocs/blob/main/_includes/system-errors.md
- Events overview: https://github.com/bitrix24/b24restdocs/blob/main/api-reference/events/index.md
- Event bind: https://github.com/bitrix24/b24restdocs/blob/main/api-reference/events/event-bind.md
- Offline events: https://github.com/bitrix24/b24restdocs/blob/main/api-reference/events/offline-events.md
- Event handler security: https://github.com/bitrix24/b24restdocs/blob/main/api-reference/events/safe-event-handlers.md
- REST 3.0 overview: https://github.com/bitrix24/b24restdocs/blob/main/api-reference/rest-v3/index.md
- Scopes list: https://github.com/bitrix24/b24restdocs/blob/main/api-reference/scopes/permissions.md
- Network access: https://github.com/bitrix24/b24restdocs/blob/main/settings/cloud-and-on-premise/network-access.md
- MCP for Bitrix24 docs access:
  - https://github.com/bitrix24/b24restdocs/blob/main/sdk/mcp.md

## 20. Notes About External Recommendations

When importing guidance from blogs/chats/slides:
- verify OAuth/token endpoint hostnames against official docs,
- verify webhook source IP feed URL against official docs,
- treat chat-bot pages marked as "docs are being updated" as useful but validate on live methods/events,
- avoid assuming non-Bitrix "skills.md" fields are supported by this Codex skill runtime.
