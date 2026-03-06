---
name: digitalocean
description: Manage DigitalOcean resources via API — Droplets (create/destroy/resize/power), DNS zones and records, Spaces (object storage), Databases, Firewalls, Load Balancers, Kubernetes, and account/billing info.
---

# DigitalOcean API Skill

Control DigitalOcean infrastructure programmatically: droplets, DNS, databases, storage, networking.

## Authentication

API token required. Get one from: https://cloud.digitalocean.com/account/api/tokens

Store in `~/.config/digitalocean/token` (just the token, no newline):
```bash
mkdir -p ~/.config/digitalocean
echo -n "YOUR_API_TOKEN" > ~/.config/digitalocean/token
chmod 600 ~/.config/digitalocean/token
```

## Quick Reference

### Droplets (VMs)

```bash
# List all droplets
python3 scripts/digitalocean.py droplets list

# Get droplet details
python3 scripts/digitalocean.py droplets get <droplet_id>

# Create droplet
python3 scripts/digitalocean.py droplets create <name> --region nyc1 --size s-1vcpu-1gb --image ubuntu-24-04-x64

# Power actions
python3 scripts/digitalocean.py droplets power-on <droplet_id>
python3 scripts/digitalocean.py droplets power-off <droplet_id>
python3 scripts/digitalocean.py droplets reboot <droplet_id>

# Resize droplet
python3 scripts/digitalocean.py droplets resize <droplet_id> --size s-2vcpu-4gb

# Snapshot
python3 scripts/digitalocean.py droplets snapshot <droplet_id> --name "backup-2024"

# Destroy droplet
python3 scripts/digitalocean.py droplets destroy <droplet_id>
```

### DNS Management

```bash
# List domains
python3 scripts/digitalocean.py dns list

# Get domain records
python3 scripts/digitalocean.py dns records <domain>

# Add record
python3 scripts/digitalocean.py dns add <domain> --type A --name www --data 1.2.3.4 --ttl 300

# Update record
python3 scripts/digitalocean.py dns update <domain> <record_id> --data 5.6.7.8

# Delete record
python3 scripts/digitalocean.py dns delete <domain> <record_id>

# Add domain
python3 scripts/digitalocean.py dns create <domain>
```

### Firewalls

```bash
# List firewalls
python3 scripts/digitalocean.py firewalls list

# Create firewall
python3 scripts/digitalocean.py firewalls create <name> --inbound tcp:22:0.0.0.0/0 --inbound tcp:80:0.0.0.0/0 --inbound tcp:443:0.0.0.0/0

# Add droplet to firewall
python3 scripts/digitalocean.py firewalls add-droplet <firewall_id> <droplet_id>
```

### Spaces (Object Storage)

```bash
# List spaces (requires spaces key)
python3 scripts/digitalocean.py spaces list

# Create space
python3 scripts/digitalocean.py spaces create <name> --region nyc3
```

### Databases

```bash
# List database clusters
python3 scripts/digitalocean.py databases list

# Get database details
python3 scripts/digitalocean.py databases get <db_id>
```

### Account & Billing

```bash
# Account info
python3 scripts/digitalocean.py account

# Balance
python3 scripts/digitalocean.py billing balance

# Billing history
python3 scripts/digitalocean.py billing history
```

### SSH Keys

```bash
# List SSH keys
python3 scripts/digitalocean.py ssh-keys list

# Add SSH key
python3 scripts/digitalocean.py ssh-keys add <name> --key "ssh-ed25519 AAAA..."
```

### Images & Snapshots

```bash
# List available images
python3 scripts/digitalocean.py images list

# List your snapshots
python3 scripts/digitalocean.py images snapshots

# Delete snapshot
python3 scripts/digitalocean.py images delete <image_id>
```

### Regions & Sizes

```bash
# List regions
python3 scripts/digitalocean.py regions

# List droplet sizes
python3 scripts/digitalocean.py sizes
```

## DNS Record Types

Supported record types:
- `A` — IPv4 address
- `AAAA` — IPv6 address
- `CNAME` — Canonical name (alias)
- `MX` — Mail exchange (requires priority)
- `TXT` — Text record
- `NS` — Nameserver
- `SRV` — Service record
- `CAA` — Certificate Authority Authorization

## Common Workflows

### Deploy a New Server

```bash
# 1. Create droplet
python3 scripts/digitalocean.py droplets create myserver --region nyc1 --size s-1vcpu-2gb --image ubuntu-24-04-x64 --ssh-keys <key_id>

# 2. Get IP address
python3 scripts/digitalocean.py droplets get <droplet_id>

# 3. Add DNS record
python3 scripts/digitalocean.py dns add mydomain.com --type A --name @ --data <ip>

# 4. Set up firewall
python3 scripts/digitalocean.py firewalls create web-server --inbound tcp:22:0.0.0.0/0 --inbound tcp:80:0.0.0.0/0 --inbound tcp:443:0.0.0.0/0
python3 scripts/digitalocean.py firewalls add-droplet <fw_id> <droplet_id>
```

### Migrate DNS to DigitalOcean

```bash
# 1. Add domain
python3 scripts/digitalocean.py dns create example.com

# 2. Add records
python3 scripts/digitalocean.py dns add example.com --type A --name @ --data 1.2.3.4
python3 scripts/digitalocean.py dns add example.com --type CNAME --name www --data example.com.

# 3. Update nameservers at registrar to:
#    ns1.digitalocean.com
#    ns2.digitalocean.com
#    ns3.digitalocean.com
```

## Direct API Access

For operations not covered by the script:
```bash
TOKEN=$(cat ~/.config/digitalocean/token)
curl -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     https://api.digitalocean.com/v2/droplets
```

## API Documentation

- Full API reference: https://docs.digitalocean.com/reference/api/
- API v2 base URL: https://api.digitalocean.com/v2/

## Common Droplet Sizes

| Slug | vCPUs | RAM | Disk | Price/mo |
|------|-------|-----|------|----------|
| s-1vcpu-512mb-10gb | 1 | 512MB | 10GB | $4 |
| s-1vcpu-1gb | 1 | 1GB | 25GB | $6 |
| s-1vcpu-2gb | 1 | 2GB | 50GB | $12 |
| s-2vcpu-2gb | 2 | 2GB | 60GB | $18 |
| s-2vcpu-4gb | 2 | 4GB | 80GB | $24 |
| s-4vcpu-8gb | 4 | 8GB | 160GB | $48 |

## Common Regions

| Slug | Location |
|------|----------|
| nyc1, nyc3 | New York |
| sfo3 | San Francisco |
| ams3 | Amsterdam |
| sgp1 | Singapore |
| lon1 | London |
| fra1 | Frankfurt |
| tor1 | Toronto |
| blr1 | Bangalore |
| syd1 | Sydney |
