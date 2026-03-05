# OpenExec

## Deterministic Execution Boundary for AI Systems

OpenExec is a deterministic execution adapter that separates **proposal**, **authorization**, and **execution** in AI systems that interact with real-world infrastructure.

If an AI system can:

- Send email
- Move money
- Modify infrastructure
- Delete data
- Call internal tools

It should not execute what it merely proposes.

OpenExec enforces that separation.

### Static Architecture Guarantees

OpenExec guarantees:

- No dynamic code loading
- No `eval`/`exec` usage
- No runtime plugin system
- No remote code execution primitives
- Static handler registry only
- No self-modifying behavior

---

## Core Principle

Nothing executes without explicit approval.

Not inferred approval.
Not model confidence.
Not heuristic safety checks.

Explicit approval.
Deterministic execution.
Verifiable receipts.

---

## What Problem This Solves

Modern AI stacks commonly collapse:

```
Reasoning -> Authorization -> Execution
```

This creates failure modes such as:

- Replay execution (duplicate payments)
- Parameter mutation between intent and action
- Escalation via prompt injection
- Silent execution without auditability
- Race conditions firing in parallel

OpenExec forces architectural separation:

```
Propose -> Approve -> Execute -> Witness
```

Execution becomes an enforceable boundary instead of a side effect.

---

## What OpenExec Does

OpenExec is a lightweight execution boundary that:

- Accepts structured execution requests
- Enforces replay protection (nonce-based)
- Performs deterministic hashing of execution inputs
- Verifies signed approval artifacts (ClawShield mode)
- Executes registered handlers deterministically
- Emits a receipt for every execution attempt
- Allows independent receipt verification

It does not:

- Define policy
- Evaluate prompts
- Decide what should be approved
- Grant permissions
- Provide OS/container sandboxing
- Override governance decisions
- Make outbound HTTP or governance calls during execution

It executes only what has already been authorized.

---

## Quickstart (Demo Mode)

Install:

```bash
pip install -r requirements.txt
```

Run:

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 5000
```

By default, bind to `127.0.0.1` unless intentionally deploying behind a firewall or reverse proxy.
Production deployments may override host binding explicitly (e.g., `--host 0.0.0.0`).

Confirm health:

```bash
curl http://localhost:5000/health
```

Execute:

```bash
curl -X POST http://localhost:5000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "echo",
    "payload": {"msg":"hello world"},
    "nonce":"unique-1"
  }'
```

Replay with same nonce -- returns original result without re-execution.

Replay protection prevents duplicate execution classes entirely.

---

## Verify a Receipt

Every execution produces a deterministic receipt.

```bash
curl -X POST http://localhost:5000/receipts/verify \
  -H "Content-Type: application/json" \
  -d '{
    "exec_id": "<id>",
    "result": "<result_json>",
    "receipt": "<hash>"
  }'
```

Receipts are evidence, not logs.
Logs can be altered. Receipts can be verified.

---

## Wrapping OpenAI Tool Calls

If your agent uses OpenAI function calling, route execution through OpenExec:

```python
import requests
from uuid import uuid4

tool_call = model_output["tool_calls"][0]

response = requests.post(
    "http://localhost:5000/execute",
    json={
        "action": tool_call["function"]["name"],
        "payload": tool_call["function"]["arguments"],
        "nonce": uuid4().hex
    }
)

result = response.json()
if not result.get("approved"):
    raise Exception("Execution blocked by OpenExec")
```

The agent proposes. OpenExec determines whether it runs.

---

## Production Mode (Signed Approval Enforcement)

Enable strict governance enforcement:

```bash
export OPENEXEC_MODE=clawshield
export CLAWSHIELD_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----..."
export CLAWSHIELD_TENANT_ID="tenant-id"
```

In this mode:

- Execution requires a signed approval artifact
- Approval hash must match execution request
- Ed25519 signature must verify
- Tenant must match
- Expired approvals are rejected
- No outbound HTTP or governance calls are performed during execution

Authority remains external to execution.

ClawShield governance layer:
[https://clawshield.forgerun.ai/](https://clawshield.forgerun.ai/)

### Cryptographic Boundary

In ClawShield mode:

- Public key is loaded from `CLAWSHIELD_PUBLIC_KEY`
- Signature verification is performed locally
- No remote verification calls occur
- The execution layer never contacts the governance service during runtime

This preserves execution determinism and prevents network-induced variability.

---

## Installation Model

OpenExec is a source-distributed Python service.
It does not install system-wide binaries or modify the host environment.

Installation consists of:

1. Installing pinned Python dependencies (`pip install -r requirements.txt`)
2. Running the FastAPI application via uvicorn
3. Optionally configuring environment variables

No dynamic downloads or runtime package installation occur.

All dependencies are pinned in `requirements.txt` for reproducible builds.

---

## Optional: Execution Allow-List

Restrict which actions may execute:

```bash
export OPENEXEC_ALLOWED_ACTIONS=echo,send_email,charge_card
```

If set:

- Any unlisted action is rejected prior to execution.

If unset:

- All registered actions are eligible (subject to approval mode).

---

## Architecture

```
        Proposal Layer (LLM / Agent)
                   |
                   v
        +------------------------+
        |        OpenExec        |
        |  Deterministic Boundary|
        +------------------------+
                   |
                   v
        +------------------------+
        |     Governance Layer   |
        |      (ClawShield)      |
        +------------------------+
                   |
                   v
        +------------------------+
        |       Witness Layer    |
        |      (ClawLedger)      |
        +------------------------+
```

Each layer is independently replaceable.

No layer can act alone.

That separation is intentional.

---

## Threat Model

OpenExec protects against:

- Replay execution (duplicate attempts)
- Forged approval artifacts (ClawShield mode)
- Parameter mutation after approval
- Silent execution without receipt
- Unauthorized execution without approval

OpenExec does NOT protect against:

- Prompt injection in proposal layer
- LLM hallucinations during proposal
- Compromised approval logic
- OS-level or container escape
- Host compromise
- Supply chain vulnerabilities in external tools

OpenExec assumes:

- The proposal layer is untrusted
- Governance decisions originate externally
- Infrastructure isolation is handled separately

---

## Formal Guarantees

OpenExec enforces the following properties:

**Deterministic Execution**

- For a given `(action, payload, nonce)` tuple, execution behavior and receipt hash are reproducible.
- Identical inputs cannot produce divergent receipts.

**Replay Protection**

- Duplicate nonce submissions are rejected.
- Prevents duplicate execution of the same request.

**Cryptographic Approval Verification (ClawShield Mode)**

- Approval artifacts must be signed using Ed25519.
- Signature verification is performed offline.
- Approval hash must match the execution request.
- Expired approvals are rejected.
- Tenant identifier must match the configured tenant.

**Network Isolation**

- OpenExec performs no outbound HTTP, RPC, or governance calls during execution.
- Signature verification is performed locally using a pre-loaded public key.
- By default, OpenExec uses a local SQLite database (`sqlite:///openexec.db`).
- Database network I/O occurs only if explicitly configured by the operator via `OPENEXEC_DB_URL`.

**Receipt Integrity**

- Every execution attempt emits a deterministic receipt.
- Receipt verification recomputes hash to confirm integrity.
- Receipts are tamper-evident.

**Authority Separation**

- Execution authority never originates from the execution layer.
- Approval logic must exist externally.

These guarantees are enforced by runtime logic, not policy heuristics.

---

## Determinism Definition

Deterministic execution means:

Given identical input parameters:

- `action`
- `payload`
- `nonce`

The execution path and receipt hash are fixed and reproducible.

OpenExec does not rely on probabilistic evaluation, heuristic scoring, or model reasoning during execution.

Execution behavior is fully defined by the registered handler and verified inputs.

---

## Security Boundary Notice

OpenExec enforces execution authority separation at the application layer.

It does not provide OS-level sandboxing.

For high-risk environments, deploy OpenExec inside:

- Docker
- gVisor
- Firecracker
- Hardened VM environments

Infrastructure isolation is a separate concern from execution authorization.

This separation is deliberate.

---

## Execution Privilege Model

OpenExec does not sandbox OS-level execution.
Handlers execute with the privileges of the hosting process.

Operators must:

- Restrict allowed actions via `OPENEXEC_ALLOWED_ACTIONS`
- Deploy inside a container or VM for high-risk workloads
- Avoid running the service as root
- Bind to localhost unless intentionally exposed to a network

These constraints are operational requirements, not optional recommendations.

---

## Network Isolation Model

OpenExec does not initiate outbound HTTP, RPC, or governance calls during execution.

Inbound HTTP is used solely to receive execution proposals.

Outbound network I/O occurs only if:

- The operator explicitly configures `OPENEXEC_DB_URL` to point to a remote database.

Signature verification is performed locally using a pre-loaded public key.

No external policy engine calls occur at runtime.

---

## Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Service info |
| `/health` | GET | Health + mode + verification status |
| `/ready` | GET | Readiness check |
| `/version` | GET | Version metadata |
| `/execute` | POST | Execute approved action |
| `/receipts/verify` | POST | Verify receipt integrity |

---

## Status

- Demo mode: stable
- Replay protection: enforced
- Deterministic receipts: enforced
- Ed25519 signature validation: implemented
- Execution allow-list: supported
- No outbound HTTP or governance calls during execution
- Database defaults to local SQLite; remote DB only if explicitly configured
- No external dependencies required for local testing

---

## Security Model & Threat Boundaries

OpenExec is an execution boundary -- not a sandbox.

For a formal description of its security assumptions, threat model,
network model, and production hardening checklist, see [SECURITY.md](SECURITY.md).

### Threat Boundary Diagram

```
Untrusted Proposal Layer
        |
        v
+------------------------------+
|        OpenExec              |
|  Deterministic Boundary      |
|  - Replay protection         |
|  - Signature verification    |
|  - Receipt generation        |
+------------------------------+
        |
        v
Optional Governance Layer (ClawShield)
        |
        v
Optional Witness Layer (Ledger)

Trust Assumptions:
- Proposal input is untrusted
- Approval artifact must be valid
- Execution handlers run with host privileges
- Infrastructure isolation is external
```

Operators are responsible for:

- Host isolation
- Network exposure controls
- TLS
- Database trust configuration
- Container or VM isolation
- Action allow-list enforcement

OpenExec enforces deterministic execution and approval integrity.
Infrastructure isolation is intentionally externalized.

---

## Security Properties Summary

| Property | Enforced |
|----------|----------|
| Replay rejection | Yes |
| Deterministic receipts | Yes |
| Signature validation | Yes (ClawShield mode) |
| Allow-list enforcement | Optional |
| Outbound HTTP/governance calls during execution | None |
| Database network I/O | Only if remote DB explicitly configured |
| OS-level sandboxing | No (external responsibility) |
| Policy decision engine | No (external responsibility) |

---

## Production Hardening (Minimum)

- Bind to `127.0.0.1` unless behind reverse proxy
- Run inside container or VM
- Do not run as root
- Restrict `OPENEXEC_ALLOWED_ACTIONS`
- Use local SQLite unless remote DB explicitly required
- Keep ClawShield private key offline (OpenExec only needs public key)
- Pin dependencies (already enforced)

---

## Security Changelog

### v0.1.9

- Eliminated packaging ambiguity
- Added formal threat boundary diagram
- Added STRIDE-lite threat mapping
- Clarified installation model as source-distributed
- No runtime logic changes

---

## Summary

If your AI system touches production infrastructure,
separate authority from execution.

OpenExec is the minimal deterministic boundary
that makes that separation enforceable.
