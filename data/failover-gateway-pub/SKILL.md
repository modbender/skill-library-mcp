---
name: failover-gateway
version: 1.0.0
description: Set up an active-passive failover gateway for OpenClaw. Deploy a standby node that auto-promotes when your primary goes down and auto-demotes when it recovers. Includes health monitor script, systemd services, channel splitting strategy, and step-by-step deployment guide. Use when you need high availability, disaster recovery, or redundancy for your OpenClaw instance.
---

# Failover Gateway for OpenClaw

Deploy a standby OpenClaw gateway that automatically takes over when your primary goes down. Active-passive design with auto-promotion and auto-demotion.

## What You Get

- **~30 second failover** — health monitor detects primary down, promotes standby
- **Auto-recovery** — when primary comes back, standby demotes itself
- **Zero split-brain** — primary and standby use different channels (no duplicate messages)
- **Git-synced workspace** — standby pulls latest workspace on promotion
- **$12/month** — runs on a minimal VPS

## Architecture

```
PRIMARY (your main VPS)          STANDBY (failover VPS)
├─ Full stack (all channels)     ├─ Single channel only (e.g., Discord DM)
├─ All cron jobs                 ├─ No crons (recovery mode)
├─ Gateway active ✅              ├─ Gateway stopped 💤
└─ Pushes workspace to git       └─ Health monitor watches primary
                                      │
                                      ├─ Primary healthy → sleep
                                      ├─ Primary down 30s → PROMOTE
                                      └─ Primary back → DEMOTE
```

The key insight: **split your channels between primary and standby**. Don't share credentials — give each node exclusive ownership of different channels. This eliminates split-brain entirely.

### Channel Split Examples

| Setup | Primary | Standby |
|-------|---------|---------|
| RC + Discord | Rocket.Chat (full) | Discord DM only |
| Discord + Telegram | Discord (full) | Telegram DM only |
| Slack + Discord | Slack (full) | Discord DM only |

Your primary handles everything. The standby is minimal recovery — just enough to stay reachable.

## Prerequisites

- Primary OpenClaw instance running on a VPS
- A second VPS for the standby ($6-12/mo, any provider)
- [Tailscale](https://tailscale.com) mesh network (or any VPN/private network)
- Git repository for workspace sync (GitHub, GitLab, etc.)
- A second messaging channel for the standby (different from primary)

## Step-by-Step Deployment

### Phase 1: Provision the Standby VPS

Any cheap VPS works. Recommended: 2GB RAM, Ubuntu 24.04.

```bash
# Harden the box
ufw allow 22/tcp
ufw enable
apt install -y fail2ban unattended-upgrades

# Create openclaw user
adduser openclaw --disabled-password
usermod -aG sudo openclaw
# Copy your SSH key to openclaw user

# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up --hostname=your-failover-name
```

### Phase 2: Install OpenClaw

```bash
# As openclaw user
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc
nvm install --lts
npm install -g openclaw

# Clone workspace
git clone <your-workspace-repo> ~/.openclaw/workspace
```

### Phase 3: Failover Config

Create a **minimal** OpenClaw config on the standby. Only enable the standby channel:

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-opus-4-6",
        "fallbacks": ["anthropic/claude-sonnet-4-5"]
      },
      "workspace": "/home/openclaw/.openclaw/workspace"
    },
    "list": [{ "id": "main", "default": true }]
  },
  "channels": {
    "discord": {
      "enabled": true,
      "token": "<YOUR_DISCORD_BOT_TOKEN>",
      "dm": {
        "policy": "allowlist",
        "allowFrom": ["<YOUR_DISCORD_USER_ID>"]
      }
    }
  },
  "gateway": {
    "port": 18789,
    "mode": "local",
    "bind": "tailnet"
  }
}
```

**Important:** Disable this channel on your primary to avoid conflicts.

Test it works: `openclaw gateway run` — verify the bot connects and responds, then stop it.

### Phase 4: Deploy Health Monitor

Copy the included `scripts/health-monitor.sh` to the standby:

```bash
sudo cp health-monitor.sh /usr/local/bin/openclaw-health-monitor.sh
sudo chmod +x /usr/local/bin/openclaw-health-monitor.sh
```

Edit the variables at the top:
- `PRIMARY_IP` — your primary's Tailscale IP
- `PRIMARY_PORT` — your primary's gateway port (default: 18789)
- `SECRETS_HOST` — (optional) host to rsync secrets from on promotion

Create the systemd services:

**`/etc/systemd/system/openclaw-health-monitor.service`**
```ini
[Unit]
Description=OpenClaw Failover Health Monitor
After=network-online.target tailscaled.service
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/local/bin/openclaw-health-monitor.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**`/etc/systemd/system/openclaw.service`**
```ini
[Unit]
Description=OpenClaw Gateway (Failover)
After=network-online.target tailscaled.service
Wants=network-online.target

[Service]
Type=simple
User=openclaw
Group=openclaw
WorkingDirectory=/home/openclaw/.openclaw/workspace
ExecStart=/usr/bin/openclaw gateway run
Restart=on-failure
RestartSec=5
Environment=HOME=/home/openclaw
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

Enable the monitor (but NOT the gateway — the monitor starts it on promotion):

```bash
sudo systemctl daemon-reload
sudo systemctl enable openclaw-health-monitor
sudo systemctl start openclaw-health-monitor
# Do NOT enable openclaw.service — the monitor controls it
```

### Phase 5: Disable Standby Channel on Primary

This is critical. Remove or disable the standby's channel from your primary config:

```json
{
  "channels": {
    "discord": { "enabled": false }
  }
}
```

Each node owns its channels exclusively. No sharing, no conflicts.

### Phase 6: Test

```bash
# On primary — simulate failure
sudo systemctl stop openclaw-gateway  # or kill the process

# Watch the standby logs
journalctl -u openclaw-health-monitor -f

# Expected: 3 failed checks → PROMOTE → gateway starts → standby channel live

# On primary — recover
sudo systemctl start openclaw-gateway

# Expected: standby detects primary → DEMOTE → gateway stops
```

## Failover Timeline

| Time | Event |
|------|-------|
| 0s | Primary goes down |
| 10s | First health check fails |
| 20s | Second check fails |
| 30s | Third check fails → **PROMOTE** |
| 35s | Git pull, secrets sync |
| 40s | Gateway starting |
| 45s | Standby channel active |
| ~60s | **You're reachable again** |

## Edge Cases

| Scenario | Result |
|----------|--------|
| Primary dies | Standby promotes in ~30-60s |
| Primary + standby die | You're offline (add a third node?) |
| Network partition | Standby may promote while primary is still running — but since they use different channels, no conflicts |
| Standby reboots | Health monitor auto-restarts (systemd), resumes watching |
| Primary flaps | Promote/demote cycles — health monitor handles it, but consider increasing FAIL_THRESHOLD |

## Failback

Recovery is automatic. When the primary comes back:

1. Health monitor detects primary healthy
2. Stops the standby gateway
3. Primary resumes all channels
4. Standby returns to watching

No manual intervention needed.

## Cost

| Component | Cost |
|-----------|------|
| VPS (2GB RAM) | $6-12/mo |
| Tailscale | Free (personal) |
| Git repo | Free |
| **Total** | **$6-12/mo** |

## Tips

- **Test monthly.** Kill your primary, verify failover works. Trust but verify.
- **Keep the standby minimal.** No crons, no extra channels. It's recovery mode.
- **Git push frequently.** The standby's workspace is only as fresh as your last push.
- **Use Tailscale.** It makes cross-VPS networking trivial. No firewall rules, no port forwarding.
- **Different bot tokens.** If using Discord on both, you need two bot applications. Same bot token = last-connect-wins.
- **Monitor the monitor.** Check `journalctl -u openclaw-health-monitor` occasionally to make sure it's running.
