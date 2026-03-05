---
name: Caddy
description: Configure Caddy as a reverse proxy with automatic HTTPS and simple Caddyfile syntax.
metadata: {"clawdbot":{"emoji":"🔒","requires":{"bins":["caddy"]},"os":["linux","darwin","win32"]}}
---

# Caddy Configuration Rules

## Automatic HTTPS
- Caddy provisions SSL certificates automatically — don't manually configure Let's Encrypt unless you have specific needs
- Domain must resolve to the server publicly for HTTP challenge — use DNS challenge for internal/wildcard certs
- Ports 80 and 443 must be free — Caddy needs both even for HTTPS-only (80 handles ACME challenges and redirects)
- Let's Encrypt has rate limits — use staging CA during testing to avoid hitting production limits

## Caddyfile Syntax
- Indentation is significant — blocks are defined by indentation, not braces in shorthand
- Site blocks need a space before the opening brace: `example.com {` not `example.com{`
- Use `caddy fmt --overwrite` to fix formatting — catches most syntax issues
- Validate before applying: `caddy validate --config /etc/caddy/Caddyfile`

## Reverse Proxy
- Caddy adds `X-Forwarded-For`, `X-Forwarded-Proto`, `X-Forwarded-Host` automatically — don't add them manually
- WebSocket works out of the box — no special configuration needed
- Load balancing is automatic with multiple backends — default is random, use `lb_policy` to change
- Passive health checks remove failed backends automatically

## Docker Networking
- Use container names as hostnames: `reverse_proxy container_name:3000`
- Caddy and backends must share a Docker network — default bridge doesn't support DNS resolution
- For Docker Compose, service names work as hostnames when on the same network

## Configuration Management
- Use `caddy reload` not restart — reload applies changes without dropping connections
- Config changes are atomic — if new config fails validation, old config stays active
- Test without applying: `caddy adapt --config Caddyfile` shows parsed JSON output

## Certificate Storage
- Certificates stored in `~/.local/share/caddy` by default — preserve this across reinstalls
- For Docker, mount volumes for `/data` and `/config` — losing these means re-requesting all certificates
- Multiple Caddy instances need shared storage or will fight over certificates

## Debugging
- Enable debug logging: add `debug` as first line in global options block
- Check certificate status in `/data/caddy/certificates/` directory
- Common issue: DNS not pointing to server yet — certificates fail silently until domain resolves

## Security Headers
- Caddy doesn't add security headers by default — add X-Frame-Options, X-Content-Type-Options explicitly
- HSTS is automatic when serving HTTPS — no manual configuration needed

## Performance
- Handles thousands of concurrent connections without tuning
- HTTP/3 available with `servers { protocols h1 h2 h3 }`
- Compression automatic for text content
