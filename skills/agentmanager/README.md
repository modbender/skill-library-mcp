# Agent Manager

Agent Manager is a Node.js + TypeScript + Express orchestration service for external AI clients.
It supports dynamic multi-agent planning, asynchronous run execution, incremental events, strict budget controls, and safe tool usage.

## Highlights

- Dynamic planning over HTTP with pluggable planner strategies.
- Asynchronous `/v1/run` execution with `run_id` polling and `/v1/run/:id/events` incremental feeds.
- Optional client-supplied plan execution (`POST /v1/run` with `plan`).
- Cost-aware execution with model tiers, owner pricing caps, retries, upgrades, and fallback.
- Tool hardening for public usage:
  - registration disabled by default
  - path traversal protection in `file_store`
  - arithmetic-only safe `js_eval`
- Run controls:
  - cancellation endpoint `/v1/run/:id/cancel`
  - event ring buffer cap
  - artifact bytes cap per run


## LLM provider

Agent Manager uses a provider adapter contract and treats the gateway provider as the recommended default.
This keeps the engine stable and avoids vendor SDK maintenance inside Agent Manager.

Routing priority is:
1. `task.provider_id`
2. `run.options.provider_id`
3. `DEFAULT_PROVIDER_ID` (or `LLM_PROVIDER`)
4. fallback `mock`

Use `GET /v1/provider-adapter/schema` to fetch the adapter request and response schema plus examples for implementing a custom gateway.

## Environment variables

| Variable | Default | Description |
|---|---:|---|
| `PORT` | `3000` | HTTP server port |
| `PERSIST_RUNS` | `0` | Persist run files under `./runs` when `1` |
| `ENABLE_TOOL_REGISTER` | `0` | Enable `POST /v1/tools/register` when `1` |
| `TOKENOWNER_MAX_RUNNING` | `8` | Max concurrently running runs per token owner |
| `TOKENOWNER_MAX_PER_MINUTE` | `60` | Max run creations/minute per token owner |
| `TOOL_ALLOWLIST` | empty | Comma-separated tool names allowed for external registration only (built-in tools remain available) |
| `MAX_EVENTS_PER_RUN` | `2000` | Max events stored per run (ring-buffer behavior) |
| `MAX_ARTIFACT_BYTES_PER_RUN` | `5000000` | Max artifact bytes written per run |
| `LLM_PROVIDER` | `gateway` | Preferred provider id if `DEFAULT_PROVIDER_ID` is not set |
| `DEFAULT_PROVIDER_ID` | `gateway` | Default provider id used by registry resolution |
| `GATEWAY_URL` | empty | Base URL for the provider adapter gateway |
| `GATEWAY_STEP_PATH` | `/v1/llm/step` | Gateway adapter path joined to `GATEWAY_URL` |
| `GATEWAY_API_KEY` | empty | Optional bearer token sent to gateway |
| `GATEWAY_TIMEOUT_MS` | `30000` | Provider-level timeout cap for gateway calls |
| `SSE_HEARTBEAT_MS` | `15000` | SSE idle heartbeat interval |
| `REQUIRE_RUN_TOKEN` | `0` | Require `X-Run-Token` when set to `1` |
| `RUN_TOKENS` | empty | Comma-separated allowed run tokens when auth is enabled |
| `OUTBOUND_ALLOWLIST` | empty | Comma-separated outbound allowlist for provider and gateway targets. Supports exact host, wildcard subdomain, optional scheme and port pinning |
| `TOOL_CALLBACK_ALLOWLIST` | empty | Comma-separated outbound allowlist for callback tools |
| `MAX_PROVIDER_REQUEST_BYTES` | `1000000` | Maximum JSON payload bytes for outbound provider requests |
| `MAX_TOOL_CALLBACK_REQUEST_BYTES` | `200000` | Maximum JSON payload bytes for outbound callback tool requests |
| `REDACT_TELEMETRY` | `0` | Enable telemetry redaction on replay/report/events/stream when set to `1` |
| `REDACT_TELEMETRY_MODE` | `none` | Redaction mode: `none`, `hash`, `truncate` |
| `REDACT_TELEMETRY_TRUNCATE_CHARS` | `200` | Truncate length when redaction mode is `truncate` |


## Planner strategies

Available strategies are returned by `GET /v1/capabilities`.

- `heuristic_v1` (default): existing heuristic behavior.
- `safe_minimal_v2`: prefers single mode and stricter tool usage.

Use strategy hints in:

- `POST /v1/plan` -> `options.strategy_hint`
- `POST /v1/run` -> `options.strategy_hint`

Additional split-control options are supported in `options` for both endpoints:
`goal_type`, `risk_level`, `must_verify`, `tool_preference`, `latency_hint_ms`, `max_cost_override`.

Unknown hints return:

```json
{ "code": "STRATEGY_NOT_FOUND", "message": "...", "retryable": false, "at": "strategy_hint" }
```

## Key endpoints

### POST /v1/plan

```json
{
  "user_request": "Analyze and verify with tools",
  "options": {
    "budget_level": "normal",
    "strategy_hint": "safe_minimal_v2"
  }
}
```

### POST /v1/plan/validate

```json
{
  "plan": {
    "mode": "single",
    "rationale": "client plan",
    "budget": {
      "max_steps": 2,
      "max_tool_calls": 2,
      "max_latency_ms": 2000,
      "max_cost_estimate": 1,
      "max_model_upgrades": 1
    },
    "invariants": [],
    "success_criteria": [],
    "tasks": [
      {
        "name": "single_executor",
        "agent": "executor",
        "input": "compute",
        "depends_on": [],
        "tools_allowed": ["js_eval"],
        "model": "gpt-lite",
        "reasoning_level": "low",
        "max_output_tokens": 80
      }
    ],
    "output_contract": { "type": "json" }
  }
}
```

### POST /v1/run

With planner:

```json
{
  "user_request": "Analyze and verify",
  "idempotency_key": "run-1",
  "options": {
    "budget_level": "normal",
    "strategy_hint": "heuristic_v1",
    "max_concurrency": 8
  }
}
```

With client plan:

```json
{
  "plan": { "mode": "single", "rationale": "client", "budget": { "max_steps": 1, "max_tool_calls": 1, "max_latency_ms": 1000, "max_cost_estimate": 1, "max_model_upgrades": 0 }, "invariants": [], "success_criteria": [], "tasks": [{ "name": "single_executor", "agent": "executor", "input": "compute", "depends_on": [], "tools_allowed": [], "model": "gpt-lite", "reasoning_level": "low", "max_output_tokens": 64 }], "output_contract": { "type": "json" } }
}
```

Response:

```json
{ "run_id": "...", "status": "queued" }
```

### POST /v1/run/:id/cancel

A cancellation request aborts queued/running runs and appends `run_cancelled` event.

Cancels queued/running runs and returns run object with:

```json
{
  "error": {
    "code": "RUN_CANCELLED",
    "message": "Run cancelled",
    "retryable": false,
    "at": "cancel"
  }
}
```

### GET /v1/run/:id/events?after=n

```json
{
  "next": 12,
  "events": [
    { "ts": 1700000000000, "type": "task_start", "run_id": "...", "task_name": "planner", "data": {} }
  ]
}
```

### GET /v1/capabilities

Includes machine-readable service capabilities, strategy list, defaults, rate limits, endpoint templates, and provider catalog metadata (`llm_providers`).

### GET /openapi.json

Returns OpenAPI JSON document for client generation/discovery.

### GET /v1/provider-adapter/schema

Returns adapter contract schema, endpoint path, and request/response examples for gateway implementations.

## Run locally

```bash
npm ci
npm run test
npm run build
npm run start
```


### POST /v1/run/sync

Optional synchronous wrapper for short tasks. It enqueues a run and waits up to `RUN_SYNC_TIMEOUT_MS` (default `30000`) for terminal state.

### Events cursor response

`GET /v1/run/:id/events?after=n` returns:

```json
{
  "base": 120,
  "next": 128,
  "events": [],
  "truncated": false
}
```

- `base` is the current global cursor start in the ring buffer.
- `truncated=true` indicates the requested cursor was older than retained events.


### GET /v1/run/:id/report

Returns a consolidated run report from in-memory state: plan summary, task results, events (with `logs_base`), metrics, and final output fields.

## Dry run behavior

Set `options.dry_run=true` on `POST /v1/run` or `POST /v1/run/sync` to validate and normalize execution inputs without creating a run.

Dry-run response shape:

```json
{
  "ok": true,
  "dry_run": true,
  "normalized_plan": { "mode": "single" },
  "estimated_cost": 0.08,
  "estimated_latency_ms": 35000,
  "task_count": 1
}
```

Dry runs do not return `run_id` and are not stored.

## Authentication and multi-tenant controls

Optional token enforcement for shared deployments:

- `REQUIRE_RUN_TOKEN=1`
- `RUN_TOKENS=a,b,c`

When enabled, clients must send `X-Run-Token` for planning/run/report/event endpoints, including `/v1/runs`.
Invalid or missing tokens return:

```json
{ "code": "AUTH_INVALID_TOKEN", "message": "Missing or invalid X-Run-Token", "retryable": false, "at": "auth" }
```

## Run listing and resume

Use `GET /v1/runs` to list runs with pagination.

Query params:
- `limit` (default 50, max 200)
- `cursor` (opaque)
- `status` (optional)

Response:

```json
{
  "runs": [
    { "id": "...", "created_at": 1700000000000, "status": "succeeded", "plan_digest": "...", "summary": "...", "owner": "owner-a" }
  ],
  "next_cursor": "..."
}
```

## SSE stream heartbeat

`GET /v1/run/:id/stream` emits standard SSE `data:` events and heartbeat comments while idle:

```text
: ping
```

Heartbeat interval is controlled by `SSE_HEARTBEAT_MS` (default 15000).

## Error catalog endpoint

`GET /v1/errors` returns a machine-readable list of known error codes and retry guidance.

## Callback tools and timeout behavior

Registered callback tools (`callback_url`) are invoked by HTTP POST and enforce `timeout_ms`.
On timeout, tools return:

```json
{ "ok": false, "output": { "error": "TOOL_TIMEOUT", "retryable": true } }
```

## External planner first contract

- `POST /v1/plan` accepts either `{ plan, options }` for validation/recommendation or `{ user_request, options }` for backward-compatible generation.
- `POST /v1/plan/generate` keeps heuristic plan generation as a convenience endpoint.
- `GET /v1/run/:id/replay` returns a stable replay payload with plan digest and ordered events.
- `POST /v1/run/:id/task/:name/inject` allows deterministic task payload injection for queued/running tasks.

## Tool-calling protocol guarantee

When a model/provider round returns `tool_calls`, Agent Manager executes each requested tool and appends exactly one `role="tool"` message per `tool_call_id` before the next provider round.
This prevents orphaned tool calls, duplicate tool results, and protocol drift.

## Integrations

- Clawhub and other AI clients: [`skill.md`](./skill.md)


## Outbound data flow and security defaults

By default, outbound network calls are blocked unless allowlists are configured.

- Provider/gateway calls require `OUTBOUND_ALLOWLIST`.
- Callback tools require `TOOL_CALLBACK_ALLOWLIST`.
- IP literal targets are blocked.
- URLs with embedded username/password are blocked.
- Redirects are blocked with `fetch(..., { redirect: "error" })`.
- DNS resolution blocks private, loopback, link-local, multicast, and unspecified addresses.

Use `GET /v1/provider-adapter/schema` to integrate gateways safely.

## Telemetry redaction

Set `REDACT_TELEMETRY=1` to redact sensitive values in replay/report/events/stream output.

- `REDACT_TELEMETRY_MODE=hash` replaces strings with sha256 and length metadata.
- `REDACT_TELEMETRY_MODE=truncate` keeps a short preview plus length metadata.

Redaction applies to telemetry output and persisted traces, not live execution inputs.


## Configuration

Node.js requirement: `>=20` (see `package.json`).

All runtime settings are validated in `src/config.ts`.

| Variable | Default | Notes |
|---|---|---|
| PORT | 3000 | API port |
| PERSIST_RUNS | 0 | Persist run files when enabled |
| PROVIDER | gateway if `GATEWAY_URL` set, else mock | Provider selection (`gateway|openai|mock`) |
| DEFAULT_PROVIDER_ID | empty | Optional provider override |
| LLM_PROVIDER | empty | Legacy provider override |
| GATEWAY_URL | empty | Gateway base URL |
| GATEWAY_STEP_PATH | /v1/llm/step | Gateway route path |
| GATEWAY_API_KEY | empty | Bearer token for gateway calls |
| GATEWAY_TIMEOUT_MS | 30000 | Gateway timeout cap |
| OPENAI_API_KEY | empty | Enables OpenAI provider |
| ANTHROPIC_API_KEY | empty | Enables Anthropic stub provider |
| OUTBOUND_HOST_ALLOWLIST | empty | Comma-separated allowed outbound hosts (supports `.example.com`) |
| OUTBOUND_ALLOWLIST | empty | Backward-compatible outbound allowlist alias |
| OUTBOUND_ALLOW_ALL | 0 | Explicitly allow any outbound host |
| ALLOW_INSECURE_HTTP | 0 | Allow HTTP only for localhost in dev |
| ALLOW_INSECURE_HTTP_TOOLS | 0 | Allow HTTP callback tool endpoints |
| MAX_PROVIDER_REQUEST_BYTES | 1000000 | Max gateway request JSON size |
| MAX_TOOL_CALLBACK_REQUEST_BYTES | 200000 | Max callback request JSON size |
| TOOL_CALLBACK_MAX_BYTES | 262144 | Max callback response body bytes |
| ENABLE_TOOL_REGISTER / ENABLE_TOOL_REGISTRATION | 0 | Enables external tool registration endpoint |
| TOOL_ALLOWLIST | empty | Allowed externally registered tool names |
| TOOL_CALLBACK_ALLOWLIST | empty | Allowed callback destination hosts |
| REQUIRE_RUN_TOKEN | 0 | Require X-Run-Token |
| RUN_TOKENS | empty | Allowed token values when required |
| ALLOW_ANONYMOUS_READ | 0 | If 0, GET run/replay/report/events requires token even when auth not required |
| TOKENOWNER_MAX_RUNNING | 8 | Max concurrent runs per owner |
| TOKENOWNER_MAX_PER_MINUTE | 60 | Max run creations per minute per owner |
| RUN_SYNC_TIMEOUT_MS | 30000 | Sync run timeout |
| RUN_TTL_MS | 3600000 | Non-terminal run retention |
| RUN_TTL_TERMINAL_MS | 3600000 | Terminal run retention |
| MAX_RUNS_IN_MEMORY | 5000 | In-memory run cap |
| MAX_EVENTS_PER_RUN | 2000 | Event ring buffer cap |
| MAX_ARTIFACT_BYTES_PER_RUN | 5000000 | Per-run artifact cap |
| MAX_DEP_PAYLOAD_BYTES | 262144 | Dependency payload propagation cap |
| SSE_HEARTBEAT_MS | 15000 | SSE heartbeat interval |
| REDACT_TELEMETRY | 0 | Redact replay/report/events/stream payload data |
| REDACT_TELEMETRY_MODE | none | `none|hash|truncate` |
| REDACT_TELEMETRY_TRUNCATE_CHARS | 200 | Truncate length when enabled |
| REDACT_EVENTS | 0 | Redact large/sensitive event data keys |

### Outbound data flow

Outbound traffic is disabled by default unless allowlists or explicit `OUTBOUND_ALLOW_ALL=1` are configured.
Provider gateway and callback tools both use `safeFetch` protections (allowlist, DNS checks, redirect blocking, timeout, and body caps).
