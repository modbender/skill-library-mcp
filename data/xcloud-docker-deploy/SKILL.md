---
name: xcloud-docker-deploy
description: "Adapt any docker-compose.yml to deploy on xCloud. Handles 4 common blockers: (1) build-from-source apps — generates GitHub Actions to build/push to GHCR; (2) proxy conflicts (Caddy/Traefik/nginx-proxy) — removes them, adds nginx-router with single port; (3) multi-port apps — routes all services through nginx-router; (4) external config files — embeds inline. Use when a user wants to deploy any Docker app on xCloud and has an incompatible docker-compose.yml, or asks make this work on xCloud."
license: Apache-2.0
metadata:
  version: 1.0.0
  author: Asif2BD
  homepage: https://github.com/Asif2BD/xCloud-Docker-Deploy-Skill
  source: https://github.com/Asif2BD/xCloud-Docker-Deploy-Skill
  tags: docker, xcloud, deployment, devops, docker-compose
  platforms: openClaw, claude-code, claude-ai, cursor, windsurf, any
  security_verified: true
  no_network_calls: true
  no_executables: true
---

# xCloud Docker Deploy

Adapt any `docker-compose.yml` to work with [xCloud](https://xcloud.host) — a git-push Docker deployment platform.

## How xCloud Works

```
git push → xCloud runs: docker-compose pull && docker-compose up -d
```

**xCloud never runs `docker build`.** Images must be pre-built in a public registry. SSL, reverse proxy, and domain routing are handled by xCloud — your stack must not duplicate them.

Read `references/xcloud-constraints.md` for the full ruleset before making changes.

---

## Step 1 — Detect Which Scenarios Apply

Inspect the provided `docker-compose.yml`:

| Signal | Scenario |
|--------|----------|
| `build:` or `build: context: .` | **A** — Build-from-source |
| Caddy / Traefik / nginx-proxy service | **B** — Proxy conflict |
| Multiple `ports:` across services | **B** — Multi-port |
| `./nginx.conf:/etc/nginx/...` volume mount | **B** — External config |
| Multiple services each with `build:` | **C** — Multi-service build |
| `image: some-public-image`, single port | Already compatible — verify port + env vars |

A compose file can trigger **multiple scenarios** simultaneously (handle A first, then B).

---

## Scenario A — Build-from-Source

> Read `references/scenario-build-source.md` for full details.

**What to do:**
1. Remove `build:` directive from compose
2. Replace `image:` with `ghcr.io/OWNER/REPO:latest`
3. Generate `.github/workflows/docker-build.yml` using `assets/github-actions-build.yml` template
4. Generate `.env.example` from all `${VAR}` references

**Deliverables:**
- Modified `docker-compose.yml`
- `.github/workflows/docker-build.yml`
- `.env.example`
- xCloud Deploy Steps (see Output Format)

---

## Scenario B — Proxy Conflict / Multi-Port / External Config

> Read `references/scenario-proxy-conflict.md` for full details.

**What to do:**
1. Remove Caddy/Traefik/nginx-proxy service entirely
2. Remove SSL labels and multi-port `ports:` from app services (replace with `expose:`)
3. Add `nginx-router` service with inline config via `configs:` block
4. Expose single port (default: `3080`) for xCloud to proxy

**Deliverables:**
- Modified `docker-compose.yml` with `nginx-router` + `configs:` block
- `.env.example`
- xCloud Deploy Steps

---

## Scenario C — Multi-Service Build

> Read `references/scenario-multi-service-build.md` for full details.

When multiple services have `build:` directives (separate frontend + backend + worker):

**What to do:**
1. For each service with `build:`, create a separate GHCR image path
2. Generate a matrix GitHub Actions workflow that builds all images in parallel
3. Update compose to use all GHCR image references

**Deliverables:**
- Modified `docker-compose.yml` (all `build:` removed)
- `.github/workflows/docker-build.yml` (matrix strategy)
- `.env.example`

---

## Output Format

Always produce complete, copy-paste-ready output:

```
## Modified docker-compose.yml
[full file]

## .github/workflows/docker-build.yml  (Scenario A/C only)
[full file]

## .env.example
[full file]

## xCloud Deploy Steps
1. Push repo to GitHub
2. (Scenario A/C) Wait for GitHub Actions to build image — check Actions tab
3. Server → New Site → Custom Docker → connect repo
4. Exposed port: [PORT]
5. Env vars to add: [list from .env.example]
6. Deploy
```

---

## Rules

- **Never** include `build:` in the final compose — xCloud silently ignores it
- **Never** expose database ports to host (remove `"5432:5432"` — use `expose:` internally)
- **Never** include Caddy, Traefik, nginx-proxy, or Let's Encrypt config
- **Always** preserve `environment:`, `volumes:`, `healthcheck:`, worker/sidecar services
- **Always** use `expose:` (internal) not `ports:` (host) for services behind nginx-router
- **WebSockets?** Add upgrade headers to nginx config (see proxy-conflict reference)
- `configs.content:` inline syntax requires Docker Compose v2.23+ — use heredoc `command:` alternative if uncertain

---

## Examples

See `examples/` for ready-made transformations:
- `examples/rybbit-analytics.md` — Caddy + multi-port app (Scenario B)
- `examples/custom-app-dockerfile.md` — build-from-source (Scenario A)
- `examples/fullstack-monorepo.md` — multi-service build (Scenario C)
