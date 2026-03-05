---
name: gatewaystack-governance
description: Deny-by-default governance for every tool call — identity, scope, rate limiting, injection detection, audit logging, plus opt-in output DLP, escalation, and behavioral monitoring. Hooks into OpenClaw at the process level so the agent can't bypass it.
user-invocable: true
metadata: { "openclaw": { "emoji": "🛡️", "requires": { "bins": ["node"] }, "homepage": "https://github.com/davidcrowe/openclaw-gatewaystack-governance" } }
---

# GatewayStack Governance

Deny-by-default governance for every tool call in OpenClaw.

Five core checks run automatically on every invocation:

1. **Identity** — maps the agent to a policy role. Unknown agents are denied.
2. **Scope** — deny-by-default tool allowlist. Unlisted tools are blocked.
3. **Rate limiting** — per-user and per-session sliding window limits.
4. **Injection detection** — 40+ patterns from Cisco, Snyk, and Kaspersky research.
5. **Audit logging** — every decision recorded to append-only JSONL.

Three opt-in features extend governance further:

6. **Output DLP** — scans tool output for PII using `@gatewaystack/transformabl-core`. Log or redact.
7. **Escalation** — human-in-the-loop review for medium-severity detections and first-time tool use.
8. **Behavioral monitoring** — detects anomalous tool usage patterns using `@gatewaystack/limitabl-core`.

## Install

```bash
openclaw plugins install @gatewaystack/gatewaystack-governance
```

One command. Zero config. The core 5 checks are active on every tool call immediately.

The plugin hooks into `before_tool_call` at the process level — the agent can't bypass it, skip it, or talk its way around it.

## Customize

To override the defaults, create a policy file:

```bash
cp ~/.openclaw/plugins/gatewaystack-governance/policy.example.json \
   ~/.openclaw/plugins/gatewaystack-governance/policy.json
```

Configure which tools are allowed, who can use them, rate limits, injection detection sensitivity, and the three optional features (DLP, escalation, behavioral monitoring — all disabled by default).

## Optional GatewayStack packages

The opt-in features use GatewayStack packages via lazy import. Install only what you need:

```bash
npm install @gatewaystack/transformabl-core   # for output DLP
npm install @gatewaystack/limitabl-core       # for behavioral monitoring
```

The core 5 checks have zero external dependencies and work without these packages.

## Links

- [GitHub](https://github.com/davidcrowe/openclaw-gatewaystack-governance) — source, docs, getting started guide
- [npm](https://www.npmjs.com/package/@gatewaystack/gatewaystack-governance) — package registry
- MIT licensed
