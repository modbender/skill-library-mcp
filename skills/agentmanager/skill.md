# Agent Manager skill

## What this file is for

This file is a concise integration contract for AI tool callers and gateway implementers.

This `skill.md` is a compact integration guide for Clawhub and other AI clients.

Agent Manager is an orchestration kernel for external AI planners. External AI builds plans, and Agent Manager validates, schedules, executes tools, enforces budgets, and provides replayable telemetry.

## Authentication

Use `X-Run-Token` for owner attribution and optional access control.

- `REQUIRE_RUN_TOKEN=1` enables token enforcement.
- `RUN_TOKENS` contains allowed token values.

Example header:

```http
X-Run-Token: tenant-a
```

## Capability discovery and endpoint map

Start with:

- `GET /v1/capabilities`
- `GET /v1/provider-adapter/schema`

Core endpoints:

- `POST /v1/plan` (validate plus recommendations)
- `POST /v1/plan/validate`
- `POST /v1/plan/generate`
- `POST /v1/run`
- `POST /v1/run/sync`
- `GET /v1/run/:id`
- `GET /v1/run/:id/events?after=`
- `GET /v1/run/:id/stream`
- `GET /v1/run/:id/replay`
- `GET /v1/run/:id/report` (if enabled)
- `GET /v1/runs`
- `POST /v1/run/:id/cancel`
- `POST /v1/run/:id/task/:name/inject`
- `POST /v1/tools/register` (only when enabled)

## Provider selection

Provider choice follows this order:

1. `task.provider_id`
2. `run.options.provider_id`
3. `DEFAULT_PROVIDER_ID`
4. `mock`

Read provider availability from `capabilities.llm_providers.providers` and `capabilities.llm_providers.default_provider_id`.

## Recommended client flow

1. `GET /v1/capabilities`
2. `POST /v1/plan` with `{ plan, options }`
3. `POST /v1/run` (async) or `POST /v1/run/sync`
4. Stream with `GET /v1/run/:id/stream` or poll `GET /v1/run/:id/events?after=<seq>`
5. Read final run from `GET /v1/run/:id`
6. Export replay from `GET /v1/run/:id/replay`
7. Use `POST /v1/run/:id/task/:name/inject` for deterministic overrides when needed

## Tool-calling protocol rule

When a provider returns `tool_calls`, Agent Manager appends exactly one `role="tool"` message for each `tool_call_id` before the next provider round.

This prevents protocol errors in model APIs.

## SSE reliability and resume

`GET /v1/run/:id/stream` sends event `id` from event sequence numbers.

- Resume with `Last-Event-ID` header or `?after=` query.
- If idle and run is non-terminal, heartbeat comments are emitted:

```text
: ping
```

Heartbeat interval uses `SSE_HEARTBEAT_MS` (default `15000`).

## Event types

Common emitted event types include:

- `task_start`, `task_end`, `task_retry`
- `tool_call_requested`, `tool_call_start`, `tool_call_end`, `tool_call_failed`, `tool_call_started`, `tool_call_finished`
- `llm_step_start`, `llm_step_tool_calls`, `llm_step_final`
- `llm_round_start`, `llm_round_tool_calls`, `llm_round_final`
- `budget_violation`, `fallback_start`, `fallback_end`
- `run_complete`, `run_cancel_requested`
- `dependency_truncated`, `artifact_limit`

## Replay and report data

`GET /v1/run/:id/replay` returns stable replay JSON:

```json
{
  "run": { "id": "run_123", "created_at": 1700000000000, "status": "succeeded" },
  "plan_digest": "sha256:...",
  "events": [{ "seq": 1, "type": "task_start", "run_id": "run_123" }],
  "results_index": { "task_a": { "digest_hash": "sha256:..." } }
}
```

Run cost attribution is exposed per task in `run.metrics.cost_breakdown`:

```json
{
  "metrics": {
    "cost_breakdown": {
      "task_a": {
        "cost_est": 0.0021,
        "tier": "cheap",
        "tool_calls": 1
      }
    }
  }
}
```

## HTTP callback tools and timeout enforcement

Callback tools use `callback_url` and enforce `ToolSpec.timeout_ms`.

The execution signal combines run abort plus timeout. On timeout, tool result is structured with `error_code` as `TOOL_TIMEOUT` and `retryable: true`.


## Provider adapter contract

Use `GET /v1/provider-adapter/schema` to fetch `schema_version`, request and response schemas, and examples for your gateway implementation.


## Outbound security defaults

Outbound traffic is blocked by default until allowlists are configured.

- Provider and gateway calls require `OUTBOUND_ALLOWLIST`.
- Callback tools require `TOOL_CALLBACK_ALLOWLIST`.
- IP literal hostnames and redirect chains are blocked.

## Telemetry redaction

Enable `REDACT_TELEMETRY=1` with mode `hash` or `truncate` to redact sensitive event and replay fields for shared deployments.


## Environment variables

This service uses validated configuration from `src/config.ts`. Critical outbound controls: `OUTBOUND_HOST_ALLOWLIST`, `OUTBOUND_ALLOW_ALL`, `ALLOW_INSECURE_HTTP`, `TOOL_CALLBACK_ALLOWLIST`, `MAX_PROVIDER_REQUEST_BYTES`, `MAX_TOOL_CALLBACK_REQUEST_BYTES`, and redaction flags.

## Outbound data disclosure

When gateway or callback tools are enabled, task inputs, dependency payloads, and tool payloads may be sent outbound to allowed destinations. Keep allowlists strict in shared deployments.
