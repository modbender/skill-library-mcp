---
name: kevros
description: "Precision decisioning, agentic trust, and verifiable identity for autonomous agents"
version: 0.3.6
metadata:
  openclaw:
    requires:
      env:
        - KEVROS_API_KEY
      bins: []
    primaryEnv: KEVROS_API_KEY
    always: false
    skillKey: kevros
    os:
      - linux
      - macos
      - windows
    install:
      - kind: uv
        package: kevros
        bins: []
---

# Kevros

Three cryptographic primitives for autonomous agents: precision decisioning, provenance attestation, and intent binding.

Every decision gets a signed release token. Every action gets a hash-chained record. Every intent gets a cryptographic binding to its command. Downstream services verify independently — no callbacks, no trust assumptions.

**Base URL:** `https://governance.taskhawktech.com`

## Quick Start

Get an API key (free, instant, no payment):

```bash
curl -X POST https://governance.taskhawktech.com/signup \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "your-agent-id"}'
```

Response:

```json
{
  "api_key": "kvrs_...",
  "tier": "free",
  "monthly_limit": 100,
  "usage": {
    "header": "X-API-Key"
  }
}
```

Use the API key in all subsequent requests via the `X-API-Key` header.

## Precision Decisioning

**POST /governance/verify**

Verify an action against policy bounds before execution. Returns ALLOW, CLAMP, or DENY with a cryptographic release token that any downstream service can verify independently.

Request:

```json
{
  "action_type": "api_call",
  "action_payload": {
    "endpoint": "/deploy",
    "service": "api-v2",
    "replicas": 3
  },
  "agent_id": "your-agent-id",
  "policy_context": {
    "max_values": { "replicas": 5 },
    "forbidden_keys": ["sudo", "force"]
  }
}
```

Response:

```json
{
  "decision": "ALLOW",
  "verification_id": "a1b2c3d4-...",
  "release_token": "f7a8b9c0...",
  "applied_action": {
    "endpoint": "/deploy",
    "service": "api-v2",
    "replicas": 3
  },
  "reason": "All values within policy bounds",
  "epoch": 42,
  "provenance_hash": "e3b0c442...",
  "timestamp_utc": "2026-02-26T12:00:00Z"
}
```

- **ALLOW** — proceed as planned. The `release_token` is proof.
- **CLAMP** — action was adjusted to safe bounds. Use `applied_action` instead of your original.
- **DENY** — action rejected. Do not proceed. `release_token` is null.

Share the `release_token` with collaborating agents so they can independently verify the decision.

## Provenance Attestation

**POST /governance/attest**

Record a completed action in a hash-chained, append-only evidence ledger. Each attestation extends your provenance chain. Your raw payload is SHA-256 hashed — actual data is never stored.

Request:

```json
{
  "agent_id": "your-agent-id",
  "action_description": "Deployed api-v2 with 3 replicas",
  "action_payload": {
    "service": "api-v2",
    "replicas": 3,
    "status": "success"
  },
  "context": {
    "environment": "production",
    "triggered_by": "scheduled"
  }
}
```

Response:

```json
{
  "attestation_id": "b2c3d4e5-...",
  "epoch": 43,
  "hash_prev": "e3b0c442...",
  "hash_curr": "a1b2c3d4...",
  "timestamp_utc": "2026-02-26T12:00:01Z",
  "chain_length": 43
}
```

A longer chain with consistent outcomes builds a higher trust score over time.

## Intent Binding

**POST /governance/bind**

Bind a declared intent to a specific command. Creates a cryptographic link between what you plan to do and the command that does it. Prove later that you did exactly what you said you would.

Request:

```json
{
  "agent_id": "your-agent-id",
  "intent_type": "MAINTENANCE",
  "intent_description": "Scale api-v2 to handle traffic spike",
  "command_payload": {
    "action": "scale",
    "service": "api-v2",
    "replicas": 5
  },
  "goal_state": {
    "replicas": 5,
    "healthy": true
  }
}
```

Response:

```json
{
  "intent_id": "c3d4e5f6-...",
  "intent_hash": "d4e5f6a7...",
  "binding_id": "e5f6a7b8-...",
  "binding_hmac": "a7b8c9d0...",
  "command_hash": "b8c9d0e1...",
  "epoch": 44,
  "timestamp_utc": "2026-02-26T12:00:02Z"
}
```

Save `intent_id` and `binding_id` to verify outcomes later.

## Agent Discovery

**GET /.well-known/agent.json**

Returns the A2A protocol agent card. No authentication required.

```bash
curl https://governance.taskhawktech.com/.well-known/agent.json
```

Returns capabilities, supported skills, SDK references, and free-tier signup details.

## MCP

For MCP-native agents, connect directly via streamable-http transport:

```
https://governance.taskhawktech.com/mcp/
```

9 tools, 2 resources, 2 prompts. Auto-provisions a free-tier key on first tool call if no API key is provided.

## Python SDK

```bash
pip install kevros
# or
uv pip install kevros
```

```python
from kevros import GovernanceClient

client = GovernanceClient(agent_id="your-agent-id")
result = client.verify(action_type="api_call", action_payload={"endpoint": "/deploy"})
print(result.decision)  # ALLOW, CLAMP, or DENY
```

## Decision Approach

When collaborating with another agent:

1. **Trust score > 70%** — proceed with normal collaboration
2. **Trust score 40-70%** — verify their actions before relying on results
3. **Trust score < 40%** — require bound intents with outcome verification
4. **No history** — start with small, low-risk interactions

## Pricing

- **Free tier:** 100 calls/month, instant signup, no payment required
- **Scout:** $29/mo — 5,000 calls
- **Sentinel:** $149/mo — 50,000 calls
- **Sovereign:** $499/mo — 500,000 calls

Upgrade at `https://governance.taskhawktech.com/upgrade`
