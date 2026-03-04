---
description: Set up and manage SSH tunnels, port forwarding, and SOCKS proxies with simple commands.
---

# Port Forwarder

Set up and manage SSH tunnels and port forwarding.

**Use when** creating SSH tunnels, forwarding ports, or setting up SOCKS proxies.

## Requirements

- OpenSSH client (`ssh`)
- Optional: `autossh` for persistent tunnels
- No API keys needed

## Instructions

### Local Port Forwarding
Access a remote service as if it's local:
```bash
# Forward local:8080 → remote:80
ssh -fNL 8080:localhost:80 user@remote-host

# Access a service behind a jump host
ssh -fNL 5432:db-server:5432 user@jump-host

# Bind to all interfaces (not just localhost)
ssh -fNL 0.0.0.0:8080:localhost:80 user@remote-host
```

### Remote Port Forwarding
Expose a local service on the remote host:
```bash
# Expose local:3000 on remote:9000
ssh -fNR 9000:localhost:3000 user@remote-host
```

### Dynamic SOCKS Proxy
Route all traffic through the remote host:
```bash
ssh -fND 1080 user@remote-host
# Configure browser: SOCKS5 proxy → localhost:1080
```

### SSH Flag Reference

| Flag | Meaning |
|------|---------|
| `-f` | Background after auth |
| `-N` | No remote command (tunnel only) |
| `-L` | Local port forward |
| `-R` | Remote port forward |
| `-D` | Dynamic SOCKS proxy |
| `-o ServerAliveInterval=60` | Keep alive every 60s |
| `-o ExitOnForwardFailure=yes` | Fail if port binding fails |

### Management Commands
```bash
# List active SSH tunnels
ps aux | grep 'ssh -[fN]' | grep -v grep

# Test if a forwarded port works
nc -zv localhost 8080
curl -s http://localhost:8080

# Kill a specific tunnel
kill <PID>

# Kill all SSH tunnels
pkill -f 'ssh -fN'
```

### Persistent Tunnels with autossh
```bash
# Auto-reconnect on failure
autossh -M 0 -fNL 8080:localhost:80 user@remote-host \
  -o "ServerAliveInterval=30" \
  -o "ServerAliveCountMax=3"

# As a systemd service
# Create /etc/systemd/system/ssh-tunnel.service
```

## Output Format
When reporting tunnel status:
```
## 🔌 Active SSH Tunnels
| PID | Type | Local | Remote | Host | Status |
|-----|------|-------|--------|------|--------|
| 1234 | Local | :8080 | :80 | server1 | 🟢 Active |
| 5678 | SOCKS | :1080 | — | proxy1 | 🟢 Active |
```

## Edge Cases

- **Port already in use**: Check with `lsof -i :8080` or `ss -tlnp | grep 8080`.
- **Connection drops**: Add `-o ServerAliveInterval=60 -o ServerAliveCountMax=3`. Or use `autossh`.
- **Permission denied**: Ensure SSH key is configured. Check `~/.ssh/config`.
- **Remote port forwarding blocked**: Server needs `GatewayPorts yes` in `/etc/ssh/sshd_config`.
- **Tunnel works but service doesn't respond**: The remote service might only listen on localhost.

## Security Considerations

- **Never forward sensitive ports to `0.0.0.0`** unless intentional — this exposes to all network interfaces.
- Use SSH key auth, not passwords, for tunnel connections.
- Restrict remote port forwarding on servers that don't need it.
- Monitor active tunnels — orphaned tunnels can be security risks.
