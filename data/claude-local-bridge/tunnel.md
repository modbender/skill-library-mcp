# Tunnel Setup Guide

Access your Claude Local Bridge from anywhere — phone, tablet, or another machine.

---

## Option 1: Tailscale (Recommended for personal use)

**What:** Encrypted WireGuard mesh VPN. Your phone and PC join the same private network.
**Cost:** Free for up to 100 devices.
**FOSS:** Client is BSD-3 licensed. For fully FOSS, use [Headscale](https://github.com/juanfont/headscale) as the control server.

### Setup

1. Install Tailscale on your PC: https://tailscale.com/download
2. Install Tailscale on your phone (iOS/Android)
3. Sign in with the same account on both
4. Start the bridge binding to all interfaces:
   ```bash
   python -m app.main --roots /your/projects --host 0.0.0.0
   ```
5. From your phone browser, go to: `http://<your-pc-tailscale-ip>:9120`
   - Find the IP: run `tailscale ip -4` on your PC

### With Headscale (fully FOSS)

If you want zero proprietary components, self-host [Headscale](https://github.com/juanfont/headscale) on a VPS and point your Tailscale clients at it.

---

## Option 2: Cloudflare Tunnel (Best for sharing with others)

**What:** Gives you a public HTTPS URL that routes to your localhost.
**Cost:** Free tier. No credit card needed.
**FOSS:** `cloudflared` client is Apache 2.0.

### Quick start (no account needed)

```bash
# Install cloudflared
# Windows: winget install cloudflare.cloudflared
# Mac: brew install cloudflared
# Linux: See https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/

# Start a quick tunnel (gives you a random URL)
cloudflared tunnel --url http://localhost:9120
```

This prints a URL like `https://random-words.trycloudflare.com` — open it on your phone.

### Persistent named tunnel (with account)

```bash
cloudflared tunnel login
cloudflared tunnel create bridge
cloudflared tunnel route dns bridge bridge.yourdomain.com
cloudflared tunnel run --url http://localhost:9120 bridge
```

---

## Option 3: NetBird (Fully FOSS alternative)

**What:** Open-source WireGuard mesh VPN, similar to Tailscale.
**Cost:** Free self-hosted. Managed free tier also available.
**FOSS:** BSD-3-Clause. Entire stack is open source.

### Setup

1. Install: https://netbird.io/install
2. Sign up / self-host the management server
3. Connect both devices: `netbird up`
4. Start bridge with `--host 0.0.0.0` and access via NetBird IP

---

## Option 4: FRP (Fast Reverse Proxy)

**What:** Self-hosted reverse proxy tunneling. Requires a VPS.
**Cost:** Free (you need a VPS though, ~$3-5/month).
**FOSS:** Apache 2.0.
**Repo:** https://github.com/fatedier/frp

### Setup

On your VPS (frps.ini):
```ini
[common]
bind_port = 7000
vhost_http_port = 80
```

On your PC (frpc.ini):
```ini
[common]
server_addr = your-vps-ip
server_port = 7000

[bridge]
type = http
local_port = 9120
custom_domains = bridge.yourdomain.com
```

---

## Security Notes

- **Always use the bearer token** — anyone with the URL can browse your files without it
- **Approval gating** prevents file reads/writes without your explicit OK
- **For public tunnels:** consider adding IP allowlists or basic auth in front
- **Tailscale/NetBird** are inherently private — only your devices see the traffic
- **Cloudflare Tunnel** is publicly accessible — protect with Cloudflare Access (free) for extra security
