# Infra Watchdog — Infrastructure Monitoring & Health Alerts

Self-hosted infrastructure monitoring for OpenClaw agents. Zero external SaaS required — monitors everything locally and alerts via WhatsApp, Telegram, or Discord.

## What It Does

- **HTTP/HTTPS endpoint monitoring** — checks status codes, response time, SSL validity
- **TCP port checks** — database, SSH, custom services
- **Docker container status** — running, stopped, unhealthy
- **System resources** — CPU, RAM, disk usage with configurable thresholds
- **SSL certificate expiry** — alerts 30 days before expiry
- **DNS resolution checks** — verifies domain → IP mappings
- **Proxmox VM/CT status** — checks via local API
- **Alerts via WhatsApp/Telegram/Discord** — with configurable cooldown

## Quick Start

```bash
# Initialize data directory & config
infra-watchdog init

# Add your first monitor
infra-watchdog add-monitor --type http --name "My API" --url https://myapi.example.com

# Add a TCP port check
infra-watchdog add-monitor --type tcp --name "PostgreSQL" --host localhost --port 5432

# Add a Docker container check
infra-watchdog add-monitor --type docker --name "My App" --container myapp

# Run all checks now
infra-watchdog check

# View current status dashboard
infra-watchdog dashboard

# Install auto-check cron (every 5 min)
infra-watchdog cron-install
```

## Commands

| Command | Description |
|---------|-------------|
| `infra-watchdog init` | Set up data directory and default config |
| `infra-watchdog add-monitor` | Add a new monitor (http/tcp/docker/resource/ssl/dns) |
| `infra-watchdog list` | List all configured monitors and their current state |
| `infra-watchdog check` | Run all checks immediately |
| `infra-watchdog check --name <name>` | Run a specific monitor |
| `infra-watchdog status` | Summary: UP/DOWN/WARN counts |
| `infra-watchdog dashboard` | ASCII dashboard with all monitors |
| `infra-watchdog cron-install` | Install auto-check cron job |

## Monitor Types

### HTTP/HTTPS
```bash
infra-watchdog add-monitor \
  --type http \
  --name "Main API" \
  --url https://api.example.com/health \
  --expected-status 200 \
  --timeout 5
```

### TCP Port
```bash
infra-watchdog add-monitor \
  --type tcp \
  --name "Postgres" \
  --host 192.168.1.10 \
  --port 5432
```

### Docker Container
```bash
infra-watchdog add-monitor \
  --type docker \
  --name "Nginx" \
  --container nginx-proxy
```

### System Resources
```bash
infra-watchdog add-monitor \
  --type resource \
  --name "Disk /" \
  --resource disk \
  --path / \
  --warn-at 80 \
  --alert-at 90
```

### SSL Certificate
```bash
infra-watchdog add-monitor \
  --type ssl \
  --name "My Domain SSL" \
  --host example.com \
  --port 443 \
  --warn-days 30
```

## Configuration

Edit `~/.openclaw/workspace/infra-watchdog-data/config.json`:

```json
{
  "alert_channel": "whatsapp",
  "alert_cooldown_minutes": 15,
  "check_interval_minutes": 5,
  "ssl_expiry_warning_days": 30
}
```

## Alert Channels

| Channel | Config value |
|---------|-------------|
| WhatsApp | `"whatsapp"` |
| Telegram | `"telegram"` |
| Discord | `"discord"` |
| None (log only) | `"none"` |

## Use Cases

### Homelab Monitoring
Track all your self-hosted services: Proxmox, Docker stacks, databases, Jellyfin, Home Assistant, etc. Get a WhatsApp alert the moment anything goes down.

### API Uptime Monitoring
If you sell API services on RapidAPI, this skill monitors your endpoints 24/7 and pings you before customers notice an outage.

### SSL Expiry Prevention
Never let a certificate expire again. Get a WhatsApp warning 30 days before expiry.

### Resource Alerts
Disk full at 3am? Get alerted before it kills your services.

## Data Storage

All data stored locally at `~/.openclaw/workspace/infra-watchdog-data/`. SQLite database, no cloud sync, no telemetry.

## Requirements

- Python 3.8+
- Docker (optional, for container monitoring)
- OpenClaw 1.0+

## Source & Issues

- **Source:** https://github.com/mariusfit/infra-watchdog
- **Issues:** https://github.com/mariusfit/infra-watchdog/issues
- **Author:** [@mariusfit](https://github.com/mariusfit)
