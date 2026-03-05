# HL Privateer -- API Reference

Complete REST and WebSocket API surface for HL Privateer.

Part of the skill package at `https://hlprivateer.xyz/skills/`.

## Base URLs

| Service | URL |
|---------|-----|
| REST API | `https://api.hlprivateer.xyz` |
| WebSocket | `wss://ws.hlprivateer.xyz` |
| Web UI | `https://hlprivateer.xyz` |

## Authentication Model

| Route Group | Auth Method |
|-------------|------------|
| Public (`/v1/public/*`) | None |
| Health (`/healthz`) | None |
| Agent (`/v1/agent/*`) | x402 payment per call |
| Operator (`/v1/operator/*`) | Bearer JWT with role claims |

### x402 Payment (Agent Routes)

Agent endpoints require x402 payment. On first request, the server responds `402 Payment Required` with a `PAYMENT-REQUIRED` header. The client signs a payment and retries with `PAYMENT-SIGNATURE`. On success, the response includes `PAYMENT-RESPONSE`.

- Network: Base (eip155:8453)
- Asset: USDC (`0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`)
- Facilitator: `https://facilitator.payai.network`
- Protocol: x402 v2 (exact scheme)

See `x402.md` in this directory for the full payment flow.

### Operator JWT

Operator routes require a Bearer token obtained via login:

```
Authorization: Bearer <jwt>
```

Roles: `operator_view` (read-only), `operator_admin` (full control).

---

## REST Endpoints

### Public (free, no auth)

#### GET /v1/public/pnl

Current PnL percentage and runtime mode.

Response:

```json
{
  "pnlPct": 1.92,
  "mode": "READY",
  "updatedAt": "2026-02-13T16:20:00Z"
}
```

#### GET /v1/public/floor-snapshot

Public floor snapshot with mode, PnL, health, account value, positions, and ops tape.

#### GET /v1/public/floor-tape

Recent ops log lines from all agent roles.

#### GET /healthz

Service health check. Returns `200` when healthy.

---

### Agent (x402 paid)

All agent endpoints are GET requests unless noted otherwise.

#### GET /v1/agent/stream/snapshot -- $0.01

Live desk snapshot: runtime mode, PnL%, health indicators, open positions, and recent ops tape.

#### GET /v1/agent/positions -- $0.01

Full position array with symbols, sides, sizes, entry prices, and unrealized PnL.

#### GET /v1/agent/orders -- $0.01

All open orders currently on the book.

#### GET /v1/agent/analysis?latest=true -- $0.01

Latest AI strategist analysis including thesis, signals, and confidence.

#### GET /v1/agent/analysis -- $0.01

Analysis history. Supports query parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `latest` | boolean | If `true`, returns only the most recent analysis |
| `correlationId` | string | Filter by correlation ID |
| `limit` | number | Max results (default 20) |

#### GET /v1/agent/insights?scope=market -- $0.02

Risk configuration, signal timeline, and account snapshot.

#### GET /v1/agent/insights?scope=ai -- $0.02

Full AI dashboard: floor state, risk posture, analysis summary, and copy-trade overview.

#### GET /v1/agent/copy/trade?kind=signals -- $0.03

Audit trail of proposals, analysis outputs, risk decisions, and basket events.

#### GET /v1/agent/copy/trade?kind=positions -- $0.03

Position data formatted for copy-trading integration.

#### POST /v1/agent/handshake

Agent handshake for session establishment.

Request:

```json
{
  "type": "agent.hello",
  "agentId": "bot-abc",
  "agentVersion": "1.2.0",
  "capabilities": ["stream.read", "command.status"],
  "requestedTier": "tier2",
  "proof": "<jwt-or-x402-proof>"
}
```

Response:

```json
{
  "type": "agent.welcome",
  "sessionId": "ses_01J...",
  "grantedTier": "tier1",
  "capabilities": ["stream.read", "command.status"],
  "quota": { "rpm": 120, "daily": 5000 },
  "expiresAt": "2026-02-14T12:00:00Z"
}
```

#### GET /v1/agent/entitlement

Check current entitlement status for the authenticated agent.

#### POST /v1/agent/command

Execute a command as an external agent (subject to tier permissions).

Request:

```json
{
  "command": "/status",
  "args": [],
  "reason": "periodic-check"
}
```

#### POST /v1/agent/unlock/:tier

Unlock a higher access tier via payment proof.

---

### Operator (JWT auth)

#### POST /v1/operator/login

Mint a short-lived JWT. Requires `x-operator-login-secret` header in production.

#### POST /v1/operator/refresh

Refresh an expiring JWT.

#### GET /v1/operator/status

Full runtime status including mode, positions, risk state, and service health.

#### GET /v1/operator/positions

Detailed position data (unredacted).

#### GET /v1/operator/orders

All orders with full lifecycle state.

#### GET /v1/operator/audit

Audit log entries. Supports query parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `from` | ISO datetime | Start of time range |
| `to` | ISO datetime | End of time range |
| `limit` | number | Max results (1-5000, default 200) |

#### POST /v1/operator/command

Execute operator commands.

Request:

```json
{
  "command": "/halt",
  "args": [],
  "reason": "volatility-breakout"
}
```

Available commands: `/status`, `/positions`, `/risk-policy`, `/halt`, `/resume`, `/flatten`, `/explain`

#### PATCH /v1/operator/config/risk

Update risk configuration parameters.

#### POST /v1/operator/replay/start

Start a replay session for incident analysis.

#### GET /v1/operator/replay

Stream replay events. Supports parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `from` | ISO datetime | Start time |
| `to` | ISO datetime | End time |
| `correlationId` | string | Filter by correlation ID |
| `resource` | string | Filter by audit resource or stream |
| `limit` | number | Max results (1-5000, default 200) |

#### GET /v1/operator/replay/export

Export replay data.

---

### Internal

#### GET /health

Internal health check.

#### GET /metrics

Prometheus metrics endpoint.

---

## x402 Behavior

### Route Pricing

| Endpoint | Price |
|----------|-------|
| `/v1/agent/stream/snapshot` | $0.01 |
| `/v1/agent/positions` | $0.01 |
| `/v1/agent/orders` | $0.01 |
| `/v1/agent/analysis?latest=true` | $0.01 |
| `/v1/agent/analysis` | $0.01 |
| `/v1/agent/insights?scope=market` | $0.02 |
| `/v1/agent/insights?scope=ai` | $0.02 |
| `/v1/agent/copy/trade?kind=signals` | $0.03 |
| `/v1/agent/copy/trade?kind=positions` | $0.03 |

### Payment Flow

```
Client  -> GET /v1/agent/positions
Server  -> 402 Payment Required
            PAYMENT-REQUIRED: <Base64 JSON>
Client  -> GET /v1/agent/positions
            PAYMENT-SIGNATURE: <Base64 JSON signed payment>
Server  -> 200 OK
            PAYMENT-RESPONSE: <Base64 JSON settlement>
            Body: { positions data }
```

### Capability Gates

Each route maps to a required capability:

| Capability | Route |
|-----------|-------|
| `stream.read.public` | `/v1/agent/stream/snapshot` |
| `analysis.read` | `/v1/agent/analysis` |
| `market.data.read` | `/v1/agent/insights?scope=market` |
| `agent.insights.read` | `/v1/agent/insights?scope=ai` |
| `copy.signals.read` | `/v1/agent/copy/trade?kind=signals` |
| `copy.positions.read` | `/v1/agent/copy/trade?kind=positions` |
| `command.positions` | `/v1/agent/positions`, `/v1/agent/orders` |

---

## WebSocket Protocol

### Connection

Connect to `wss://ws.hlprivateer.xyz`. Authentication determines available channels:

- **Public**: no token required, limited to public channels
- **Operator**: JWT with role claims
- **Agent**: API key + entitlement token or x402 proof session

### Message Envelope

All messages follow this shape:

```json
{
  "type": "string",
  "ts": "2026-02-13T16:05:00Z",
  "requestId": "optional-string",
  "channel": "optional-string",
  "payload": {}
}
```

### Client Messages

| Type | Purpose | Example |
|------|---------|---------|
| `sub.add` | Subscribe to a channel | `{ "type": "sub.add", "channel": "public.tape" }` |
| `sub.remove` | Unsubscribe | `{ "type": "sub.remove", "channel": "public.tape" }` |
| `cmd.exec` | Execute a command | `{ "type": "cmd.exec", "payload": { "command": "/status" } }` |
| `ping` | Keepalive | `{ "type": "ping" }` |

### Server Messages

| Type | Purpose |
|------|---------|
| `sub.ack` | Subscription confirmed |
| `event` | Channel event with payload |
| `cmd.result` | Command result |
| `error` | Error response |
| `pong` | Keepalive response |

### Event Types

| Event | Description |
|-------|-------------|
| `market.tick` | Market data update |
| `strategy.proposal` | New strategy proposal |
| `risk.decision` | Risk engine ALLOW/DENY |
| `execution.order` | Order placed/modified/cancelled |
| `execution.fill` | Order fill |
| `ui.floor` | Floor tape event |
| `payment.entitlement` | Entitlement grant/revoke |
| `system.alert` | System alert |

### Event Payload Example

```json
{
  "type": "event",
  "channel": "operator.execution",
  "payload": {
    "eventType": "execution.fill",
    "orderId": "ord_01J...",
    "symbol": "HYPE",
    "qty": 12.5,
    "price": 23.14,
    "ts": "2026-02-13T16:21:12Z"
  }
}
```

### Backpressure

The server maintains a bounded queue per connection. On overflow, low-priority channels are dropped first. Critical alerts are always delivered.

---

## Zod Contracts

```ts
import { z } from "zod";

export const RuntimeMode = z.enum([
  "INIT", "WARMUP", "READY", "IN_TRADE",
  "REBALANCE", "HALT", "SAFE_MODE"
]);

export const PublicPnlResponseSchema = z.object({
  pnlPct: z.number(),
  mode: RuntimeMode,
  updatedAt: z.string().datetime()
});

export const OperatorCommandSchema = z.object({
  command: z.enum([
    "/status", "/positions", "/risk-policy",
    "/halt", "/resume", "/flatten", "/explain"
  ]),
  args: z.array(z.string()).default([]),
  reason: z.string().min(3)
});

export const WsEnvelopeSchema = z.object({
  type: z.string(),
  ts: z.string().datetime(),
  requestId: z.string().optional(),
  channel: z.string().optional(),
  payload: z.unknown()
});
```

---

## Error Model

All errors return a standard envelope:

```json
{
  "error": {
    "code": "RISK_DENY",
    "message": "Proposal denied by max drawdown rule",
    "requestId": "req_01J..."
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `PAYMENT_REQUIRED` | 402 | x402 payment needed |
| `UNAUTHORIZED` | 401 | Missing or invalid authentication |
| `FORBIDDEN` | 403 | Insufficient tier or capability |
| `NOT_FOUND` | 404 | Resource not found |
| `RISK_DENY` | 422 | Risk engine denied the action |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Related Files

- Skill definition: https://hlprivateer.xyz/skills/hl-privateer.md
- x402 payment guide: https://hlprivateer.xyz/skills/x402.md
- Machine-readable discovery: https://hlprivateer.xyz/skills/agents.json
- Agent quick start: https://hlprivateer.xyz/skills/llms.txt
