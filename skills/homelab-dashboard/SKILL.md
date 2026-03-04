---
description: Generate a status dashboard for self-hosted services, Docker containers, and homelab infrastructure.
---

# Homelab Dashboard

Check health and status of homelab services and infrastructure.

**Use when** checking service status, monitoring Docker containers, or getting a homelab overview.

## Requirements

- Linux system with standard tools (`free`, `df`, `uptime`)
- Optional: Docker, systemd, curl
- No API keys needed

## Instructions

1. **System resources**:
   ```bash
   nproc                          # CPU cores
   uptime                         # load average
   free -h                        # memory usage
   df -h / /mnt/* 2>/dev/null     # disk usage (root + mounts)
   ```

2. **Docker containers** (if Docker is installed):
   ```bash
   docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null
   docker ps -a --filter "status=exited" --format '{{.Names}}\t{{.Status}}' 2>/dev/null
   ```

3. **HTTP health checks** (if user provides URLs):
   ```bash
   curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 10 <url>
   ```
   - 200-299: 🟢 Healthy
   - 300-399: 🟡 Redirect
   - 400+: 🔴 Error
   - No response: 🔴 Down

4. **Systemd services** (if specified):
   ```bash
   systemctl is-active <service>
   systemctl is-failed <service>  # check for failed services
   ```

5. **Output format**:
   ```
   🏠 Homelab Dashboard — 2025-01-15 14:30 JST

   ## 💻 System Resources
   | Resource | Usage | Status |
   |----------|-------|--------|
   | CPU | 4 cores, load 1.2 | 🟢 Normal |
   | Memory | 6.2G / 16G (39%) | 🟢 Normal |
   | Disk / | 120G / 500G (24%) | 🟢 Normal |
   | Disk /mnt/hdd | 2.1T / 2.7T (78%) | 🟡 Warning |

   ## 🐳 Docker Containers
   | Container | Status | Ports |
   |-----------|--------|-------|
   | nginx | 🟢 Up 3 days | 80, 443 |
   | postgres | 🟢 Up 3 days | 5432 |
   | redis | 🔴 Exited (1) 2h ago | — |

   ## 🌐 Services
   | Service | Status | Response |
   |---------|--------|----------|
   | Nextcloud | 🟢 200 OK | 142ms |
   | Gitea | 🔴 Connection refused | — |

   ## ⚠️ Alerts
   - 🔴 redis container is down (exited with code 1)
   - 🔴 Gitea is unreachable
   - 🟡 /mnt/hdd disk usage at 78% — consider cleanup
   ```

6. **Alert thresholds**:
   - Disk > 85%: 🔴 Critical
   - Disk > 70%: 🟡 Warning
   - Memory > 90%: 🔴 Critical
   - Load > 2× CPU cores: 🟡 Warning
   - Any stopped container or failed service: 🔴

## Edge Cases

- **Docker not installed**: Skip container section, note it in output.
- **Permission denied**: Some commands need sudo. Report what couldn't be checked.
- **Remote hosts**: Use SSH (`ssh user@host "command"`) for checking remote machines.
- **No services specified**: Run a general system check + Docker containers only.

## Security Considerations

- Don't expose internal service URLs or IPs in shared outputs.
- Health check URLs may contain tokens — redact them in output.
