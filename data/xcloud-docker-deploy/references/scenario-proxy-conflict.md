# Scenario: Proxy/SSL Conflict & Multi-Port Apps

## Detection

This scenario applies when `docker-compose.yml` contains any of:
- A Caddy, Traefik, nginx-proxy, or similar reverse-proxy service
- Multiple exposed ports (e.g., `3001` for API, `3002` for frontend)
- External config files referenced via volume mounts (e.g., `./nginx.conf:/etc/nginx/nginx.conf`)
- SSL/TLS config (certresolver, Let's Encrypt, ACME)

**Real example — Rybbit Analytics:**
```yaml
services:
  caddy:           # ← conflicts with xCloud's nginx
    image: caddy
    ports: ["80:80", "443:443"]
  clickhouse: ...
  backend:
    ports: ["3001:3001"]   # ← multiple ports
  frontend:
    ports: ["3002:3002"]   # ← multiple ports
```

## Solution Overview

1. Remove the proxy/SSL service (Caddy/Traefik/nginx-proxy)
2. Remove SSL-related labels and config
3. Add a lightweight `nginx-router` service that routes internal traffic
4. Embed the nginx config inline using the `configs:` block (no external files)
5. Expose a single port (e.g., `3080`) for xCloud to proxy to

## Architecture After Fix

```
xCloud Nginx (443) → nginx-router:3080 → backend:3001 (API)
                                        → frontend:3002 (UI)
```

## Step 1 — Remove Proxy Service

Delete the entire Caddy/Traefik/nginx-proxy service block.
Remove any `labels:` containing `traefik.*` or Caddy directives from other services.
Remove port mappings `"80:80"` and `"443:443"`.

## Step 2 — Remove External Port Mappings from App Services

Backend and frontend services should NOT expose ports directly to the host.
Remove their `ports:` sections — they communicate internally via Docker network.

```yaml
# BEFORE
backend:
  ports:
    - "3001:3001"

# AFTER
backend:
  expose:
    - "3001"    # internal only — accessible within Docker network
```

## Step 3 — Add nginx-router Service with Embedded Config

Use the `configs:` top-level block to embed nginx config inline:

```yaml
services:
  nginx-router:
    image: nginx:alpine
    ports:
      - "3080:80"     # ← single port xCloud proxies to
    configs:
      - source: nginx_config
        target: /etc/nginx/conf.d/default.conf
    depends_on:
      - backend
      - frontend
    networks:
      - app-network

configs:
  nginx_config:
    content: |
      server {
        listen 80;

        location /api/ {
          proxy_pass http://backend:3001/;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
        }

        location / {
          proxy_pass http://frontend:3002/;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
        }
      }
```

**Note:** The `configs:` inline `content:` feature requires Docker Compose v2.23+ / Docker Engine 25+. For older versions, use a heredoc in a startup command instead (see below).

## Alternative: Inline Config via Command

If `configs.content` is not supported:

```yaml
nginx-router:
  image: nginx:alpine
  ports:
    - "3080:80"
  command: >
    sh -c "echo 'server {
      listen 80;
      location /api/ { proxy_pass http://backend:3001/; }
      location / { proxy_pass http://frontend:3002/; }
    }' > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"
```

## Step 4 — Ensure Shared Network

All services must be on the same Docker network for internal routing:

```yaml
services:
  nginx-router:
    networks: [app-network]
  backend:
    networks: [app-network]
  frontend:
    networks: [app-network]

networks:
  app-network:
    driver: bridge
```

## Step 5 — xCloud Configuration

- **Exposed port:** `3080` (or whatever single port you chose)
- **No SSL config needed** — xCloud handles it
- All env vars added via xCloud UI

## Common Routing Patterns

| App type | Route pattern |
|----------|--------------|
| API + SPA | `/api/* → backend`, `/* → frontend` |
| API + SSR | `/api/* → api-service`, `/* → web-service` |
| Multiple APIs | `/api/v1/* → service-a`, `/api/v2/* → service-b` |
| WebSocket | Add `proxy_http_version 1.1; proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection "upgrade";` |
