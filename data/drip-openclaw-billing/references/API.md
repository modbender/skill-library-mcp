# OpenClaw + Drip API Reference

## Base

- Base URL: `${DRIP_BASE_URL}/v1` (must be explicitly configured)
- Auth: `Authorization: Bearer <DRIP_API_KEY>`

## Endpoint trust requirement

- Set `DRIP_BASE_URL` to an official trusted Drip endpoint.
- Do not send telemetry to unknown or unverified hosts.

## Run lifecycle

### Start run

`POST /runs`

```json
{
  "customerId": "cus_123",
  "workflowId": "wf_openclaw",
  "externalRunId": "openclaw_req_456",
  "correlationId": "trace_789",
  "metadata": { "integration": "openclaw" }
}
```

### End run

`PATCH /runs/:id`

```json
{ "status": "COMPLETED" }
```

```json
{
  "status": "FAILED",
  "errorMessage": "Provider timeout",
  "errorCode": "TOOL_TIMEOUT"
}
```

## Execution event emission

`POST /events`

```json
{
  "customerId": "cus_123",
  "runId": "run_abc",
  "actionName": "brave_search",
  "eventType": "TOOL_CALL",
  "outcome": "SUCCEEDED",
  "quantity": 1,
  "idempotencyKey": "openclaw_run_abc_brave_search_001",
  "metadata": {
    "provider": "brave",
    "endpoint": "/res/v1/web/search",
    "statusCode": 200,
    "latencyMs": 412,
    "queryHash": "9f9e2d...",
    "tokens": 0
  }
}
```

## Billable usage emission

`POST /usage`

```json
{
  "customerId": "cus_123",
  "usageType": "brave_api_calls",
  "quantity": 1,
  "idempotencyKey": "openclaw_run_abc_brave_search_001_usage",
  "metadata": {
    "runId": "run_abc",
    "provider": "brave",
    "endpoint": "/res/v1/web/search",
    "statusCode": 200,
    "latencyMs": 412,
    "queryHash": "9f9e2d..."
  }
}
```

Use `POST /usage/async` for non-blocking billing.

## Recommended meters

- `brave_search` -> `brave_api_calls`
- `google_search` -> `google_api_calls`
- generic external requests -> `api_calls`

## Deterministic request and idempotency mapping

- Prefer explicit `requestId` from caller if available.
- Otherwise derive deterministic hash from action/requester/tenant/params.
- Build idempotency keys from stable parts:
  - event: `openclaw_<runId>_<actionName>_<requestId-or-sequence>:event`
  - usage: `openclaw_<runId>_<actionName>_<requestId-or-sequence>:usage`

## Telemetry minimization

- Send only minimum fields required for billing and diagnostics.
- Do not send raw prompts, raw outputs, raw query text, credentials, or full request/response bodies.
- Use `queryHash` instead of raw query text.
