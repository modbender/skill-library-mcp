---
name: opnsense-admin
description: Manage OPNsense firewall, DNS, IDS/IPS, and network configuration via API and SSH. Use when administering OPNsense firewall, configuring Suricata IDS/IPS, managing Unbound DNS, creating firewall rules, backing up configurations, monitoring traffic, or troubleshooting network issues. Supports both API-based automation and SSH command execution for OPNsense 26.1+.
---

# OPNsense Admin

> ⚠️ **DISCLAIMER**
>
> This tool grants **HIGH PRIVILEGE** access to your firewall and network.
> It can modify firewall rules, block traffic, and restart critical services.
>
> **By using this skill, you declare that:**
> - You are a responsible adult
> - You have authorization to administer this firewall
> - You understand that a mistake can render your network inoperable
> - You will use this tool ethically and legally
>
> **The author is not responsible** for misconfigurations, access lockouts,
> or damages resulting from the use of this skill.

Complete OPNsense firewall administration via API and SSH. Automate backups, monitor security, manage services, and troubleshoot network issues.

## Features

- 🔥 **Firewall Management** - Rules, NAT, aliases, and diagnostics
- 🛡️ **IDS/IPS (Suricata)** - Monitor and manage intrusion detection/prevention
- 🌐 **DNS (Unbound)** - DNS resolver, blocklists, forwarding, DNS over TLS
- 📊 **Monitoring** - Service status, traffic analysis, system health
- 💾 **Automated Backups** - Scheduled configuration backups with retention
- 🔧 **Service Control** - Start/stop/restart services via SSH
- 🔌 **API Integration** - RESTful API wrapper for automation

## Installation

### Prerequisites

- OPNsense 26.1 or later
- API key with appropriate permissions
- SSH access (optional, for service management)

### Quick Setup

1. Generate API credentials in OPNsense:
   ```
   System → Access → Users → API
   ```

2. Configure credentials (choose one method):

   **Option A: Environment variables**
   ```bash
   export OPNSENSE_HOST="192.168.1.1"
   export OPNSENSE_KEY="your_api_key"
   export OPNSENSE_SECRET="your_api_secret"
   ```

   **Option B: Credentials file** (recommended)
   ```bash
   mkdir -p ~/.opnsense
   cat > ~/.opnsense/credentials << EOF
   OPNSENSE_HOST=192.168.1.1
   OPNSENSE_PORT=443
   OPNSENSE_KEY=your_api_key
   OPNSENSE_SECRET=your_api_secret
   EOF
   chmod 600 ~/.opnsense/credentials
   ```

## Usage

### API Helper Script

```bash
# Check system status
./scripts/opnsense-api.sh status

# Get firmware information
./scripts/opnsense-api.sh firmware-status

# Check Suricata status
./scripts/opnsense-api.sh suricata-status

# Custom API request
./scripts/opnsense-api.sh get /api/core/system/status
./scripts/opnsense-api.sh post /api/core/firmware/update '{"upgrade":true}'
```

### Configuration Backup

```bash
# Full backup (with RRD data)
./scripts/backup-config.sh

# Config-only backup (smaller)
./scripts/backup-config.sh --config-only

# Custom directory and retention
./scripts/backup-config.sh --dir /mnt/backups --keep 90
```

### Service Control

```bash
# Restart DNS resolver
./scripts/service-control.sh unbound restart

# Check Suricata status
./scripts/service-control.sh suricata status

# Reload DHCP configuration
./scripts/service-control.sh dhcpd reload

# Check all services
./scripts/service-control.sh all status
```

## Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPNSENSE_HOST` | `192.168.1.1` | OPNsense IP or hostname |
| `OPNSENSE_PORT` | `443` | HTTPS port |
| `OPNSENSE_KEY` | - | API key |
| `OPNSENSE_SECRET` | - | API secret |
| `SSH_PORT` | `22` | SSH port for service control |
| `BACKUP_DIR` | `./backups` | Default backup directory |
| `KEEP_DAYS` | `30` | Backup retention period |

### Common API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/core/system/status` | GET | System health |
| `/api/core/firmware/status` | GET | Firmware info |
| `/api/ids/service/status` | GET | Suricata status |
| `/api/unbound/diagnostics/stats` | GET | DNS statistics |
| `/api/diagnostics/interface/getInterfaceConfig` | GET | Interface config |
| `/api/diagnostics/firewall/pfstatists` | GET | Firewall stats |
| `/api/core/backup/backup` | GET | Download backup |

## Security Best Practices

1. **SSL Certificate Validation** - Enabled by default. Use `--insecure` or `OPNSENSE_INSECURE=true` ONLY for development or self-signed certificates in internal networks
2. **Restrict API permissions** - Create dedicated API users with minimal required permissions
3. **Secure credential storage** - Use file permissions (600) and environment variables
4. **Backup before changes** - Always backup configuration before making changes
5. **Test IDS rules first** - Run Suricata in IDS mode before enabling IPS blocking

### SSL/TLS Configuration

By default, all API calls validate SSL certificates. For production deployments with valid certificates, no changes needed.

For development or self-signed certificates:
```bash
# Option 1: Command line flag
./scripts/opnsense-api.sh --insecure status

# Option 2: Environment variable
export OPNSENSE_INSECURE=true
./scripts/opnsense-api.sh status
```

## Key Concepts

### Firewall Rules

- **Stateful filtering** - Connection tracking enabled by default
- **Processing order**: Floating → Interface Groups → Interface Rules
- **Actions**: Pass (allow), Block (drop silently), Reject (drop with notice)
- **NAT**: Processed BEFORE filter rules

### Suricata IDS/IPS

- **IDS Mode**: Detection only (alerts, no blocking)
- **IPS Mode**: Detection + blocking (requires inline setup)
- **Best Practice**: Monitor on LAN interface to see real client IPs
- **Rules**: Emerging Threats, Abuse.ch feeds, app detection

### Unbound DNS

- **Recursive resolver** - Queries root servers directly by default
- **DNSSEC validation** - Enabled by default for security
- **Blocklists** - DNS-based ad/tracker blocking via plugin
- **DNS over TLS** - Encrypted upstream queries

## Troubleshooting

### API Connection Issues

```bash
# Test connectivity
curl -k -u "key:secret" https://opnsense/api/core/system/status

# Check API is enabled in OPNsense
# System → Access → Settings → Enable API
```

### SSH Connection Issues

```bash
# Test SSH connectivity
ssh -p 22 root@opnsense "echo OK"

# Check SSH is enabled
# System → Administration → Secure Shell
```

### Permission Denied

- Verify API key has required permissions
- Check user is member of appropriate groups
- Ensure API is enabled in System → Access → Settings

## Version Compatibility

| OPNsense Version | Skill Version | Status |
|------------------|---------------|--------|
| 26.1+ | 1.x | ✅ Supported |
| 25.x | 1.x | ⚠️ May work |
| 24.x | 1.x | ❌ Not tested |

## Reference Documentation

- [API Guide](references/api-guide.md) - Complete API authentication guide
- [Firewall Rules](references/firewall-rules.md) - Rule structure and examples
- [Suricata IPS](references/suricata-ips.md) - IDS/IPS configuration
- [Unbound DNS](references/unbound-dns.md) - DNS resolver setup
- [Quick Reference](references/quick-ref.md) - Commands and file locations

## License

MIT - See LICENSE file for details.

## Contributing

Issues and pull requests welcome at the GitHub repository.

---

**Disclaimer**: This is an unofficial skill. Not affiliated with Deciso B.V. or the OPNsense project.
