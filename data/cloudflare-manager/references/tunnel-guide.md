# Cloudflare Tunnel Configuration (cloudflared)

## CLI Basics
- `cloudflared login`: Authenticate with Cloudflare.
- `cloudflared tunnel create <name>`: Create new tunnel (UUID).
- `cloudflared tunnel run <name>`: Start tunnel.
- `cloudflared access tcp`: For SSH/RDP access.

## config.yml Template
```yaml
tunnel: <UUID>
credentials-file: /root/.cloudflared/<UUID>.json

ingress:
  # SSH Access
  - hostname: ssh.example.com
    service: ssh://localhost:22

  # Web App
  - hostname: app.example.com
    service: http://localhost:3000

  # Default Fallback (Required)
  - service: http_status:404
```

## Systemd Service
- Install: `cloudflared service install`.
- Logs: `journalctl -u cloudflared`.
