# xCloud Docker Deployment — Constraints & Architecture

## Architecture

```
Internet → Cloudflare → xCloud Nginx (port 443, SSL) → Docker container (single exposed port)
```

xCloud manages:
- SSL/TLS termination (via Let's Encrypt or Cloudflare)
- Reverse proxy (nginx)
- Domain routing

Your Docker stack must NOT include: Caddy, Traefik, nginx-proxy, or any SSL-terminating proxy.

## xCloud Git Deployment Behavior

When you push to git, xCloud runs:
```bash
git pull
docker-compose pull   # pulls images from registry — does NOT build
docker-compose up -d
```

**Critical:** xCloud never runs `docker build`. Images must be pre-built and available in a public registry.

## docker-compose.yml Constraints

| Rule | Detail |
|------|--------|
| Single file only | No external `.conf`, `.env`, or override files at deploy time |
| Public images only | All `image:` must reference a public registry (`docker.io`, `ghcr.io`, etc.) |
| No `build:` directives | Will be silently ignored or fail |
| Single exposed port | One port proxied by xCloud's nginx |
| Env vars via UI | Set in xCloud dashboard, not in compose |
| Volume paths | Use relative paths; xCloud sets working directory to repo root |

## Deployment Steps in xCloud

1. Server → New Site → Custom Docker
2. Connect git repo (GitHub/GitLab/Bitbucket)
3. Paste `docker-compose.yml` or point to repo file
4. Set exposed port (the port xCloud proxies to)
5. Add env vars in xCloud UI
6. Deploy

## Supported Public Registries

- `ghcr.io` (GitHub Container Registry) — free for public repos
- `docker.io` / `hub.docker.com` — free for public images
- `registry.gitlab.com` — GitLab registry
- Any public registry URL

## Environment Variables

Never hardcode secrets in `docker-compose.yml`. Use `${VAR_NAME}` syntax — xCloud injects them via the UI. Always provide a `.env.example` listing all required variables.
