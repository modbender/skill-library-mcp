# Cloud Provider Reference

## Hetzner (Best for cost-conscious, Europe-focused)

### Create Server
```bash
# CLI
hcloud server create --name myapp --type cx22 --image ubuntu-24.04 \
  --ssh-key my-key --location nbg1

# With firewall
hcloud firewall create --name web-firewall \
  --rules-file rules.json
hcloud firewall apply-to-resource --type server \
  --server myapp web-firewall
```

### Firewall Rules (rules.json)
```json
[
  {"direction": "in", "protocol": "tcp", "port": "22", "source_ips": ["YOUR_IP/32"]},
  {"direction": "in", "protocol": "tcp", "port": "80", "source_ips": ["0.0.0.0/0"]},
  {"direction": "in", "protocol": "tcp", "port": "443", "source_ips": ["0.0.0.0/0"]}
]
```

### Pricing Reference (2024)
| Type | vCPU | RAM | Storage | Price |
|------|------|-----|---------|-------|
| CX22 | 2 | 4GB | 40GB | €4.51/mo |
| CX32 | 4 | 8GB | 80GB | €8.98/mo |
| CX42 | 8 | 16GB | 160GB | €17.85/mo |
| CAX11 (ARM) | 2 | 4GB | 40GB | €4.51/mo |

---

## AWS (Best for enterprise, global scale)

### Create EC2 Instance
```bash
aws ec2 run-instances \
  --image-id ami-0123456789abcdef0 \
  --instance-type t3.micro \
  --key-name my-key \
  --security-group-ids sg-12345678 \
  --subnet-id subnet-12345678

# Security group
aws ec2 create-security-group --group-name web-sg \
  --description "Web server"
aws ec2 authorize-security-group-ingress --group-id sg-xxx \
  --protocol tcp --port 443 --cidr 0.0.0.0/0
```

### Cost Gotchas
- **Egress:** $0.09/GB after first 100GB
- **EBS:** Charged even when instance stopped
- **NAT Gateway:** $0.045/hour + $0.045/GB processed
- **Load Balancer:** $0.0225/hour minimum

---

## DigitalOcean (Good middle ground)

### Create Droplet
```bash
doctl compute droplet create myapp \
  --size s-1vcpu-1gb \
  --image ubuntu-24-04-x64 \
  --region nyc1 \
  --ssh-keys fingerprint

# Firewall
doctl compute firewall create --name web-fw \
  --inbound-rules "protocol:tcp,ports:22,address:YOUR_IP" \
  --inbound-rules "protocol:tcp,ports:443,address:0.0.0.0/0"
```

### Pricing Reference
| Size | vCPU | RAM | Storage | Price |
|------|------|-----|---------|-------|
| s-1vcpu-1gb | 1 | 1GB | 25GB | $6/mo |
| s-2vcpu-2gb | 2 | 2GB | 50GB | $12/mo |
| s-2vcpu-4gb | 2 | 4GB | 80GB | $24/mo |

---

## Provider Selection Guide

| Priority | Best Choice | Why |
|----------|-------------|-----|
| Lowest cost | Hetzner | 50-70% cheaper than hyperscalers |
| EU data residency | Hetzner | German company, EU datacenters |
| Global presence | AWS/GCP | Regions everywhere |
| Simplicity | DigitalOcean/Render | Less knobs to turn |
| Startup credits | AWS/GCP/Azure | $5K-100K free credits available |
| ARM workloads | Hetzner CAX / AWS Graviton | Better price/performance |
