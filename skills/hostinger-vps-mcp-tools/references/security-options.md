# Security Options

Choose the security setup that fits your needs.

## Quick Comparison

| Method | Difficulty | Public Ports | Best For |
|--------|------------|--------------|----------|
| **Tailscale** | Easy | None | Personal/team use |
| **Cloudflare Tunnel** | Easy | None | Public access with protection |
| **WireGuard** | Medium | 1 (VPN) | Self-hosted VPN |
| **HTTPS + Nginx** | Medium | 443 | Public access with SSL |

## Recommended Setups

### 🏆 Most Secure: Tailscale (Zero Public Ports)

```bash
# Install Tailscale
./scripts/security/setup-tailscale.sh

# Lock down public access
./scripts/security/lockdown-public.sh

# Access via Tailscale IP only
# http://100.x.x.x:18789
```

**Pros:**
- No public ports exposed
- End-to-end encryption
- Easy to add team members
- Works through NAT/firewalls
- Free for personal use

### 🌐 Public Access: Cloudflare Tunnel

```bash
# 1. Create tunnel at https://one.dash.cloudflare.com/
# 2. Copy tunnel token
./scripts/security/setup-cloudflare-tunnel.sh YOUR_TOKEN

# 3. Lock down direct access
./scripts/security/lockdown-public.sh

# Access via your domain with HTTPS
# https://koda.yourdomain.com
```

**Pros:**
- Free HTTPS/SSL
- DDoS protection
- No public ports needed
- Can add Zero Trust policies

### 🔐 Self-Hosted VPN: WireGuard

```bash
# Setup WireGuard server
./scripts/security/setup-wireguard.sh my-laptop

# Import config on your device
# /etc/wireguard/my-laptop.conf

# Lock down public access
./scripts/security/lockdown-public.sh

# Access via VPN IP
# http://10.200.200.1:18789
```

**Pros:**
- Full control
- Very fast (kernel-level)
- Works on all platforms

### 🌍 Public with SSL: HTTPS + Nginx

```bash
# Requires a domain pointing to your server
./scripts/security/setup-https.sh koda.example.com you@email.com

# Access via HTTPS
# https://koda.example.com
```

**Pros:**
- Standard HTTPS access
- No VPN client needed
- Good for public-facing services

## Additional Hardening

Always run after basic setup:

```bash
# SSH key-only authentication
./scripts/security/setup-ssh-keys.sh "ssh-rsa AAAA..."

# Full server hardening
./scripts/security/harden-server.sh
```

## Security Checklist

- [ ] Changed default SSH port
- [ ] SSH key-only authentication
- [ ] Firewall configured (UFW)
- [ ] fail2ban running
- [ ] Automatic security updates
- [ ] VPN or tunnel configured
- [ ] Public ports removed
- [ ] Strong passwords for all accounts

## Accessing Locked-Down Server

After lockdown, connect via:

```bash
# Tailscale
tailscale up  # On your machine
ssh koda@100.x.x.x

# WireGuard  
wg-quick up client1  # On your machine
ssh koda@10.200.200.1

# Cloudflare (SSH over tunnel)
# Configure SSH tunnel in Cloudflare dashboard
```
