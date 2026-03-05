## Security & Remote Access

### Golden Rule

**No ports exposed to internet.** Period.

### Secure Remote Access Options

| Method | Complexity | Security |
|--------|------------|----------|
| Tailscale | Easy | Excellent |
| WireGuard | Medium | Excellent |
| Cloudflare Tunnel | Medium | Good |
| Synology QuickConnect | Easy | Acceptable |
| OpenVPN | Hard | Good |
| Port forwarding + DDNS | Easy | **TERRIBLE** |

### Common Traps

1. **QuickConnect is convenience, not security** — Acceptable for personal use, but adds relay dependency.

2. **Exposing DSM/QTS = ransomware target** — Shodan scans find open NAS admin panels in minutes.

3. **Brute force is real** — Log shows thousands of login attempts. Fail2ban + auto-block mandatory.

4. **VPN to NAS, not router** — NAS-hosted VPN (Synology VPN Server) exposes less than router VPN.

### Hardening Checklist

- [ ] Disable default admin account
- [ ] Named admin accounts only
- [ ] 2FA enabled for all users
- [ ] Auto-block after 5 failed logins
- [ ] Firewall: deny all, allow specific
- [ ] HTTPS only (disable HTTP redirect)
- [ ] Update DSM/QTS within days of release
- [ ] Disable unused services (Telnet, SSH if not needed)
- [ ] Security Advisor scan monthly

### SSL Certificates

```
Option 1: Let's Encrypt (free, auto-renew)
Option 2: Reverse proxy (nginx/Caddy handles SSL)
Option 3: Cloudflare Tunnel (no certs to manage)
```

### Firewall Rules

Only enable what you use:

```
SMB: LAN only (port 445)
NFS: LAN only (port 2049)
Web station: LAN or behind reverse proxy
Docker: LAN only unless reverse proxied
```
