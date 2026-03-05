# Hookaido Operations Reference

Use this file for concrete command syntax and request payloads.

## Install Hookaido

OpenClaw supports two runtime variants.

### Variant A: Host Binary (Gateway/Host)

- Use one of the skill installer actions from `metadata.openclaw.install` (platform + architecture specific download).
- Choose the artifact that matches your host architecture (`amd64` or `arm64`).
- The OpenClaw download URLs are pinned to Hookaido `v1.5.0`.
- macOS/Linux installers extract to `~/.local/bin` (with `stripComponents: 1`).
- Windows installers extract to `~/.openclaw/tools/hookaido`.

Direct CLI fallback:

```bash
go install github.com/nuetzliches/hookaido/cmd/hookaido@v1.5.0
```

Release-binary fallback from this skill folder:

```bash
bash {baseDir}/scripts/install_hookaido.sh
```

The fallback installer is hardened:

- Defaults to pinned `v1.5.0` (no dynamic `latest` lookup).
- Verifies SHA256 of the downloaded release artifact before extraction/install.

Optional pins/overrides for the installer script:

```bash
# Default pinned install, custom location
HOOKAIDO_INSTALL_DIR="$HOME/bin" bash {baseDir}/scripts/install_hookaido.sh

# Non-default release requires explicit checksum
HOOKAIDO_VERSION=v1.4.1 \
HOOKAIDO_SHA256="<artifact-sha256>" \
bash {baseDir}/scripts/install_hookaido.sh
```

### Variant B: Docker Sandbox

- OpenClaw supports Docker sandbox mode via `sandboxing.enabled: true` and `sandboxing.type: docker`.
- Preferred: provide a custom sandbox image with `hookaido` preinstalled, and pin the image by immutable digest.
- Optional: use `agents.defaults.sandbox.docker.setupCommand` to install `hookaido` inside the container at startup.
- Keep `metadata.openclaw.install` as fallback and for `metadata.openclaw.requires.bins` checks on the host.

## Core CLI Commands

```bash
# Validate and format config
hookaido config fmt --config ./Hookaidofile
hookaido config validate --config ./Hookaidofile

# Start runtime
hookaido run --config ./Hookaidofile --db ./.data/hookaido.db

# Start runtime with live config watch
hookaido run --config ./Hookaidofile --db ./.data/hookaido.db --watch

# Start MCP server (read-only)
hookaido mcp serve --config ./Hookaidofile --db ./.data/hookaido.db --role read
```

## Minimal Pull-Mode Config

```hcl
ingress {
  listen :8080
}

pull_api {
  listen :9443
  auth token env:HOOKAIDO_PULL_TOKEN
}

/webhooks/github {
  auth hmac env:HOOKAIDO_INGRESS_SECRET
  pull { path /pull/github }
}
```

## Pull API Calls

Assume base URL `http://localhost:9443/pull/github` and token in `HOOKAIDO_PULL_TOKEN`.

```bash
# Dequeue
curl -sS -X POST "http://localhost:9443/pull/github/dequeue" \
  -H "Authorization: Bearer $HOOKAIDO_PULL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"batch":10,"lease_ttl":"30s","max_wait":"5s"}'

# Ack
curl -sS -X POST "http://localhost:9443/pull/github/ack" \
  -H "Authorization: Bearer $HOOKAIDO_PULL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"lease_id":"lease_xyz"}'

# Nack (requeue with delay)
curl -sS -X POST "http://localhost:9443/pull/github/nack" \
  -H "Authorization: Bearer $HOOKAIDO_PULL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"lease_id":"lease_xyz","delay":"5s","dead":false}'

# Extend lease
curl -sS -X POST "http://localhost:9443/pull/github/extend" \
  -H "Authorization: Bearer $HOOKAIDO_PULL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"lease_id":"lease_xyz","lease_ttl":"30s"}'
```

## Optional gRPC Pull-Worker Mode (`v1.4.0+`)

Enable gRPC pull-worker transport alongside HTTP pull:

```hcl
pull_api {
  listen :9443
  grpc_listen :9943
  auth token env:HOOKAIDO_PULL_TOKEN
}

/webhooks/github {
  pull { path /pull/github }
}
```

Use gRPC workers with the same lease semantics and operation parity as Pull HTTP:

- `Dequeue` -> `POST {endpoint}/dequeue`
- `Ack` -> `POST {endpoint}/ack`
- `Nack` -> `POST {endpoint}/nack`
- `Extend` -> `POST {endpoint}/extend`

Notes:

- Worker gRPC reuses pull token auth and pull endpoint routing.
- Keep `grpc_listen` on a dedicated internal listener; do not share ingress/pull/admin/metrics ports.
- Worker lease operations are intentionally outside MCP scope.

## Admin API Reads

```bash
# Health summary
curl -sS "http://127.0.0.1:2019/healthz"

# Detailed diagnostics
curl -sS "http://127.0.0.1:2019/healthz?details=1"

# Backlog trends
curl -sS "http://127.0.0.1:2019/backlog/trends?window=1h&step=5m"

# Dead-letter queue
curl -sS "http://127.0.0.1:2019/dlq?limit=50"
```

## Admin API Mutations

Use `X-Hookaido-Audit-Reason` and keep reasons actionable.

```bash
# Requeue DLQ items
curl -sS -X POST "http://127.0.0.1:2019/dlq/requeue" \
  -H "Content-Type: application/json" \
  -H "X-Hookaido-Audit-Reason: retry-after-fix" \
  -d '{"ids":["evt_1","evt_2"]}'

# Delete DLQ items
curl -sS -X POST "http://127.0.0.1:2019/dlq/delete" \
  -H "Content-Type: application/json" \
  -H "X-Hookaido-Audit-Reason: remove-invalid-payloads" \
  -d '{"ids":["evt_3"]}'
```

## MCP Role Patterns

```bash
# Read-only diagnostics
hookaido mcp serve --config ./Hookaidofile --db ./.data/hookaido.db --role read

# Queue mutation workflows
hookaido mcp serve --config ./Hookaidofile --db ./.data/hookaido.db \
  --enable-mutations --role operate --principal ops@example.test

# Full admin control (includes runtime operations)
hookaido mcp serve --config ./Hookaidofile --db ./.data/hookaido.db \
  --enable-mutations --enable-runtime-control --role admin \
  --principal ops@example.test --pid-file ./hookaido.pid
```
