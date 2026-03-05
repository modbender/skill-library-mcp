---
name: openclaw-agent-compute
description: "Public HTTP client skill exposing compute.* tools by calling a private Compute Gateway over HTTPS. Includes a starter kit to run OpenClaw preconfigured."
---

# openclaw-agent-compute

Public, agent-friendly skill that exposes `compute.*` tools by calling a **private** Compute Gateway over **HTTPS**.

## Environment

- `MCP_COMPUTE_URL` (e.g. `https://compute.example.com`)
- `MCP_COMPUTE_API_KEY`

Copy `skills/openclaw-agent-compute/.env.example`.

## Tools / API expectation

This client expects the private gateway to implement:
- `POST /v1/sessions` (create)
- `POST /v1/exec` (run command)
- `GET /v1/usage/{session_id}` (usage/cost)
- `DELETE /v1/sessions/{session_id}` (destroy)

## Scripts

- HTTP client: `skills/openclaw-agent-compute/scripts/client.js`
- Example: `skills/openclaw-agent-compute/scripts/example_exec.js`

### Local smoke test

```bash
cp skills/openclaw-agent-compute/.env.example .env
# edit .env
npm i
npm run example:exec
```

## Starter kit

See `skills/openclaw-agent-compute/starter-kit/`.

It keeps the OpenClaw image overrideable via `OPENCLAW_IMAGE` until an official image/tag is confirmed.
