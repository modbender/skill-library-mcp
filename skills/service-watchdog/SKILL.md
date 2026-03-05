# Service Watchdog

Lightweight service and endpoint monitoring for self-hosted infrastructure. Checks HTTP endpoints, TCP ports, SSL certificate expiry, and DNS resolution — then reports status in a clean, chat-friendly format.

## What It Does

- **HTTP Health Checks** — GET/POST with expected status codes, response time tracking, content matching
- **TCP Port Checks** — Verify services are listening (databases, mail servers, game servers, etc.)
- **SSL Certificate Monitoring** — Days until expiry, issuer info, auto-warn thresholds
- **DNS Resolution** — Verify domains resolve correctly, detect DNS hijacking
- **Smart Summaries** — One-glance status for all your services, with trend data
- **Alert Logic** — Configurable thresholds, cooldowns, and severity levels to prevent alert fatigue

## Quick Start

### 1. Create a watchlist

Create `watchdog.json` in your workspace root:

```json
{
  "services": [
    {
      "name": "Home Assistant",
      "type": "http",
      "url": "http://192.168.1.100:8123",
      "expect_status": 200,
      "timeout_ms": 5000
    },
    {
      "name": "Proxmox",
      "type": "https",
      "url": "https://proxmox.local:8006",
      "expect_status": 200,
      "ssl_warn_days": 14,
      "timeout_ms": 5000
    },
    {
      "name": "PostgreSQL",
      "type": "tcp",
      "host": "db.local",
      "port": 5432,
      "timeout_ms": 3000
    },
    {
      "name": "My Domain",
      "type": "dns",
      "domain": "example.com",
      "expect_ip": "93.184.216.34"
    }
  ],
  "defaults": {
    "timeout_ms": 5000,
    "ssl_warn_days": 14,
    "alert_cooldown_min": 30,
    "history_retention_days": 30
  }
}
```

### 2. Run a check

```bash
bash skills/service-watchdog/watchdog.sh
```

Output example:
```
🟢 Home Assistant       — 200 OK (142ms)
🟢 Proxmox              — 200 OK (89ms) | SSL: 47 days
🟢 PostgreSQL           — port 5432 open (12ms)
🟢 My Domain            — resolves to 93.184.216.34 ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4/4 healthy | avg response: 81ms | checked: 2026-02-24 16:30 UTC
```

### 3. Detailed report

```bash
bash skills/service-watchdog/watchdog.sh --report
```

Shows trend data: uptime percentage, P95 response times, incident history.

### 4. JSON output (for cron integration)

```bash
bash skills/service-watchdog/watchdog.sh --json
```

### 5. Check SSL only

```bash
bash skills/service-watchdog/watchdog.sh --ssl-only
```

### 6. Alert summary (for messaging)

```bash
bash skills/service-watchdog/watchdog.sh --alerts-only
```

Only outputs services that need attention (down, slow, SSL expiring).

## Cron Integration

Add to your OpenClaw cron for continuous monitoring:

**Every 5 minutes (lightweight check):**
```
Run `bash skills/service-watchdog/watchdog.sh --json` and report only if any service is unhealthy.
```

**Daily SSL report:**
```
Run `bash skills/service-watchdog/watchdog.sh --ssl-only` and report expiring certificates.
```

## Configuration Reference

### Service types

| Type | Required Fields | Optional Fields |
|------|----------------|-----------------|
| `http` / `https` | `url` | `expect_status`, `expect_body`, `method`, `headers`, `timeout_ms`, `ssl_warn_days` |
| `tcp` | `host`, `port` | `timeout_ms` |
| `dns` | `domain` | `expect_ip`, `nameserver` |

### Global defaults

| Field | Default | Description |
|-------|---------|-------------|
| `timeout_ms` | 5000 | Request timeout |
| `ssl_warn_days` | 14 | SSL expiry warning threshold |
| `alert_cooldown_min` | 30 | Min minutes between repeated alerts |
| `history_retention_days` | 30 | How long to keep check history |
| `history_file` | `watchdog-history.csv` | Path for check history data |

## How the Agent Should Use This

When the user asks about service status, infrastructure health, or "are my services up?":

1. Run `bash skills/service-watchdog/watchdog.sh` for a quick overview
2. Run with `--report` for detailed trends and history
3. Run with `--alerts-only` for just the problems
4. Run with `--ssl-only` to check certificate status
5. Run with `--json` when you need structured data for further analysis

For proactive monitoring, run checks in cron jobs and only alert the user when something is wrong.

## Requirements

- `curl` (for HTTP/HTTPS checks)
- `openssl` (for SSL certificate checks)
- `nc` or `ncat` (for TCP port checks) — falls back to bash `/dev/tcp` if unavailable
- `dig` or `nslookup` (for DNS checks) — falls back to `host` command
- `jq` (for JSON config parsing)

All standard on most Linux distributions. No external APIs or accounts needed.
