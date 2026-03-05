# bandwidth-income

Turn your unused internet bandwidth into passive crypto income. This skill helps you set up, monitor, and optimize bandwidth-sharing nodes across multiple networks.

## What It Does

- **Setup** Grass.io, Mysterium Network, Storj, and Honeygain nodes via Docker
- **Monitor** node uptime and auto-restart on failure
- **Track earnings** across all platforms in one dashboard
- **Alert** via message when a node goes offline or earnings drop
- **Calculate** ROI based on your bandwidth and hardware costs

## Supported Platforms

| Platform | Type | Earnings | Setup |
|----------|------|----------|-------|
| Grass.io | Bandwidth sharing | $100-1000/mo | Browser extension or Docker |
| Mysterium Network | VPN exit node | $10-200/mo | Docker, needs static IP |
| Storj | Decentralized storage | $5-100/mo | Docker, needs 500GB+ disk |
| Honeygain | Bandwidth sharing | $20-150/mo | App or Docker |

## Requirements

- Linux server or homelab (CT/VM works)
- Docker + docker-compose
- 1Mbps+ upload bandwidth
- Static or semi-static IP (Mysterium benefits most)
- For Storj: 500GB+ free disk space

## Commands

### `setup <platform>`
Sets up a bandwidth income node for the specified platform.

```
setup grass       — Install Grass.io desktop node
setup mysterium   — Deploy Mysterium Network exit node
setup storj       — Configure Storj storage node
setup honeygain   — Deploy Honeygain container
setup all         — Deploy all platforms
```

**Example:**
> "Set up a Mysterium node on CT 215"
> "Install Grass on my homelab server"

### `status`
Check current status of all running nodes.

```
status            — All nodes summary
status grass      — Grass.io node details
status mysterium  — Mysterium dashboard link + uptime
status storj      — Storj earnings + disk usage
```

### `earnings`
Estimate and track earnings across platforms.

```
earnings          — Current estimated monthly earnings
earnings history  — Past 30 days breakdown
earnings calc     — Calculator: enter bandwidth + disk → revenue estimate
```

### `monitor`
Set up automated monitoring with alerts.

```
monitor start     — Start monitoring all nodes (checks every 5 min)
monitor stop      — Stop monitoring
monitor logs      — View recent monitoring events
```

### `restart <platform>`
Restart a specific node.

```
restart grass
restart mysterium
restart all
```

## Quick Start (5 minutes)

### Option 1: Grass.io (Easiest, no static IP needed)

```bash
# Desktop node — run on any Linux with display, or headless via Xvfb
docker run -d \
  --name grass-node \
  --restart unless-stopped \
  -e GRASS_USER=your@email.com \
  -e GRASS_PASS=yourpassword \
  mrcolorrain/grass:latest

# Check status
docker logs grass-node --tail 20
```

**Requirements:** Grass.io account (free), residential IP preferred.

### Option 2: Mysterium Network (Best per-MB earnings)

```bash
# 1. Get a Mysterium wallet first: my.mystnodes.com
# 2. Deploy the node:
docker run -d \
  --name mysterium-node \
  --restart unless-stopped \
  --cap-add NET_ADMIN \
  -p 4449:4449 \
  -v ~/.mysterium:/root/.mysterium \
  mysteriumnetwork/myst:latest \
  service --agreed-terms-and-conditions

# 3. Claim your node:
# Visit: http://YOUR_SERVER_IP:4449
# Enter your wallet address from my.mystnodes.com
```

**Requirements:** Static/semi-static IP, port 4449 open, ERC-20 wallet.

### Option 3: Storj (If you have spare disk)

```bash
# 1. Create account at storj.io + generate auth token
# 2. Deploy:
docker run -d \
  --name storj-node \
  --restart unless-stopped \
  -p 28967:28967 \
  -p 14002:14002 \
  -e WALLET="0xYOUR_ETH_WALLET" \
  -e EMAIL="your@email.com" \
  -e ADDRESS="YOUR_PUBLIC_IP:28967" \
  -e STORAGE="500GB" \
  -v /path/to/storj/data:/app/identity \
  -v /path/to/storj/storage:/app/config \
  storjlabs/storagenode:latest
```

**Requirements:** 500GB free disk, port 28967 open, eth wallet.

## Docker Compose (All-in-one)

```yaml
version: "3.8"
services:
  grass:
    image: mrcolorrain/grass:latest
    container_name: grass-node
    restart: unless-stopped
    environment:
      - GRASS_USER=${GRASS_EMAIL}
      - GRASS_PASS=${GRASS_PASSWORD}
    
  mysterium:
    image: mysteriumnetwork/myst:latest
    container_name: mysterium-node
    restart: unless-stopped
    cap_add:
      - NET_ADMIN
    ports:
      - "4449:4449"
    volumes:
      - mysterium_data:/root/.mysterium
    command: service --agreed-terms-and-conditions

  honeygain:
    image: honeygain/honeygain:latest
    container_name: honeygain-node
    restart: unless-stopped
    environment:
      - HONEYGAIN_EMAIL=${HONEYGAIN_EMAIL}
      - HONEYGAIN_PASS=${HONEYGAIN_PASSWORD}
      - HONEYGAIN_DEVICE=homelab-01

volumes:
  mysterium_data:
```

## Earnings Calculator

| Platform | 100Mbps Upload | 50Mbps Upload | 10Mbps Upload |
|----------|----------------|---------------|---------------|
| Grass.io | $150-400/mo | $80-200/mo | $20-60/mo |
| Mysterium | $30-100/mo | $15-50/mo | $5-15/mo |
| Storj | $10-50/mo | $10-50/mo | $10-50/mo |
| Honeygain | $20-80/mo | $10-40/mo | $3-12/mo |
| **Total** | **$210-630/mo** | **$115-340/mo** | **$38-137/mo** |

*Estimates based on community reports as of Feb 2026. Actual earnings vary.*

## Monitoring Script

```bash
#!/bin/bash
# bandwidth-monitor.sh — check all nodes and alert on failure

check_container() {
  local name=$1
  local status=$(docker inspect --format='{{.State.Status}}' $name 2>/dev/null)
  if [ "$status" != "running" ]; then
    echo "ALERT: $name is $status — restarting..."
    docker start $name
    # openclaw message send "⚠️ $name node went down, restarted automatically"
    return 1
  fi
  echo "✅ $name: running"
}

check_container grass-node
check_container mysterium-node
check_container storj-node
check_container honeygain-node
```

## Notes

- **Residential IPs** earn more on Grass.io than datacenter/VPS IPs
- **Mysterium** requires you to stake MYST tokens to unlock higher earnings
- **Storj** earnings grow over time as your node builds reputation
- **Multiple nodes** on same IP may reduce per-node earnings on some platforms
- Always check platform ToS before running on VPS/cloud providers

## Privacy & Safety

- These platforms share your IP as an exit node or bandwidth relay
- Use a dedicated machine/container, not your primary workstation
- Mysterium traffic is encrypted end-to-end; you don't see user data
- Consider running on a separate VLAN if security is a concern
