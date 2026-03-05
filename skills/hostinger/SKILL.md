---
name: hostinger
description: Manage Hostinger account via API — VPS administration (start/stop/restart, snapshots, backups, firewall, Docker), DNS zone management, domain portfolio, website hosting, and billing. Use when asked to deploy, publish, manage servers, configure DNS, or control any Hostinger service.
---

# Hostinger API Skill

Control Hostinger services programmatically: VPS instances, DNS records, domains, websites, hosting.

## Authentication

API token required. Get one from: https://hpanel.hostinger.com/profile/api

Store in `~/.config/hostinger/token` (just the token, no newline):
```bash
mkdir -p ~/.config/hostinger
echo -n "YOUR_API_TOKEN" > ~/.config/hostinger/token
chmod 600 ~/.config/hostinger/token
```

## Quick Reference

### VPS Operations

```bash
# List all VPS instances
python3 scripts/hostinger.py vps list

# Get VPS details
python3 scripts/hostinger.py vps get <vm_id>

# Start/stop/restart VPS
python3 scripts/hostinger.py vps start <vm_id>
python3 scripts/hostinger.py vps stop <vm_id>
python3 scripts/hostinger.py vps restart <vm_id>

# Create/restore snapshots
python3 scripts/hostinger.py vps snapshot-create <vm_id>
python3 scripts/hostinger.py vps snapshot-restore <vm_id>

# View backups
python3 scripts/hostinger.py vps backups <vm_id>
```

### DNS Management

```bash
# Get DNS records for domain
python3 scripts/hostinger.py dns get <domain>

# Update DNS records (JSON file with records array)
python3 scripts/hostinger.py dns update <domain> <records.json>

# Reset DNS to defaults
python3 scripts/hostinger.py dns reset <domain>

# DNS snapshots
python3 scripts/hostinger.py dns snapshots <domain>
python3 scripts/hostinger.py dns snapshot-restore <domain> <snapshot_id>
```

### Domain Portfolio

```bash
# List all domains
python3 scripts/hostinger.py domains list

# Get domain details
python3 scripts/hostinger.py domains get <domain>

# Update nameservers
python3 scripts/hostinger.py domains nameservers <domain> ns1.example.com ns2.example.com

# Check availability
python3 scripts/hostinger.py domains check example.com example.org
```

### Hosting/Websites

```bash
# List websites
python3 scripts/hostinger.py hosting websites

# List datacenters
python3 scripts/hostinger.py hosting datacenters
```

### Billing

```bash
# View subscriptions
python3 scripts/hostinger.py billing subscriptions

# View payment methods
python3 scripts/hostinger.py billing payment-methods

# View catalog
python3 scripts/hostinger.py billing catalog
```

## DNS Record Format

When updating DNS records, provide a JSON file:
```json
{
  "records": [
    {"type": "A", "name": "@", "value": "1.2.3.4", "ttl": 300},
    {"type": "A", "name": "www", "value": "1.2.3.4", "ttl": 300},
    {"type": "MX", "name": "@", "value": "mail.example.com", "priority": 10, "ttl": 300},
    {"type": "TXT", "name": "@", "value": "v=spf1 include:_spf.google.com ~all", "ttl": 300}
  ]
}
```

## VPS Docker Management

For VPS with Docker OS templates:
```bash
# List Docker projects
python3 scripts/hostinger.py docker list <vm_id>

# Deploy from docker-compose.yml URL
python3 scripts/hostinger.py docker deploy <vm_id> <project_name> --url <compose_url>

# Or from local file
python3 scripts/hostinger.py docker deploy <vm_id> <project_name> --file <compose.yml>

# Start/stop/restart project
python3 scripts/hostinger.py docker start <vm_id> <project_name>
python3 scripts/hostinger.py docker stop <vm_id> <project_name>
python3 scripts/hostinger.py docker restart <vm_id> <project_name>

# View logs
python3 scripts/hostinger.py docker logs <vm_id> <project_name>

# Delete project
python3 scripts/hostinger.py docker down <vm_id> <project_name>
```

## VPS Firewall

```bash
# List firewalls
python3 scripts/hostinger.py firewall list

# Create firewall
python3 scripts/hostinger.py firewall create <name>

# Add rule
python3 scripts/hostinger.py firewall add-rule <firewall_id> --protocol tcp --port 443 --source 0.0.0.0/0

# Activate on VM
python3 scripts/hostinger.py firewall activate <firewall_id> <vm_id>
```

## Direct API Access

For operations not covered by the script, use curl:
```bash
TOKEN=$(cat ~/.config/hostinger/token)
curl -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     https://developers.hostinger.com/api/vps/v1/virtual-machines
```

## API Documentation

- Full API reference: https://developers.hostinger.com
- OpenAPI spec: https://github.com/hostinger/api/blob/main/openapi.json
- Python SDK: https://github.com/hostinger/api-python-sdk
- CLI tool: https://github.com/hostinger/api-cli

## Common Workflows

### Deploy a Website

1. Get VPS ID: `python3 scripts/hostinger.py vps list`
2. Update DNS to point to VPS: `python3 scripts/hostinger.py dns update domain.com records.json`
3. SSH to VPS and deploy, OR use Docker: `python3 scripts/hostinger.py docker deploy <vm_id> mysite --file docker-compose.yml`

### Secure a VPS

1. Create firewall: `python3 scripts/hostinger.py firewall create "web-server"`
2. Add rules for SSH, HTTP, HTTPS
3. Activate: `python3 scripts/hostinger.py firewall activate <fw_id> <vm_id>`

### Backup Before Changes

1. Create snapshot: `python3 scripts/hostinger.py vps snapshot-create <vm_id>`
2. Make changes
3. If needed, restore: `python3 scripts/hostinger.py vps snapshot-restore <vm_id>`
