---
name: Self-Host
description: Deploy and maintain self-hosted services with security, backups, and long-term reliability.
metadata: {"clawdbot":{"emoji":"🖥️","requires":{"anyBins":["docker","podman"]},"os":["linux","darwin","win32"]}}
---

# Self-Hosting Rules

## Before Installing Anything
- Backups first — decide where data lives and how it's backed up before deploying, not after data exists
- Check resource requirements — many services need more RAM than expected, OOM kills corrupt data
- Verify the project is actively maintained — abandoned projects become security liabilities

## Docker Fundamentals
- Always use named volumes or bind mounts for persistent data — anonymous volumes are lost on container removal
- Pin image versions (`nginx:1.25.3` not `nginx:latest`) — latest changes unexpectedly and breaks setups
- Set restart policy (`unless-stopped` or `on-failure`) — containers don't auto-start after reboot by default
- Use `docker compose down` not `docker compose rm` — down handles networks and volumes properly

## Networking
- Never expose database ports to the internet — only the reverse proxy should be public
- Use a reverse proxy (Traefik, Caddy, Nginx Proxy Manager) — handles SSL, routing, and security in one place
- Create Docker networks per project — default bridge network lacks DNS resolution between containers
- Bind admin interfaces to localhost only (`127.0.0.1:8080:8080`) — not all traffic needs to be public

## SSL and Domains
- Use automatic SSL with Let's Encrypt — Caddy and Traefik do this natively
- For local/LAN access, use a real domain with DNS challenge — avoids browser certificate warnings
- Wildcard certificates simplify multi-service setups — one cert for *.home.example.com

## Security Essentials
- Change all default passwords immediately — bots scan for default credentials within hours
- Enable automatic security updates for the host OS — unpatched systems get compromised
- Use fail2ban or equivalent — brute force attacks are constant
- Keep services behind authentication (Authelia, Authentik) — not everything has built-in auth
- Disable root SSH, use key-only authentication — password SSH is a vulnerability

## Backups
- Test restores, not just backups — untested backups are wishful thinking
- 3-2-1 rule: 3 copies, 2 different media, 1 offsite — local RAID is not backup
- Automate backup schedules — manual backups get forgotten
- Back up Docker volumes, not containers — containers are ephemeral, data is not

## Monitoring
- Set up uptime monitoring (Uptime Kuma is self-hostable) — know when services die before users tell you
- Monitor disk space — full disks cause silent failures and corruption
- Log rotation is mandatory — Docker logs grow forever by default, fill disks
- Consider resource monitoring (Netdata, Prometheus) — spot problems before they're critical

## Maintenance
- Schedule regular update windows — services need updates, plan for downtime
- Document everything you deploy — future you won't remember why that container exists
- Keep a compose file repo — reproducibility matters when hardware fails
- Test updates on staging when possible — production surprises are painful

## Home Server Specifics
- Dynamic DNS if ISP doesn't provide static IP — Cloudflare, DuckDNS work well
- UPS protects against power loss corruption — especially important for databases
- Consider power consumption — some hardware costs more in electricity than cloud hosting
- Port forwarding exposes your home network — use VPN (WireGuard, Tailscale) instead when possible

## Common Mistakes
- Putting everything on one machine with no redundancy — single point of failure for all services
- Ignoring updates for months — security vulnerabilities accumulate
- No firewall rules — assuming "nobody knows my IP" is security
- Storing secrets in docker-compose.yml committed to git — use .env files, exclude from version control
- Over-engineering from day one — start simple, add complexity when needed
