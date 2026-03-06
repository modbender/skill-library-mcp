---
name: afrexai-self-hosting-mastery
description: Complete self-hosting and homelab operating system. Deploy, secure, monitor, and maintain self-hosted services with production-grade reliability. Use when setting up home servers, Docker infrastructure, reverse proxies, backups, monitoring, or evaluating self-hosted alternatives to SaaS.
---

# Self-Hosting Mastery

Complete system for building and operating reliable self-hosted infrastructure — from first server to multi-node homelab.

## Phase 1: Infrastructure Assessment

### Server Profile YAML

```yaml
server_profile:
  name: ""
  hardware:
    cpu: ""              # e.g., "Intel i5-12400" or "Raspberry Pi 5"
    ram_gb: 0
    storage:
      - device: ""       # e.g., "/dev/sda"
        type: ""         # ssd | hdd | nvme
        size_gb: 0
        role: ""         # boot | data | backup
    network: ""          # 1gbe | 2.5gbe | 10gbe
  os: ""                 # debian | ubuntu | proxmox | unraid | truenas
  location: ""           # home | closet | rack | colo | vps
  power:
    ups: false
    wattage_idle: 0
    wattage_load: 0
    monthly_cost_estimate: ""  # electricity
  network:
    public_ip: ""        # static | dynamic | cgnat
    domain: ""
    dns_provider: ""     # cloudflare | duckdns | custom
    isp_ports_open: true # some ISPs block 80/443
  goals:
    - ""                 # media server, smart home, dev environment, etc.
  budget_monthly: ""     # electricity + domain + any VPS
```

### Hardware Decision Matrix

| Budget | RAM | Storage | Good For | Example Hardware |
|--------|-----|---------|----------|-----------------|
| $0 | 4-8GB | 64GB+ | Pi-hole, AdGuard, small tools | Raspberry Pi 4/5 |
| $50-150 | 8-16GB | 256GB+ | Docker host, 5-10 services | Used SFF PC (Dell Optiplex, Lenovo Tiny) |
| $150-400 | 16-32GB | 1TB+ | NAS + services, media server | Mini PC (Intel NUC, Beelink) |
| $400-800 | 32-64GB | 4TB+ | Full homelab, VMs + containers | Used enterprise (Dell R720, HP DL380) |
| $800+ | 64GB+ | 10TB+ | Multi-node, Proxmox cluster | Multiple nodes, dedicated NAS |

### Self-Host vs SaaS Decision

Ask before self-hosting anything:
1. **Data sensitivity** — Does keeping data local matter? (passwords, health, finance = yes)
2. **Reliability need** — Can you tolerate occasional downtime? (email = risky, media = fine)
3. **Maintenance budget** — Do you have 2-4 hours/month for updates?
4. **Skill level** — Can you debug Docker/networking issues?
5. **Cost comparison** — Is the SaaS < $10/mo? Often not worth self-hosting for trivial savings.

**Always self-host**: Password manager, DNS/ad-blocking, VPN, bookmarks, notes
**Usually self-host**: Media server, file sync, photo backup, monitoring, git
**Think twice**: Email (deliverability hell), calendar (sync complexity), chat (uptime expectations)
**Rarely worth it**: Search engine (resource hungry), social media (no network effect)

---

## Phase 2: OS & Virtualization

### OS Selection Guide

| OS | Best For | Learning Curve | Notes |
|----|----------|---------------|-------|
| Debian 12 | Docker-only host | Low | Stable, minimal, just works |
| Ubuntu Server 24.04 | Beginners, wide docs | Low | More packages, snap controversy |
| Proxmox VE | VMs + containers | Medium | Free, enterprise features, ZFS |
| Unraid | NAS + Docker + VMs | Medium | $59-129, great UI, parity array |
| TrueNAS Scale | ZFS NAS + Docker | Medium | Free, ZFS-first, apps improving |
| NixOS | Reproducible configs | High | Declarative, steep learning curve |

### Proxmox Quick Setup

```bash
# Post-install essentials
# 1. Remove enterprise repo (if no subscription)
sed -i 's/^deb/#deb/' /etc/apt/sources.list.d/pve-enterprise.list
echo "deb http://download.proxmox.com/debian/pve bookworm pve-no-subscription" > /etc/apt/sources.list.d/pve-no-subscription.list
apt update && apt upgrade -y

# 2. Create a Docker LXC (lightweight container)
# Download template: Datacenter → Storage → CT Templates → Download → debian-12
# Create CT: 2 cores, 2GB RAM, 32GB disk, bridge vmbr0
# Inside CT: install Docker
apt install -y curl
curl -fsSL https://get.docker.com | sh

# 3. Enable IOMMU for GPU passthrough (if needed)
# Edit /etc/default/grub: GRUB_CMDLINE_LINUX_DEFAULT="quiet intel_iommu=on"
# update-grub && reboot
```

### VM vs LXC vs Docker Decision

| Factor | VM | LXC | Docker |
|--------|----|-----|--------|
| Isolation | Full (own kernel) | Partial (shared kernel) | Process-level |
| Overhead | High (1-2GB base) | Low (50-200MB) | Minimal |
| Use when | Different OS, GPU passthrough, untrusted workloads | Dedicated service host, ZFS datasets | Most services |
| Avoid when | RAM-constrained | Need Windows, custom kernel | Stateful databases (use LXC/VM) |

**Rule**: Docker for 90% of services. LXC for Docker hosts or isolated environments. VM for Windows, different kernel needs, or GPU passthrough.

---

## Phase 3: Docker Infrastructure

### Docker Compose Project Structure

```
/opt/stacks/           # or ~/docker/
├── traefik/
│   ├── docker-compose.yml
│   ├── .env
│   ├── config/
│   │   └── traefik.yml
│   └── data/
│       ├── acme.json          # chmod 600
│       └── dynamic/
├── monitoring/
│   ├── docker-compose.yml
│   ├── .env
│   └── config/
├── media/
│   ├── docker-compose.yml
│   ├── .env
│   └── config/
├── productivity/
│   ├── docker-compose.yml
│   ├── .env
│   └── config/
└── scripts/
    ├── backup.sh
    ├── update-all.sh
    └── health-check.sh
```

### Docker Compose Best Practices

```yaml
# Template: production-grade service
services:
  app:
    image: vendor/app:1.2.3           # ALWAYS pin version
    container_name: app               # Explicit name
    restart: unless-stopped           # Auto-restart
    networks:
      - proxy                         # Traefik network
      - internal                      # Backend network
    volumes:
      - ./config:/config              # Bind mount for config
      - app-data:/data                # Named volume for data
    environment:
      - TZ=Europe/London              # Always set timezone
      - PUID=1000                     # Match host user
      - PGID=1000
    env_file:
      - .env                          # Secrets in .env (gitignored)
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.app.rule=Host(`app.example.com`)"
      - "traefik.http.routers.app.tls.certresolver=letsencrypt"
      - "traefik.http.services.app.loadbalancer.server.port=8080"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          memory: 512M               # Prevent OOM cascades
    security_opt:
      - no-new-privileges:true        # Security hardening
    read_only: true                   # Where possible
    tmpfs:
      - /tmp

volumes:
  app-data:

networks:
  proxy:
    external: true
  internal:
```

### Docker Security Checklist

- [ ] Pin all image versions (never `:latest` in production)
- [ ] Set `restart: unless-stopped` on all services
- [ ] Use `.env` files for secrets (never hardcode in compose)
- [ ] Set memory limits on all containers
- [ ] Use `security_opt: no-new-privileges:true`
- [ ] Use `read_only: true` where possible + tmpfs for /tmp
- [ ] Create separate Docker networks per stack
- [ ] Never expose database ports to 0.0.0.0
- [ ] Run containers as non-root (PUID/PGID or `user:`)
- [ ] Enable Docker content trust: `export DOCKER_CONTENT_TRUST=1`
- [ ] Prune unused images/volumes monthly: `docker system prune -af`
- [ ] Use named volumes (not anonymous) for all persistent data
- [ ] Set `TZ` environment variable on every container

---

## Phase 4: Reverse Proxy & SSL

### Reverse Proxy Selection

| Proxy | Best For | SSL | Config Style | Learning Curve |
|-------|----------|-----|-------------|---------------|
| Traefik | Docker-native, auto-discovery | Auto (ACME) | Labels + YAML | Medium |
| Caddy | Simplicity, auto-SSL | Auto (built-in) | Caddyfile | Low |
| Nginx Proxy Manager | GUI preference | Auto (UI) | Web UI | Very Low |
| Nginx (manual) | Maximum control | Manual/certbot | Config files | High |

**Recommendation**: Traefik for Docker power users. Caddy for simplicity. NPM for beginners.

### Traefik Production Config

```yaml
# traefik/config/traefik.yml
api:
  dashboard: true
  insecure: false

entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
  websecure:
    address: ":443"
    http:
      tls:
        certResolver: letsencrypt

certificatesResolvers:
  letsencrypt:
    acme:
      email: you@example.com
      storage: /data/acme.json
      # Use DNS challenge if ISP blocks port 80
      # dnsChallenge:
      #   provider: cloudflare
      httpChallenge:
        entryPoint: web

providers:
  docker:
    exposedByDefault: false    # Explicit opt-in per service
    network: proxy
  file:
    directory: /data/dynamic
    watch: true

log:
  level: WARN

accessLog:
  filePath: /data/access.log
  bufferingSize: 100
```

### Cloudflare Tunnel (Zero Port Forwarding)

For CGNAT or ISPs blocking ports — expose services without opening firewall:

```yaml
# cloudflared/docker-compose.yml
services:
  cloudflared:
    image: cloudflare/cloudflared:2024.1.0
    container_name: cloudflared
    restart: unless-stopped
    command: tunnel run
    environment:
      - TUNNEL_TOKEN=${CF_TUNNEL_TOKEN}
    networks:
      - proxy
```

**When to use Cloudflare Tunnel vs port forwarding**:
- CGNAT (no public IP) → Tunnel (only option)
- ISP blocks 80/443 → Tunnel or DNS challenge + non-standard ports
- Security-first → Tunnel (no open ports)
- Performance-first → Direct (lower latency)
- LAN-only access → Neither (use Tailscale/WireGuard)

---

## Phase 5: Essential Services Stack

### Tier 1 — Deploy First (Foundation)

| Service | Purpose | Image | RAM | Notes |
|---------|---------|-------|-----|-------|
| Traefik/Caddy | Reverse proxy + SSL | traefik:v3.0 | 64MB | Gateway to everything |
| Pi-hole/AdGuard | DNS + ad blocking | pihole/pihole | 128MB | Network-wide ad blocking |
| Authelia/Authentik | SSO + 2FA | authelia/authelia | 128MB | Protect services without built-in auth |
| Uptime Kuma | Monitoring | louislam/uptime-kuma | 128MB | Know when things break |
| Watchtower | Auto-updates | containrrr/watchtower | 32MB | Optional — some prefer manual |

### Tier 2 — Core Services

| Service | Purpose | Alt | RAM |
|---------|---------|-----|-----|
| Vaultwarden | Password manager | Bitwarden | 64MB |
| Nextcloud | File sync + office | Seafile (lighter) | 512MB |
| Immich | Photo backup | PhotoPrism | 1-4GB |
| Jellyfin | Media server | Plex (less free) | 512MB-2GB |
| Paperless-ngx | Document management | - | 256MB |
| Home Assistant | Smart home | - | 512MB |

### Tier 3 — Power User

| Service | Purpose | RAM |
|---------|---------|-----|
| Gitea/Forgejo | Git hosting | 256MB |
| n8n | Workflow automation | 256MB |
| Grafana + Prometheus | Metrics & dashboards | 512MB |
| Tandoor | Recipe management | 256MB |
| Mealie | Meal planning | 128MB |
| Linkwarden/Hoarder | Bookmark manager | 256MB |
| Stirling PDF | PDF tools | 512MB |
| IT-Tools | Developer utilities | 64MB |

### RAM Planning

```
Total RAM needed ≈ OS base (1-2GB) + sum of service RAM + 20% headroom
Example 16GB server:
  OS + Docker:     2 GB
  Traefik:         0.1 GB
  Pi-hole:         0.1 GB
  Authelia:        0.1 GB
  Uptime Kuma:     0.1 GB
  Vaultwarden:     0.1 GB
  Nextcloud:       0.5 GB
  Immich:          2.0 GB
  Jellyfin:        1.0 GB
  Paperless:       0.3 GB
  Home Assistant:  0.5 GB
  ──────────────────────
  Total:           6.8 GB → 8.2 GB with headroom
  Available:       ~7.8 GB free for more services
```

---

## Phase 6: Networking & DNS

### DNS Architecture

```
Internet → Cloudflare DNS → Your Public IP → Router → Server
                                                        ↓
                                             Reverse Proxy (Traefik)
                                                        ↓
                                     ┌──────────────────┼──────────────────┐
                                     ↓                  ↓                  ↓
                                app.domain.com   files.domain.com   media.domain.com
```

### Split DNS (Access Services Locally Without Hairpin NAT)

```
# Pi-hole/AdGuard: Local DNS rewrites
# Point *.home.example.com → 192.168.1.100 (server LAN IP)
# External: Cloudflare points to public IP
# Result: LAN traffic stays local, external goes through internet
```

### VPN for Remote Access

| Solution | Type | Best For | Complexity |
|----------|------|----------|-----------|
| Tailscale | Mesh VPN | Easiest setup, multi-device | Very Low |
| WireGuard | Point-to-point | Performance, full control | Medium |
| Headscale | Self-hosted Tailscale | Privacy, no vendor lock | Medium-High |

**Recommendation**: Start with Tailscale (free for 3 users). Move to Headscale when you want full control.

### Firewall Rules (UFW)

```bash
# Default deny incoming
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (change port from 22!)
ufw allow 2222/tcp comment 'SSH'

# Allow HTTP/HTTPS for reverse proxy
ufw allow 80/tcp comment 'HTTP redirect'
ufw allow 443/tcp comment 'HTTPS'

# Allow local network for discovery
ufw allow from 192.168.1.0/24 comment 'LAN'

# Enable
ufw enable
```

---

## Phase 7: Backup Strategy

### 3-2-1 Rule Implementation

```
3 copies:  Live data + Local backup + Remote backup
2 media:   SSD/HDD (server) + External drive or NAS
1 offsite: Cloud (Backblaze B2, Wasabi) or second location
```

### Backup Script Template

```bash
#!/bin/bash
# /opt/stacks/scripts/backup.sh
set -euo pipefail

BACKUP_DIR="/mnt/backup/docker"
STACKS_DIR="/opt/stacks"
DATE=$(date +%Y-%m-%d_%H%M)
RETENTION_DAYS=30

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"; }

# 1. Stop services that need consistent backups
log "Stopping database services..."
cd "$STACKS_DIR/productivity" && docker compose stop db

# 2. Backup Docker volumes
log "Backing up volumes..."
for vol in $(docker volume ls -q); do
    docker run --rm \
        -v "$vol":/source:ro \
        -v "$BACKUP_DIR/volumes":/backup \
        alpine tar czf "/backup/${vol}_${DATE}.tar.gz" -C /source .
done

# 3. Backup compose files and configs
log "Backing up configs..."
tar czf "$BACKUP_DIR/configs/stacks_${DATE}.tar.gz" \
    --exclude='*.log' \
    --exclude='node_modules' \
    "$STACKS_DIR"

# 4. Restart services
log "Restarting services..."
cd "$STACKS_DIR/productivity" && docker compose start db

# 5. Cleanup old backups
log "Cleaning up backups older than ${RETENTION_DAYS} days..."
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

# 6. Sync to remote (Backblaze B2 example)
# rclone sync "$BACKUP_DIR" b2:my-backups/docker/ --transfers 4

# 7. Verify
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
log "Backup complete. Total size: $BACKUP_SIZE"

# 8. Send notification (optional)
# curl -s "https://ntfy.sh/my-backups" -d "Backup complete: $BACKUP_SIZE"
```

### Backup Schedule

| What | Frequency | Retention | Method |
|------|-----------|-----------|--------|
| Docker volumes | Daily 3 AM | 30 days | Script + cron |
| Compose files + configs | Daily 3 AM | 90 days | Script + cron |
| Database dumps | Every 6 hours | 7 days | pg_dump/mysqldump |
| Full disk image | Monthly | 3 months | Clonezilla/dd |
| Offsite sync | Daily 5 AM | 60 days | rclone to B2/Wasabi |

### Backup Verification (Monthly)

- [ ] Pick a random backup from last week
- [ ] Restore to a test VM/container
- [ ] Verify data integrity (check file counts, DB row counts)
- [ ] Time the restore process (document RTO)
- [ ] Log results in backup-verification.md

---

## Phase 8: Monitoring & Alerting

### Monitoring Stack (Docker Compose)

```yaml
# monitoring/docker-compose.yml
services:
  uptime-kuma:
    image: louislam/uptime-kuma:1
    container_name: uptime-kuma
    restart: unless-stopped
    volumes:
      - uptime-data:/app/data
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.uptime.rule=Host(`status.example.com`)"

  prometheus:
    image: prom/prometheus:v2.49.0
    container_name: prometheus
    restart: unless-stopped
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.retention.time=30d'

  grafana:
    image: grafana/grafana:10.3.0
    container_name: grafana
    restart: unless-stopped
    volumes:
      - grafana-data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}

  node-exporter:
    image: prom/node-exporter:v1.7.0
    container_name: node-exporter
    restart: unless-stopped
    pid: host
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--path.rootfs=/rootfs'

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:v0.49.0
    container_name: cadvisor
    restart: unless-stopped
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro

volumes:
  uptime-data:
  prometheus-data:
  grafana-data:
```

### Alert Rules

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Disk usage | >80% | >90% | Cleanup or expand |
| RAM usage | >85% | >95% | Identify memory leak, add RAM |
| CPU sustained | >80% 5min | >95% 5min | Check runaway process |
| Container restart | >2/hour | >5/hour | Check logs, fix root cause |
| SSL cert expiry | <14 days | <3 days | Renew cert |
| Backup age | >26 hours | >48 hours | Check backup script/cron |
| Service down | >2 min | >10 min | Investigate, restart |

### Notification Channels

| Channel | Service | Best For |
|---------|---------|----------|
| Push notification | ntfy.sh (self-hosted) | Mobile alerts |
| Chat | Discord/Slack webhook | Team alerts |
| Email | Uptime Kuma built-in | Formal notifications |
| Dashboard | Grafana + Uptime Kuma | Visual monitoring |

---

## Phase 9: Security Hardening

### Server Hardening Checklist

```bash
# 1. SSH hardening
# /etc/ssh/sshd_config
Port 2222                          # Change default port
PermitRootLogin no                 # No root SSH
PasswordAuthentication no          # Key-only
MaxAuthTries 3
AllowUsers yourusername

# 2. Install fail2ban
apt install fail2ban -y
systemctl enable fail2ban

# 3. Automatic security updates
apt install unattended-upgrades -y
dpkg-reconfigure -plow unattended-upgrades

# 4. Disable unused services
systemctl list-unit-files --state=enabled
# Disable anything you don't need
```

### Authentication Architecture

```
Internet → Traefik → Authelia/Authentik → Service
                         ↓
                    Check: authenticated?
                    Yes → Forward to service
                    No → Redirect to login page + 2FA
```

**Authelia** (lightweight, YAML config) — good for smaller setups
**Authentik** (full IdP, web UI) — good for many users/services, SAML/OIDC

### Security Scoring (0-100)

| Dimension | Weight | Score Guide |
|-----------|--------|-------------|
| SSH hardened (keys, non-root, non-22) | 15 | 0=default, 15=fully hardened |
| Firewall active (deny-by-default) | 15 | 0=none, 15=UFW/iptables configured |
| Reverse proxy (no direct port exposure) | 15 | 0=ports exposed, 15=all behind proxy |
| SSL/TLS on all services | 10 | 0=HTTP, 10=HTTPS everywhere |
| Auth on all public services | 15 | 0=open, 15=SSO/2FA on everything |
| Container security (non-root, limits) | 10 | 0=default, 10=hardened |
| Auto-updates enabled | 10 | 0=manual, 10=automated |
| Secrets management (.env, not hardcoded) | 10 | 0=in compose, 10=.env + restricted perms |

**Score**: 0-40 = Vulnerable, 41-70 = Acceptable, 71-90 = Good, 91-100 = Hardened

---

## Phase 10: Maintenance & Updates

### Update Strategy

**Option A: Manual (Recommended for critical services)**
```bash
# Update script: /opt/stacks/scripts/update-all.sh
#!/bin/bash
set -euo pipefail

STACKS_DIR="/opt/stacks"
LOG="/var/log/docker-updates.log"

for stack in "$STACKS_DIR"/*/; do
    if [ -f "$stack/docker-compose.yml" ]; then
        echo "[$(date)] Updating $(basename $stack)..." | tee -a "$LOG"
        cd "$stack"
        docker compose pull 2>&1 | tee -a "$LOG"
        docker compose up -d 2>&1 | tee -a "$LOG"
    fi
done

docker image prune -f | tee -a "$LOG"
echo "[$(date)] Update complete" | tee -a "$LOG"
```

**Option B: Watchtower (Automated — use with caution)**
```yaml
services:
  watchtower:
    image: containrrr/watchtower:1.7.1
    container_name: watchtower
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - WATCHTOWER_SCHEDULE=0 0 4 * * MON  # Monday 4 AM
      - WATCHTOWER_CLEANUP=true
      - WATCHTOWER_NOTIFICATIONS=shoutrrr
      - WATCHTOWER_NOTIFICATION_URL=discord://webhook
      - WATCHTOWER_LABEL_ENABLE=true    # Only update labeled containers
    # Add label to containers: com.centurylinklabs.watchtower.enable=true
```

### Weekly Maintenance Checklist

- [ ] Check Uptime Kuma for any downtime events
- [ ] Review disk usage (`df -h`)
- [ ] Check container health (`docker ps --filter health=unhealthy`)
- [ ] Review fail2ban bans (`fail2ban-client status`)
- [ ] Check backup logs (last successful backup)
- [ ] Review Docker logs for errors (`docker logs --since 7d <container>`)
- [ ] Prune unused resources (`docker system prune -f`)

### Monthly Maintenance

- [ ] Update all container images (read changelogs first!)
- [ ] Update host OS (`apt update && apt upgrade`)
- [ ] Test a backup restore
- [ ] Review and rotate secrets/passwords
- [ ] Check SSL certificate expiry dates
- [ ] Review Grafana dashboards for trends
- [ ] Clean up unused Docker networks/volumes

---

## Phase 11: Advanced Patterns

### Multi-Node Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Node 1    │     │   Node 2    │     │   Node 3    │
│ (Proxy/DNS) │────│ (Services)  │────│   (NAS)     │
│ Traefik     │     │ Apps        │     │ TrueNAS     │
│ Pi-hole     │     │ Databases   │     │ NFS/SMB     │
│ Authelia    │     │ Media       │     │ Backup      │
└─────────────┘     └─────────────┘     └─────────────┘
       ↑                   ↑                   ↑
       └───────── Tailscale Mesh ──────────────┘
```

### Docker Compose Includes (Compose v2.20+)

```yaml
# Shared fragments
include:
  - path: ../common/traefik-labels.yml
  - path: ../common/logging.yml

services:
  app:
    # inherits common configs
```

### GitOps for Homelab

```
homelab-configs/           # Git repo
├── .github/
│   └── workflows/
│       └── deploy.yml     # CI: lint + push to server
├── stacks/
│   ├── traefik/
│   ├── monitoring/
│   └── media/
├── scripts/
└── README.md
```

**Workflow**: Edit compose locally → commit → push → CI deploys to server
**Tools**: Flux/ArgoCD (overkill), or simple `git pull && docker compose up -d` via webhook

### Hardware Redundancy

| Component | Solution | Cost |
|-----------|----------|------|
| Power | UPS (APC Back-UPS 600VA+) | $60-150 |
| Storage | RAID1/ZFS mirror (not RAID0!) | 2x disk cost |
| Network | Dual NIC, managed switch | $30-100 |
| Server | Second node (cold spare or active) | $100-400 |

**Rule**: RAID is NOT backup. It protects against disk failure only, not ransomware/deletion/corruption.

---

## Phase 12: Troubleshooting

### Common Issues Decision Tree

```
Service not accessible?
├── Can you ping the server? → No → Network/firewall issue
├── Is the container running? (`docker ps`) → No → Check logs: `docker logs <name>`
├── Is the port exposed? (`docker port <name>`) → No → Check compose ports/networks
├── Is Traefik routing? (Check Traefik dashboard) → No → Check labels, network
├── Is DNS resolving? (`dig app.example.com`) → No → Check DNS provider
└── SSL error? → Check acme.json permissions (chmod 600), cert resolver logs
```

### Docker Debug Commands

```bash
# Container not starting
docker logs <name> --tail 50
docker inspect <name> | jq '.[0].State'

# Network issues
docker network ls
docker network inspect <network>
docker exec <name> ping other-container

# Resource issues
docker stats                          # Live resource usage
docker system df                      # Disk usage
docker volume ls -f dangling=true     # Orphaned volumes

# Nuclear options (use carefully)
docker compose down && docker compose up -d    # Full restart
docker system prune -af --volumes              # Clean EVERYTHING
```

### Performance Optimization

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Slow file access | HDD for database | Move DB to SSD |
| High CPU idle | Monitoring too frequent | Increase scrape intervals |
| OOM kills | No memory limits | Set `deploy.resources.limits.memory` |
| Slow Nextcloud | Missing Redis cache | Add Redis container |
| Jellyfin buffering | No hardware transcoding | Enable GPU passthrough |
| Slow Docker builds | No layer caching | Use multi-stage + .dockerignore |

---

## Service Configuration Quick Reference

### Vaultwarden (Password Manager)

```yaml
services:
  vaultwarden:
    image: vaultwarden/server:1.30.5
    container_name: vaultwarden
    restart: unless-stopped
    volumes:
      - vaultwarden-data:/data
    environment:
      - SIGNUPS_ALLOWED=false       # Disable after creating your account
      - WEBSOCKET_ENABLED=true
      - ADMIN_TOKEN=${ADMIN_TOKEN}  # Generate: openssl rand -base64 48
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.vault.rule=Host(`vault.example.com`)"
```

### Immich (Photo Backup)

```yaml
# Use their official docker-compose.yml from:
# https://github.com/immich-app/immich/releases/latest/download/docker-compose.yml
# Key settings:
# - Set UPLOAD_LOCATION to a large storage mount
# - Enable hardware transcoding if GPU available
# - Set IMMICH_MACHINE_LEARNING_URL for face detection
```

### Paperless-ngx (Document Management)

```yaml
services:
  paperless:
    image: ghcr.io/paperless-ngx/paperless-ngx:2.4
    container_name: paperless
    restart: unless-stopped
    volumes:
      - paperless-data:/usr/src/paperless/data
      - paperless-media:/usr/src/paperless/media
      - ./consume:/usr/src/paperless/consume  # Drop PDFs here
      - ./export:/usr/src/paperless/export
    environment:
      - PAPERLESS_OCR_LANGUAGE=eng
      - PAPERLESS_TIME_ZONE=Europe/London
      - PAPERLESS_ADMIN_USER=${ADMIN_USER}
      - PAPERLESS_ADMIN_PASSWORD=${ADMIN_PASS}
```

---

## Homelab Quality Rubric (0-100)

| Dimension | Weight | 0 (Poor) | 50 (Decent) | 100 (Excellent) |
|-----------|--------|----------|-------------|-----------------|
| Security | 20% | Default passwords, open ports | Firewall + SSL | Hardened SSH, SSO/2FA, no-new-privileges |
| Backups | 20% | None | Local only, untested | 3-2-1, automated, verified monthly |
| Monitoring | 15% | None | Uptime Kuma only | Full stack: metrics + logs + alerts |
| Documentation | 10% | Nothing written | README per stack | GitOps, full runbook, diagrams |
| Updates | 10% | Never updated | Manual quarterly | Scheduled weekly, changelogs reviewed |
| Reliability | 10% | Frequent crashes | Mostly stable | UPS, auto-restart, health checks |
| Performance | 10% | Slow, OOM kills | Adequate | Resource limits, SSD, HW transcoding |
| Scalability | 5% | Single machine, no plan | Compose organized | Multi-node ready, IaC |

---

## 10 Self-Hosting Mistakes

| # | Mistake | Fix |
|---|---------|-----|
| 1 | Using `:latest` tag | Pin versions: `image:1.2.3` |
| 2 | No backups | 3-2-1 backup rule, test restores |
| 3 | Exposing ports directly | Everything behind reverse proxy |
| 4 | Default passwords | Change immediately, use password manager |
| 5 | No monitoring | Uptime Kuma minimum, Grafana for depth |
| 6 | RAID = backup mentality | RAID protects disks, not data |
| 7 | Over-engineering day 1 | Start small, add complexity as needed |
| 8 | No documentation | Document every service, every port, every cron |
| 9 | Ignoring updates | Security patches matter, schedule updates |
| 10 | Running as root | Non-root containers, restricted SSH |

---

## Natural Language Commands

| Say | Agent Does |
|-----|-----------|
| "Set up a new service" | Guide through compose file creation with security best practices |
| "Audit my homelab security" | Run through security scoring checklist |
| "Plan my backup strategy" | Design 3-2-1 backup plan for your setup |
| "What should I self-host?" | Assess needs and recommend services by tier |
| "My container keeps crashing" | Walk through troubleshooting decision tree |
| "Help me set up Traefik" | Generate production Traefik config with SSL |
| "Compare NAS options" | Compare TrueNAS vs Unraid vs DIY for your needs |
| "Optimize my Docker setup" | Review compose files for security and performance |
| "Set up monitoring" | Deploy Uptime Kuma + Prometheus + Grafana stack |
| "Plan a hardware upgrade" | Assess current usage, recommend hardware by budget |
| "Migrate from cloud to self-hosted" | Plan migration with data export and service mapping |
| "Set up remote access" | Compare and deploy VPN/Tailscale for secure remote access |
