---
name: hookaido
description: Operate Hookaido inbound/outbound webhook flows, queue triage, MCP workflows, and gRPC-pull workers. Use when tasks involve Hookaidofile authoring, `hookaido` CLI commands (`run`, `config fmt`, `config validate`, `mcp serve`), pull operations (`dequeue`/`ack`/`nack`/`extend`) over HTTP or gRPC, Admin API backlog/DLQ handling, or production hardening for webhook/webhooks ingress and delivery.
metadata: {"openclaw":{"homepage":"https://github.com/nuetzliches/hookaido","requires":{"bins":["hookaido"]},"install":[{"id":"download-darwin-amd64","kind":"download","os":["darwin"],"url":"https://github.com/nuetzliches/hookaido/releases/download/v1.5.0/hookaido_v1.5.0_darwin_amd64.tar.gz","archive":"tar.gz","extract":true,"stripComponents":1,"targetDir":"~/.local/bin","bins":["hookaido"],"label":"Download hookaido v1.5.0 (macOS amd64)"},{"id":"download-darwin-arm64","kind":"download","os":["darwin"],"url":"https://github.com/nuetzliches/hookaido/releases/download/v1.5.0/hookaido_v1.5.0_darwin_arm64.tar.gz","archive":"tar.gz","extract":true,"stripComponents":1,"targetDir":"~/.local/bin","bins":["hookaido"],"label":"Download hookaido v1.5.0 (macOS arm64)"},{"id":"download-linux-amd64","kind":"download","os":["linux"],"url":"https://github.com/nuetzliches/hookaido/releases/download/v1.5.0/hookaido_v1.5.0_linux_amd64.tar.gz","archive":"tar.gz","extract":true,"stripComponents":1,"targetDir":"~/.local/bin","bins":["hookaido"],"label":"Download hookaido v1.5.0 (Linux amd64)"},{"id":"download-linux-arm64","kind":"download","os":["linux"],"url":"https://github.com/nuetzliches/hookaido/releases/download/v1.5.0/hookaido_v1.5.0_linux_arm64.tar.gz","archive":"tar.gz","extract":true,"stripComponents":1,"targetDir":"~/.local/bin","bins":["hookaido"],"label":"Download hookaido v1.5.0 (Linux arm64)"},{"id":"download-windows-amd64","kind":"download","os":["win32"],"url":"https://github.com/nuetzliches/hookaido/releases/download/v1.5.0/hookaido_v1.5.0_windows_amd64.zip","archive":"zip","extract":true,"targetDir":"~/.openclaw/tools/hookaido","bins":["hookaido"],"label":"Download hookaido v1.5.0 (Windows amd64)"},{"id":"download-windows-arm64","kind":"download","os":["win32"],"url":"https://github.com/nuetzliches/hookaido/releases/download/v1.5.0/hookaido_v1.5.0_windows_arm64.zip","archive":"zip","extract":true,"targetDir":"~/.openclaw/tools/hookaido","bins":["hookaido"],"label":"Download hookaido v1.5.0 (Windows arm64)"}]}}
---

# Hookaido

## Overview

Implement and troubleshoot Hookaido with a config-first workflow: edit `Hookaidofile`, validate, run, exercise ingress/pull flows, then diagnose queue health and DLQ behavior.
Use conservative, reversible changes and validate before runtime operations.

## Workflow

1. Confirm target topology: inbound+pull (HTTP or gRPC), push outbound, or internal queue.
2. Choose runtime mode and ensure `hookaido` exists where tools execute.
   - Host-binary mode: use the install action from `metadata.openclaw.install`.
   - Host fallback: run `bash {baseDir}/scripts/install_hookaido.sh` (pinned `v1.5.0`, SHA256-verified).
   - Docker-sandbox mode: use a sandbox image that already includes `hookaido` (preferred), or install inside sandbox via `agents.defaults.sandbox.docker.setupCommand`.
   - Keep host install actions available as fallback and to satisfy `metadata.openclaw.requires.bins`.
3. Inspect and update `Hookaidofile` minimally.
4. Run format and validation before starting or reloading:
   - `hookaido config fmt --config ./Hookaidofile`
   - `hookaido config validate --config ./Hookaidofile`
5. Start runtime and verify health:
   - `hookaido run --config ./Hookaidofile --db ./.data/hookaido.db`
   - `curl http://127.0.0.1:2019/healthz?details=1`
6. Validate end-to-end behavior:
   - ingress request accepted and queued
   - consumer `dequeue`/`ack`/`nack`/`extend` path works (HTTP pull, plus gRPC pull when enabled)
7. For incidents, inspect backlog and DLQ first, then mutate.

## Task Playbooks

### Configure Ingress and Pull Consumption

1. Define a route with explicit auth and pull path (HTTP pull, optional gRPC pull worker listener).
2. Keep secrets in env/file refs, never inline.
3. Verify route and global pull auth are consistent.
4. Test with a real webhook payload and a dequeue/ack cycle.

Prefer this baseline:

```hcl
ingress {
  listen :8080
}

pull_api {
  listen :9443
  grpc_listen :9943 # optional gRPC pull-worker listener
  auth token env:HOOKAIDO_PULL_TOKEN
}

/webhooks/github {
  auth hmac env:HOOKAIDO_INGRESS_SECRET
  pull { path /pull/github }
}
```

### Configure Push Delivery

1. Use push delivery only when inbound connectivity to the service is acceptable.
2. Set timeout and retry policy explicitly.
3. Validate downstream idempotency since delivery is at-least-once.

```hcl
/webhooks/stripe {
  auth hmac env:STRIPE_SIGNING_SECRET
  deliver "https://billing.internal/stripe" {
    retry exponential max 8 base 2s cap 2m jitter 0.2
    timeout 10s
  }
}
```

### Operate Queue and DLQ

1. Start with health details and backlog endpoints.
2. Inspect DLQ before requeue or delete.
3. If requeueing many items, explain expected impact and rollback path.
4. Require clear operator reason strings for mutating admin calls.

Use:

- `GET /healthz?details=1`
- `GET /backlog/trends`
- `GET /dlq`
- `POST /dlq/requeue`
- `POST /dlq/delete`

### Use MCP Mode for AI Operations

1. Default to `--role read` for diagnostics.
2. Enable mutations only with explicit operator intent:
   - `--enable-mutations --role operate --principal <identity>`
3. Enable runtime control only for admin workflows:
   - `--enable-runtime-control --role admin --pid-file <path>`
4. Include `reason` for mutation calls and keep it specific.

## Validation Checklist

- `hookaido config validate` returns success before runtime start/reload.
- Health endpoint is reachable and reports expected queue/backend state.
- Pull consumer can `dequeue`, `ack`, `nack`, and `extend` with valid token (HTTP and optional gRPC transport).
- For push mode, retry/timeout behavior is explicitly configured.
- Any DLQ mutation is scoped, justified, and logged.

## Safety Rules

- Do not disable auth to "make tests pass."
- Do not suggest direct mutations before read-only diagnostics.
- Treat queue operations as at-least-once; require idempotent handlers.
- Keep secrets in `env:` or `file:` refs.

## References

- Read `references/operations.md` for command snippets and API payload templates.
