# Custom Domains with Cloudflare Tunnels

Route each OpenClaw agent to its own subdomain on a domain you own.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Add Domain to Cloudflare](#add-domain-to-cloudflare)
3. [Authenticate cloudflared](#authenticate-cloudflared)
4. [Create a Named Tunnel](#create-a-named-tunnel)
5. [Point a Subdomain at the Tunnel](#point-a-subdomain-at-the-tunnel)
6. [Multi-Agent Subdomain Layout](#multi-agent-subdomain-layout)
7. [Automatic HTTPS](#automatic-https)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- A domain name (any registrar — you'll point nameservers to Cloudflare)
- A free Cloudflare account at dash.cloudflare.com
- `cloudflared` installed on the VPS
- OpenClaw agents running on known local ports

---

## Add Domain to Cloudflare

1. Log in to [dash.cloudflare.com](https://dash.cloudflare.com)
2. Click **Add a site** → enter your domain → select **Free plan**
3. Cloudflare scans your existing DNS records — review and confirm
4. Copy the two Cloudflare nameservers shown (e.g. `carter.ns.cloudflare.com`)
5. Go to your domain registrar → update nameservers to the Cloudflare ones
6. Wait 5–30 min for propagation

Verify:
```bash
dig NS yourdomain.com +short
# Should return Cloudflare nameservers
```

---

## Authenticate cloudflared

Run once on the VPS. Opens a browser auth flow — if headless, copy the URL to your local browser.

```bash
cloudflared login
# Prints a URL — open it, pick your domain, authorize
# Saves cert.pem to /root/.cloudflared/cert.pem
```

---

## Create a Named Tunnel

```bash
# Create (produces a UUID + credentials file)
cloudflared tunnel create openclaw-koda

# List to confirm
cloudflared tunnel list
# NAME             ID                                   CREATED
# openclaw-koda    a1b2c3d4-...                         2026-03-03
```

Credentials are saved at `/root/.cloudflared/<UUID>.json`. Keep this — it's how the tunnel authenticates.

---

## Point a Subdomain at the Tunnel

### Option A: Using cloudflared CLI (auto-creates CNAME)

```bash
cloudflared tunnel route dns openclaw-koda koda.yourdomain.com
```

This creates a CNAME record:
```
koda.yourdomain.com  →  <UUID>.cfargotunnel.com  (proxied)
```

### Option B: Manually in Cloudflare dashboard

1. Go to **DNS → Records → Add record**
2. Type: **CNAME**
3. Name: `koda`
4. Target: `<UUID>.cfargotunnel.com`
5. Proxy status: **Proxied** (orange cloud ON)
6. Save

---

## Multi-Agent Subdomain Layout

One domain, multiple subdomains — each pointing to its own tunnel:

```
yourdomain.com
├── koda.yourdomain.com    → openclaw-koda tunnel  → localhost:18789
├── alex.yourdomain.com    → openclaw-alex tunnel  → localhost:18790
├── jordan.yourdomain.com  → openclaw-jordan tunnel → localhost:18791
└── (wildcard optional)    → *.yourdomain.com
```

### Config file per agent

`/etc/cloudflared/openclaw-koda.yml`:
```yaml
tunnel: a1b2c3d4-xxxx-xxxx-xxxx-xxxxxxxxxxxx
credentials-file: /root/.cloudflared/a1b2c3d4-xxxx-xxxx-xxxx-xxxxxxxxxxxx.json

ingress:
  - hostname: koda.yourdomain.com
    service: http://localhost:18789
  - service: http_status:404
```

`/etc/cloudflared/openclaw-alex.yml`:
```yaml
tunnel: b2c3d4e5-xxxx-xxxx-xxxx-xxxxxxxxxxxx
credentials-file: /root/.cloudflared/b2c3d4e5-xxxx-xxxx-xxxx-xxxxxxxxxxxx.json

ingress:
  - hostname: alex.yourdomain.com
    service: http://localhost:18790
  - service: http_status:404
```

### Systemd service per agent

`/etc/systemd/system/cloudflared-koda.service`:
```ini
[Unit]
Description=Cloudflare Tunnel — koda
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/cloudflared tunnel --no-autoupdate --config /etc/cloudflared/openclaw-koda.yml run
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start all tunnel services
systemctl daemon-reload
systemctl enable cloudflared-koda cloudflared-alex cloudflared-jordan
systemctl start  cloudflared-koda cloudflared-alex cloudflared-jordan
```

**Important:** Do NOT use `cloudflared service install` — it only supports one tunnel and will conflict with manually managed services.

---

## Automatic HTTPS

No cert management required. Cloudflare handles HTTPS termination at their edge:

- Your VPS serves HTTP on localhost — no TLS setup needed on the server
- Cloudflare issues and renews the certificate for `koda.yourdomain.com` automatically
- All traffic is encrypted between the user and Cloudflare's edge
- Traffic between Cloudflare and your VPS travels through the tunnel (encrypted)

**OpenClaw `allowedOrigins` must include the HTTPS URL** (not just HTTP):

```json
"gateway": {
  "controlUi": {
    "allowedOrigins": [
      "http://localhost:18789",
      "https://koda.yourdomain.com"
    ]
  }
}
```

---

## Troubleshooting

**Tunnel connects but UI shows origin/CORS error:**
- Add `https://koda.yourdomain.com` to `allowedOrigins` in openclaw.json and restart

**`cloudflared tunnel route dns` fails:**
- Ensure domain is in Cloudflare (not just registered — nameservers must point to Cloudflare)
- Ensure `cert.pem` exists: `ls /root/.cloudflared/cert.pem`
- Add the CNAME record manually in the dashboard instead

**Tunnel starts but immediately exits:**
- Check credentials file exists: `ls /root/.cloudflared/<UUID>.json`
- Check config YAML syntax: `cloudflared tunnel --config /etc/cloudflared/openclaw-koda.yml ingress validate`

**Multiple tunnel services conflicting:**
- Never run `cloudflared service install` after the first tunnel — it overwrites the system service
- Each extra agent needs a manually written systemd service file (as shown above)

**Free Cloudflare plan limits:**
- Unlimited tunnels ✅
- Unlimited bandwidth ✅
- No WAF on free plan (available on Pro+)
- Custom domains require a domain you own — `trycloudflare.com` quick tunnels are free with no account
