---
name: cloudflare-agent-tunnel
description: >
  Give each OpenClaw agent its own secure HTTPS URL using Cloudflare Tunnel (cloudflared). No SSL
  certificates to manage, no ports to expose publicly. Use when setting up secure cloud access for
  OpenClaw agents on a VPS, assigning per-agent subdomains (koda.yourdomain.com), enabling HTTPS
  without nginx or Let's Encrypt, or connecting a custom domain to an agent. Covers quick tunnels
  (no account, instant URL), named tunnels (permanent URL, free Cloudflare account), multi-agent
  setup on a single VPS, and custom domain configuration.
---

# Cloudflare Agent Tunnel

Give each OpenClaw agent a permanent, secure HTTPS URL via Cloudflare Tunnel — no SSL certs, no nginx, no open ports.

## How It Works

```
User → https://koda.yourdomain.com
         ↓ (Cloudflare edge — TLS termination here)
       Cloudflare Tunnel (encrypted)
         ↓
       cloudflared process on VPS
         ↓
       http://localhost:18789  (OpenClaw gateway)
```

- Cloudflare handles TLS — no cert management on the server
- The local port never needs to be open to the internet
- Each agent gets its own `cloudflared` process + systemd service

---

## Option 1 — Quick Tunnel (No Account, Instant)

For testing or temporary access. URL is random and resets on restart.

```bash
# Install cloudflared
curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null
echo "deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared any main" \
  | tee /etc/apt/sources.list.d/cloudflared.list
apt-get update -qq && apt-get install -y cloudflared

# Start quick tunnel — prints a random https://*.trycloudflare.com URL
cloudflared tunnel --url http://localhost:18789 --no-autoupdate
```

Use the automated script:
```bash
./scripts/tunnel-setup.sh --agent koda --port 18789 --quick
```

---

## Option 2 — Named Tunnel (Permanent, Free Cloudflare Account)

Permanent URL. Requires a free Cloudflare account and a domain.

### Step 1: Authenticate

```bash
cloudflared login
# Opens a browser URL — authorize your domain
# Saves /root/.cloudflared/cert.pem
```

### Step 2: Create tunnel

```bash
cloudflared tunnel create openclaw-koda
# Outputs UUID — save it
```

### Step 3: Write config

`/etc/cloudflared/openclaw-koda.yml`:
```yaml
tunnel: <UUID>
credentials-file: /root/.cloudflared/<UUID>.json

ingress:
  - hostname: koda.yourdomain.com
    service: http://localhost:18789
  - service: http_status:404
```

### Step 4: Route DNS

```bash
cloudflared tunnel route dns openclaw-koda koda.yourdomain.com
# Creates CNAME: koda.yourdomain.com → <UUID>.cfargotunnel.com
```

### Step 5: Install as systemd service

```bash
cat > /etc/systemd/system/cloudflared-koda.service << 'EOF'
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
EOF

systemctl daemon-reload
systemctl enable cloudflared-koda
systemctl start cloudflared-koda
```

Or use the automated script:
```bash
./scripts/tunnel-setup.sh --agent koda --port 18789 --domain koda.yourdomain.com
```

---

## Multi-Agent Setup (One VPS, Multiple Agents)

Each agent = one OpenClaw gateway + one Cloudflare tunnel, both as separate systemd services.

```
Port 18789 → openclaw-koda.service   + cloudflared-koda.service   → koda.yourdomain.com
Port 18790 → openclaw-alex.service   + cloudflared-alex.service   → alex.yourdomain.com
Port 18791 → openclaw-jordan.service + cloudflared-jordan.service → jordan.yourdomain.com
```

**Critical:** Do NOT use `cloudflared service install` for multiple agents — it only supports one tunnel and overwrites the system service. Always write systemd service files manually (as above) for each agent.

```bash
# Add each agent sequentially
./scripts/tunnel-setup.sh --agent alex   --port 18790 --domain alex.yourdomain.com
./scripts/tunnel-setup.sh --agent jordan --port 18791 --domain jordan.yourdomain.com
```

---

## Update OpenClaw allowedOrigins

After setting up a tunnel, add the HTTPS URL to the agent's openclaw.json — otherwise the UI blocks the connection:

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

Then restart the agent: `systemctl restart openclaw-koda`

---

## Custom Domains

Full walkthrough for adding a domain, Cloudflare nameservers, per-agent subdomains, and DNS record management: see `references/custom-domains.md`.

Key facts:
- Domain must use **Cloudflare nameservers** (transfer DNS to Cloudflare — free)
- Cloudflare issues and renews TLS certs automatically
- CNAME records created automatically via `cloudflared tunnel route dns`
- Free Cloudflare plan supports unlimited tunnels and unlimited bandwidth

---

## Managing Tunnels

```bash
# Status of all tunnels
systemctl list-units "cloudflared-*" --no-pager

# Logs
journalctl -u cloudflared-koda -f

# List all named tunnels (requires cloudflared login)
cloudflared tunnel list

# Delete a tunnel
cloudflared tunnel delete openclaw-koda
systemctl disable cloudflared-koda && rm /etc/systemd/system/cloudflared-koda.service
```
