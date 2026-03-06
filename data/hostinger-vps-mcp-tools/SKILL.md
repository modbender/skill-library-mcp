---
name: hostinger-vps-deploy
description: Set up Hostinger VPS servers as AI virtual employees with GUI and Koda (OpenClaw). Use when deploying new VPS instances, setting up remote desktops, installing Koda/OpenClaw, or configuring AI agent workstations. Handles Ubuntu server setup, GUI (XFCE + VNC/XRDP), Docker, and Koda deployment.
---

# Hostinger VPS Deploy

Deploy Koda (OpenClaw) on Hostinger VPS servers with GUI access for AI virtual employees.

## Overview

This skill automates:
1. **API-driven provisioning** — Deploy VPS instances via Hostinger API MCP tools
2. **Server hardening** — SSH keys, firewall, fail2ban
3. **GUI installation** — XFCE desktop + VNC/XRDP for remote access
4. **Docker setup** — Container runtime for Koda
5. **Koda deployment** — AI assistant with webchat interface
6. **Identity config** — Unique name/persona for each virtual employee

---

## Hostinger API Integration (MCP)

### Dashboard Tab

OpenClaw has a built-in **Hostinger** tab in the Control dashboard (Integrations group).

From the tab you can:
- Enter your **Hostinger API token** (stored securely in vault)
- Set your **GitHub repo URL** (OpenClaw fork to install on new VPS instances)
- View all available **MCP tools** grouped by category
- Reference the **Key VPS Tools** quick guide

### Getting Your API Token

1. Log into [hPanel](https://hpanel.hostinger.com)
2. Go to **API Tokens** → Create new token
3. Copy the token and paste it in the OpenClaw **Hostinger** tab

### MCP Server

The `hostinger-api-mcp` npm package is Hostinger's official MCP server.

- **Install**: `npm install -g hostinger-api-mcp` (already installed)
- **Auth**: Bearer token via `API_TOKEN` env var
- **Transport**: stdio (default) or HTTP streaming

**Important:** The API token is stored in `~/.openclaw/secrets.json` (the vault), **not** in plaintext in mcporter config. A `SecretRef` points to the vault key `HOSTINGER_API_TOKEN`.

### Key API Endpoints

| Tool | Method | Path |
|------|--------|------|
| `vps_getVirtualMachineListV1` | GET | `/api/vps/v1/virtual-machines` |
| `vps_createVirtualMachineV1` | POST | `/api/vps/v1/virtual-machines` |
| `vps_getDataCenterListV1` | GET | `/api/vps/v1/data-centers` |
| `vps_getOsListV1` | GET | `/api/vps/v1/os` |
| `vps_startVirtualMachineV1` | POST | `/api/vps/v1/virtual-machines/{id}/start` |
| `vps_stopVirtualMachineV1` | POST | `/api/vps/v1/virtual-machines/{id}/stop` |
| `vps_restartVirtualMachineV1` | POST | `/api/vps/v1/virtual-machines/{id}/restart` |
| `vps_resetPasswordV1` | POST | `/api/vps/v1/virtual-machines/{id}/reset-password` |
| `vps_getMetricsV1` | GET | `/api/vps/v1/virtual-machines/{id}/metrics` |
| `billing_getCatalogItemListV1` | GET | `/api/billing/v1/catalog` |
| `billing_getPaymentMethodListV1` | GET | `/api/billing/v1/payment-methods` |

### Using Tools via mcporter

```bash
# List all VPS instances
mcporter call hostinger-api.vps_getVirtualMachineListV1

# View available VPS plans (prices in cents)
mcporter call hostinger-api.billing_getCatalogItemListV1 category=VPS

# List data centers
mcporter call hostinger-api.vps_getDataCenterListV1

# List OS options
mcporter call hostinger-api.vps_getOsListV1

# Deploy a new VPS (requires plan item ID, OS ID, datacenter ID)
mcporter call hostinger-api.vps_createVirtualMachineV1 ...
```

### API Documentation Links

| Resource | URL |
|----------|-----|
| API Reference | https://developers.hostinger.com/ |
| Overview | https://developers.hostinger.com/#description/overview |
| Authentication | https://developers.hostinger.com/#description/authentication |
| SDKs & Tools | https://developers.hostinger.com/#description/sdks--tools |
| Official MCP Server (GitHub) | https://github.com/hostinger/api-mcp-server |
| Postman Collection | https://app.getpostman.com/run-collection/36145449-4a733c4f-6704-49f6-832a-0ccd28c37021 |
| hPanel API Tokens | https://hpanel.hostinger.com/api-tokens |

---

## VPS Deployment Workflow

### Step 1: Get a VPS

```bash
# 1. Check available plans
mcporter call hostinger-api.billing_getCatalogItemListV1 category=VPS

# 2. Pick a data center
mcporter call hostinger-api.vps_getDataCenterListV1

# 3. Pick an OS (Ubuntu 24.04 recommended)
mcporter call hostinger-api.vps_getOsListV1

# 4. Deploy
mcporter call hostinger-api.vps_createVirtualMachineV1 \
  --args '{"plan":"...", "datacenter_id": "...", "os_id": "..."}'
```

### Step 2: Set Up the Server

Once the VPS is running (get IP from `vps_getVirtualMachineListV1`):

```bash
# One-command full deploy
scripts/deploy-all.sh SERVER_IP "Agent Name" [KODA_PORT] [SSH_PORT]

# Examples:
scripts/deploy-all.sh 1.2.3.4 "Alex"
scripts/deploy-all.sh 1.2.3.4 "Alex" 9443 2222
```

### Step 3: Install OpenClaw Fork

If a GitHub repo is configured (via the Hostinger tab), Koda will:
1. SSH into the new VPS
2. Clone the configured repo (e.g., `https://github.com/your-org/openclaw`)
3. Run the install script

---

## Manual Step-by-Step Scripts

```bash
# 1. Initial server setup (with custom ports)
ssh root@SERVER_IP 'bash -s 9443 2222' < scripts/01-server-setup.sh

# 2. Install GUI + remote desktop
ssh -p 2222 root@SERVER_IP 'bash -s' < scripts/02-install-gui.sh

# 3. Install Docker
ssh -p 2222 root@SERVER_IP 'bash -s' < scripts/03-install-docker.sh

# 4. Deploy Koda (with custom port)
ssh -p 2222 root@SERVER_IP 'bash -s 9443' < scripts/04-deploy-koda.sh

# 5. Configure identity
ssh -p 2222 root@SERVER_IP 'bash -s' < scripts/05-configure-identity.sh "Agent Name"
```

## Scripts

| Script | Purpose |
|--------|---------|
| `01-server-setup.sh` | Updates, firewall, fail2ban, create user |
| `02-install-gui.sh` | XFCE desktop + XRDP (Windows Remote Desktop) |
| `03-install-docker.sh` | Docker + Docker Compose |
| `04-deploy-koda.sh` | Pull/build Koda, start container |
| `05-configure-identity.sh` | Set agent name, create workspace |
| `deploy-all.sh` | Run all scripts in sequence |

---

## Connecting to Your VPS

After deployment:

- **Remote Desktop (RDP)**: Connect with Windows Remote Desktop or Remmina to `SERVER_IP:3389`
- **VNC**: Connect to `SERVER_IP:5901` (if VNC installed)
- **Webchat**: Open `http://SERVER_IP:18789` in browser
- **SSH**: `ssh koda@SERVER_IP`

Default credentials (change after first login):
- Username: `koda`
- Password: Set during deployment

## Firewall Ports

| Port | Service | Customizable |
|------|---------|--------------|
| 22 (default) | SSH | ✅ Set via SSH_PORT |
| 3389 | XRDP (Remote Desktop) | ❌ |
| 18789 (default) | Koda webchat | ✅ Set via KODA_PORT |

---

## Security

### Vault Storage

The Hostinger API token is stored in **`~/.openclaw/secrets.json`** under the key `HOSTINGER_API_TOKEN`. It is **never stored in plaintext** in mcporter.json — only a `SecretRef` pointer is stored there.

### Post-Deployment Hardening

```bash
# Tailscale (zero-trust VPN — recommended)
ssh root@SERVER_IP 'bash -s' < scripts/security/setup-tailscale.sh
ssh root@SERVER_IP 'bash -s' < scripts/security/lockdown-public.sh

# Or: Cloudflare Tunnel for HTTPS
ssh root@SERVER_IP 'bash -s' < scripts/security/setup-cloudflare-tunnel.sh
```

| Script | Purpose |
|--------|---------|
| `security/setup-ssh-keys.sh` | SSH key-only auth |
| `security/setup-tailscale.sh` | Zero-trust VPN mesh |
| `security/setup-cloudflare-tunnel.sh` | HTTPS via Cloudflare |
| `security/setup-wireguard.sh` | Self-hosted VPN |
| `security/setup-https.sh` | Let's Encrypt SSL + Nginx |
| `security/harden-server.sh` | Kernel hardening, auto-updates |
| `security/lockdown-public.sh` | Remove all public port access |

---

## Reference Files

| File | Purpose |
|------|---------|
| `references/hostinger-backend.ts` | Gateway RPC handlers for Hostinger API |
| `references/hostinger-views.ts` | UI tab rendering (Lit) |
| `references/hostinger-controller.ts` | UI state management |
| `references/hostinger-notes.md` | hPanel navigation notes |
| `references/identity-setup.md` | Per-agent identity configuration |
| `references/security-options.md` | Security comparison guide |

---

## VPS Plans

Recommended for Koda/OpenClaw:
- **KVM 2** (2 GB RAM) — Minimum for headless Koda
- **KVM 4** (4 GB RAM) — Recommended for GUI + Koda
- **KVM 8** (8 GB RAM) — Comfortable for heavy workloads

OS: **Ubuntu 22.04 or 24.04 LTS**

---

## Troubleshooting

**Can't connect via RDP?**
- Ensure port 3389 is open: `sudo ufw status`
- Check XRDP status: `sudo systemctl status xrdp`

**Koda not starting?**
- Check Docker: `docker ps`
- View logs: `docker logs koda`

**GUI slow?**
- XFCE is lightweight but VPS needs 2GB+ RAM
- Consider headless mode if GUI not needed

**MCP tools not loading?**
- Verify token is saved: check `~/.openclaw/secrets.json` for `HOSTINGER_API_TOKEN`
- Run: `API_TOKEN=your-token mcporter list hostinger-api`
