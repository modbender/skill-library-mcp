---
name: nginx-proxy-manager
description: Manage Nginx Proxy Manager (NPM) for reverse proxy and SSL termination to internal services like staging/prod apps. Use when creating/updating proxy hosts, requesting or renewing Let's Encrypt certificates, enforcing HTTPS redirects, setting websocket support, or routing domains/subdomains to target servers.
---

# Nginx Proxy Manager Workflow

Use this skill to terminate SSL at NPM and route traffic to backend services (staging/prod).

## Required inputs

- Domain/subdomain (e.g. `staging.example.com`)
- Public DNS already pointing to NPM public IP
- Upstream target host/IP + port (e.g. `10.10.10.227:3000`)
- Whether Cloudflare proxy is enabled (if used)

## Authentication (do not hardcode secrets)

Store credentials outside this skill (local secret file or environment variables).

Recommended env vars:
- `NPM_BASE_URL` (e.g. `http://<npm-host>:81`)
- `NPM_IDENTITY`
- `NPM_SECRET`

Example token request:

```bash
curl -sS -X POST "$NPM_BASE_URL/api/tokens" \
  -H 'Content-Type: application/json; charset=UTF-8' \
  --data "{\"identity\":\"$NPM_IDENTITY\",\"secret\":\"$NPM_SECRET\"}"
```

## Standard setup flow

1. Confirm DNS resolves to NPM public IP.
2. Create or update Proxy Host in NPM:
   - Domain Names: requested host(s)
   - Scheme: `http` (or `https` if upstream is TLS)
   - Forward Hostname/IP: upstream IP/hostname
   - Forward Port: app port
   - Enable:
     - Block Common Exploits
     - Websockets Support
3. SSL tab:
   - Request new SSL certificate (Let's Encrypt)
   - Enable `Force SSL`
   - Enable `HTTP/2 Support`
   - Enable `HSTS` only after validation
4. Save and verify:
   - `curl -I https://<domain>` returns `200/301`
   - Browser check for valid certificate and app reachability

## Recommended defaults

- Keep upstream as private IP where possible.
- Use separate hostnames per environment:
  - `app.example.com` → production
  - `staging.example.com` → staging
- Avoid wildcard certificates unless explicitly needed.

## Troubleshooting

- Certificate issuance fails:
  - Check DNS A/AAAA records
  - Ensure ports 80/443 reach NPM
  - Disable conflicting CDN TLS mode or set to Full/Strict appropriately
- 502 Bad Gateway:
  - Verify upstream container/service is running
  - Verify correct target port and local firewall rules
- Redirect loops:
  - Don’t double-force HTTPS (app + proxy misconfiguration)

## Publication hygiene checklist

Before sharing/publishing this skill:
- Remove all real IPs, domains, emails, and tokens.
- Keep only placeholders like `example.com` and `<npm-host>`.
- Ensure no local credential file paths or secret values are included.

## Safety rules

- Never remove existing production proxy hosts unless explicitly requested.
- For changes on production domains, snapshot/export config or document previous values first.
- Apply changes to staging first when possible.
