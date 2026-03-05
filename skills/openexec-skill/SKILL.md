---
name: OpenExec
slug: openexec
version: 0.1.10
category: infrastructure/governance/execution
runtime: python
entrypoint: main:app
requires_network: false  # No outbound HTTP/RPC calls during execution. Inbound HTTP only.
modes:
  - demo
  - clawshield
env:
  required: none
  optional:
    - OPENEXEC_MODE
    - CLAWSHIELD_PUBLIC_KEY
    - CLAWSHIELD_TENANT_ID
    - OPENEXEC_ALLOWED_ACTIONS
    - OPENEXEC_DB_URL
description: Source-distributed deterministic execution service with pinned dependencies. Runs only with a signed approval artifact (ClawShield mode) and emits verifiable receipts. Performs no outbound HTTP or governance calls. No runtime package installation or dynamic downloads occur.
---

# OpenExec — Governed Deterministic Execution (Skill)

OpenExec is a **runnable** governed execution service.
It executes **only** what has already been approved.

It is not an agent.
It is not a policy engine.
It does not self-authorize.

OpenExec performs **no outbound HTTP, RPC, or governance calls** during signature verification or execution. All verification is fully offline. By default, OpenExec uses a local SQLite database (`sqlite:///openexec.db`). Database network I/O occurs only if explicitly configured by the operator via `OPENEXEC_DB_URL`.

---

## Install

```bash
pip install -r requirements.txt
```

## Run (local)

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 5000
```

---

## Endpoints

* `GET /` → service info (deployment health check)
* `GET /health` → health status, mode, restriction level
* `GET /ready` → readiness check
* `GET /version` → version metadata
* `POST /execute` → execute an approved action deterministically
* `POST /receipts/verify` → verify receipt hash integrity

---

## Modes

### 1) Demo mode (default, free)

No external governance required. No env vars required.

```bash
export OPENEXEC_MODE=demo
```

Demo mode still enforces:

* deterministic execution
* replay protection (nonce uniqueness)
* receipt generation

### 2) ClawShield mode (production / business)

Requires a **signed approval artifact** issued by ClawShield.
OpenExec verifies the Ed25519 signature offline using the configured public key.

```bash
export OPENEXEC_MODE=clawshield
export CLAWSHIELD_PUBLIC_KEY="-----BEGIN PUBLIC KEY----- ... -----END PUBLIC KEY-----"
export CLAWSHIELD_TENANT_ID="tenant-id"
```

If signature validation fails, execution is denied.

> Note: ClawShield governance SaaS is available at [https://clawshield.forgerun.ai/](https://clawshield.forgerun.ai/). OpenExec does not contact this URL at runtime. It is provided for reference only.

---

## Environment Variables

All environment variables are **optional**. OpenExec runs with zero configuration in demo mode.

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENEXEC_MODE` | `demo` | Execution mode: `demo` or `clawshield` |
| `CLAWSHIELD_PUBLIC_KEY` | (none) | PEM-encoded Ed25519 public key for signature verification |
| `CLAWSHIELD_TENANT_ID` | (none) | Tenant identifier for multi-tenant isolation |
| `OPENEXEC_ALLOWED_ACTIONS` | (none) | Comma-separated list of permitted actions. If unset, all registered actions are allowed |
| `OPENEXEC_DB_URL` | `sqlite:///openexec.db` | Database URL for execution record persistence |

---

## 90-Second Quickstart (Demo)

1. Start server:

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 5000
```

2. Confirm health:

```bash
curl http://localhost:5000/health
```

3. Execute a deterministic demo action:

```bash
curl -X POST http://localhost:5000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action":"echo",
    "payload":{"msg":"hello"},
    "nonce":"unique-1"
  }'
```

4. Replay attempt (returns same result, no re-execution):

```bash
curl -X POST http://localhost:5000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action":"echo",
    "payload":{"msg":"hello"},
    "nonce":"unique-1"
  }'
```

---

## Receipts

Every execution produces a receipt hash.
Receipts are **evidence**, not logs.

Verify a receipt:

```bash
curl -X POST http://localhost:5000/receipts/verify \
  -H "Content-Type: application/json" \
  -d '{"exec_id":"<id>","result":"<result_json>","receipt":"<hash>"}'
```

---

## What this skill does

* Accepts structured execution requests
* Enforces replay protection
* Executes deterministically (approved parameters only)
* Emits verifiable receipts for every attempt
* In ClawShield mode: verifies **signed approvals** before execution
* Supports optional execution allow-list via environment variable

## What this skill does not do

* Define policy
* Grant permissions
* Reason autonomously
* Override governance decisions
* Self-authorize execution
* Make outbound HTTP or governance calls during execution
* Provide OS-level sandboxing or container isolation

---

## Security Boundary Notice

OpenExec enforces execution boundaries at the application layer.
It does not provide OS-level sandboxing.
Deploy behind containerization, VM isolation, or hardened environments
when actions interact with production systems.

OpenExec enforces authority separation.
It is not a sandbox.

---

## Architecture context (3-layer separation)

* **OpenExec** -- deterministic execution adapter (this skill)
* **ClawShield** -- governance + approval minting (SaaS): [https://clawshield.forgerun.ai/](https://clawshield.forgerun.ai/)
* **ClawLedger** -- witness ledger (optional integration)

Each layer is replaceable. No single layer can act alone.

---

## Security Documentation

A full security model, threat assumptions, and production hardening
checklist are available in [SECURITY.md](SECURITY.md).

This skill intentionally separates:

- Execution enforcement (OpenExec)
- Infrastructure isolation (operator responsibility)

### Execution Safety Guarantees

This skill:

- Does not dynamically load code
- Does not evaluate user input as code
- Uses a static handler registry
- Does not install packages at runtime
- Does not fetch remote execution logic
