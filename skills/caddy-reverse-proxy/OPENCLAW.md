# OpenClaw Gateway Integration

How to proxy the OpenClaw gateway (and apps that connect to it) through Caddy.

## Add Gateway to Caddyfile

```caddy
openclaw.YOUR_DOMAIN {
    import vercel_tls
    reverse_proxy localhost:18789
}
```

## Gateway Config

The gateway needs specific config in `~/.openclaw/openclaw.json` to work behind Caddy:

```json
"gateway": {
    "trustedProxies": ["127.0.0.1", "::1", "YOUR_TAILSCALE_IP"],
    "controlUi": {
        "allowInsecureAuth": true,
        "allowedOrigins": [
            "https://openclaw.YOUR_DOMAIN",
            "https://myapp.YOUR_DOMAIN"
        ]
    }
}
```

Add each app's `https://SUBDOMAIN.YOUR_DOMAIN` origin as needed.

### Why each setting matters

**`trustedProxies`** — Caddy connects to the gateway from loopback (`::1` / `127.0.0.1`). Without this, the gateway logs `Proxy headers detected from untrusted address` and ignores `X-Forwarded-For`/`X-Forwarded-Proto` headers, treating all connections as non-local. Include `YOUR_TAILSCALE_IP` (Tailscale IP) for any direct Tailscale connections.

**`allowInsecureAuth: true`** — The gateway normally requires device-key authentication (public key signature) for control UI clients. Server-side WebSocket proxies don't support device auth. This setting allows token-only authentication. Without it, the gateway rejects with the misleading error `control ui requires HTTPS or localhost (secure context)`.

**`allowedOrigins`** — The gateway checks the `Origin` header on WebSocket upgrades for control UI and webchat clients. Any UI served from a different subdomain than the gateway itself needs its origin listed here. Without it: `origin not allowed`.

## Adding an App That Connects to the Gateway

If a Caddy-proxied app connects to the OpenClaw gateway (e.g., a web UI, dashboard, or chat client):

**a) Add its origin to allowedOrigins** in `~/.openclaw/openclaw.json`:
```json
"gateway": {
    "controlUi": {
        "allowedOrigins": [
            "https://APPNAME.YOUR_DOMAIN"
        ]
    }
}
```

**b) If the app needs device pairing**, run:
```bash
openclaw devices list       # see pending requests
openclaw devices approve <request-id>
```

**c) Restart the gateway** to pick up config changes:
```bash
# macOS
launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway
# Linux
systemctl --user restart openclaw-gateway
# Or:
openclaw gateway restart
```

## Troubleshooting

**"Proxy headers detected from untrusted address":**
Add the proxy's source address to `gateway.trustedProxies` in openclaw.json. For Caddy on the same machine: `["127.0.0.1", "::1", "YOUR_TAILSCALE_IP"]`.

**"control ui requires HTTPS or localhost (secure context)":**
Device auth is required but the client doesn't support it. Set `gateway.controlUi.allowInsecureAuth: true` in openclaw.json.

**"origin not allowed":**
Add the app's origin to `gateway.controlUi.allowedOrigins` in openclaw.json.

**"pairing required":**
The device needs to be approved:
```bash
openclaw devices list
openclaw devices approve <request-id>
```
