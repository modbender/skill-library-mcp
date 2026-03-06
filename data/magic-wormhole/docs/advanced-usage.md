# Advanced Magic Wormhole Usage

> Advanced features, customization, and enterprise deployment options

---

## Table of Contents

1. [Custom Code Length](#custom-code-length)
2. [Custom Servers](#custom-servers)
3. [Tor Integration](#tor-integration)
4. [Compression](#compression)
5. [Transit Relay Options](#transit-relay-options)
6. [Self-Hosting](#self-hosting)
7. [Performance Optimization](#performance-optimization)
8. [Security Hardening](#security-hardening)
9. [Integration with Other Tools](#integration-with-other-tools)
10. [Enterprise Deployment](#enterprise-deployment)

---

## Custom Code Length

By default, magic-wormhole uses 16-bit entropy codes (2 words + number = ~65,536 combinations). You can adjust this for different security requirements.

### Longer Codes (More Secure)

```bash
# 3 words (24-bit entropy, ~16 million combinations)
wormhole send --code-length 3 filename

# 4 words (32-bit entropy, ~4 billion combinations)
wormhole send --code-length 4 filename
```

**Use when:**
- Highly sensitive secrets (production credentials)
- Longer codes are acceptable
- Additional security margin desired

### Shorter Codes (Faster, Less Secure)

```bash
# 1 word (4-bit entropy, 16 combinations)
wormhole send --code-length 1 filename
```

**Use when:**
- Non-sensitive data
- Quick, casual transfers
- Security not critical

⚠️ **Warning:** Short codes (1 word) are easily guessable (1 in 16 chance). Never use for sensitive data.

---

## Custom Servers

### Custom Rendezvous Server

```bash
# Use your own rendezvous server
wormhole send --server=ws://your-server:4000/v1 filename

# Receive with custom server
wormhole receive --server=ws://your-server:4000/v1
```

### Custom Transit Relay

```bash
# Use custom transit relay
wormhole send --transit-relay=tcp://your-relay:4001 filename

# Both custom server and relay
wormhole send \
  --server=ws://your-server:4000/v1 \
  --transit-relay=tcp://your-relay:4001 \
  filename
```

### Multiple Transit Relays

```bash
# Specify multiple transit relays for redundancy
wormhole send \
  --transit-relay=tcp://relay1.example.com:4001 \
  --transit-relay=tcp://relay2.example.com:4001 \
  --transit-relay=tcp://relay3.example.com:4001 \
  filename
```

---

## Tor Integration

### Route All Traffic Through Tor

```bash
# Send via Tor (requires Tor service running)
wormhole send --tor filename

# Receive via Tor
wormhole receive --tor
```

### Configuration

**Install Tor:**

```bash
# Debian/Ubuntu
sudo apt install tor

# macOS
brew install tor

# Start Tor service
sudo systemctl start tor
# or
brew services start tor
```

**Verify Tor Connection:**

```bash
# Check Tor is running
sudo systemctl status tor

# Verify socks5 proxy
curl --socks5 127.0.0.1:9050 https://check.torproject.org
```

**Tor Configuration File (`~/.config/wormhole/relayconfig`):**

```ini
[tor]
control-port = 9051
socks-port = 9050
```

---

## Compression

### Zstd Compression

```bash
# Compress before sending (faster for large files)
wormhole send --zstd large-file.tar

# Verify compression stats
wormhole send --zstd --debug large-file.tar | grep "compression"
```

### Custom Compression

```bash
# Compress manually with higher compression
zstd -19 large-file > large-file.zst
wormhole send large-file.zst

# Receive and decompress
wormhole receive
zstd -d large-file.zst -o large-file
```

### Compression Benchmarks

| Compression | Speed | Ratio | Use Case |
|-------------|-------|-------|----------|
| None (default) | Fastest | 1:1 | Small files, text |
| Zstd (default) | Fast | 2:1 - 3:1 | Large files, archives |
| Zstd -3 | Medium | 3:1 - 4:1 | Logs, text files |
| Zstd -19 | Slow | 4:1 - 5:1 | Maximum compression |

---

## Transit Relay Options

### Direct Connection Preference

Magic-wormhole attempts direct connections first, then falls back to transit relays. You can control this behavior.

```bash
# Disable transit relay (direct connection only)
wormhole send --no-transit-relay filename

# Only use specified transit relay
wormhole send --transit-relay=tcp://relay.example.com:4001 filename
```

### Custom Transit Ports

```bash
# Use custom port for transit relay
wormhole send --transit-relay=tcp://relay.example.com:9001 filename
```

### Connection Strategies

Magic-wormhole tries these strategies in order:

1. **Direct LAN**: Both on same network
2. **Direct Internet**: One has public IP
3. **Transit Relay**: Via relay server

### Monitor Connection Type

```bash
# Debug mode shows connection strategy
wormhole send --debug filename 2>&1 | grep "transit"
```

---

## Self-Hosting

### Install Server

```bash
# Install magic-wormhole-server
pip install magic-wormhole-server
```

### Start Server

```bash
# Start both rendezvous and transit servers
wormhole-server start \
  --rendezvous-relay=ws://0.0.0.0:4000/v1 \
  --transit-relay=tcp:0.0.0.0:4001

# Start with custom ports
wormhole-server start \
  --rendezvous-relay=ws://0.0.0.0:9000/v1 \
  --transit-relay=tcp:0.0.0.0:9001
```

### Systemd Service

Create `/etc/systemd/system/wormhole-server.service`:

```ini
[Unit]
Description=Magic Wormhole Server
After=network.target

[Service]
Type=simple
User=wormhole
Group=wormhole
ExecStart=/usr/local/bin/wormhole-server start \
  --rendezvous-relay=ws://0.0.0.0:4000/v1 \
  --transit-relay=tcp:0.0.0.0:4001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
# Create user
sudo useradd --system --home /var/lib/wormhole wormhole

# Enable and start service
sudo systemctl enable wormhole-server
sudo systemctl start wormhole-server

# Check status
sudo systemctl status wormhole-server
```

### Firewall Configuration

```bash
# Open ports for wormhole server
sudo ufw allow 4000/tcp  # Rendezvous (WebSocket)
sudo ufw allow 4001/tcp  # Transit (TCP)

# Check firewall status
sudo ufw status
```

### Docker Deployment

**Dockerfile:**

```dockerfile
FROM python:3.11-slim

RUN pip install magic-wormhole-server

EXPOSE 4000 4001

CMD ["wormhole-server", "start", \
     "--rendezvous-relay=ws://0.0.0.0:4000/v1", \
     "--transit-relay=tcp:0.0.0.0:4001"]
```

**docker-compose.yml:**

```yaml
version: '3.8'
services:
  wormhole-server:
    build: .
    ports:
      - "4000:4000"  # Rendezvous
      - "4001:4001"  # Transit
    restart: unless-stopped
    volumes:
      - wormhole-data:/var/lib/wormhole

volumes:
  wormhole-data:
```

Run:

```bash
docker-compose up -d
docker-compose logs -f
```

### Kubernetes Deployment

**ConfigMap (`configmap.yaml`):**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: wormhole-config
data:
  relay-url: "ws://0.0.0.0:4000/v1"
  transit-url: "tcp://0.0.0.0:4001"
```

**Deployment (`deployment.yaml`):**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wormhole-server
spec:
  replicas: 2
  selector:
    matchLabels:
      app: wormhole-server
  template:
    metadata:
      labels:
        app: wormhole-server
    spec:
      containers:
      - name: wormhole-server
        image: python:3.11-slim
        command: ["wormhole-server", "start"]
        args:
          - "--rendezvous-relay=$(RELAY_URL)"
          - "--transit-relay=$(TRANSIT_URL)"
        env:
          - name: RELAY_URL
            valueFrom:
              configMapKeyRef:
                name: wormhole-config
                key: relay-url
          - name: TRANSIT_URL
            valueFrom:
              configMapKeyRef:
                name: wormhole-config
                key: transit-url
        ports:
          - containerPort: 4000
          - containerPort: 4001
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

**Service (`service.yaml`):**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: wormhole-server
spec:
  selector:
    app: wormhole-server
  ports:
    - name: rendezvous
      port: 4000
      targetPort: 4000
    - name: transit
      port: 4001
      targetPort: 4001
  type: LoadBalancer
```

Deploy:

```bash
kubectl apply -f configmap.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

---

## Performance Optimization

### Parallel Transfers

```bash
# Send multiple files in parallel
for file in file1.txt file2.txt file3.txt; do
    wormhole send "$file" &
done
wait
```

### Batch Script for Multiple Files

```bash
#!/bin/bash
# send-multiple-files.sh

FILES=("file1.txt" "file2.txt" "file3.txt")
CODES=()

for file in "${FILES[@]}"; do
    echo "[INFO] Sending: $file"
    CODE=$(wormhole send "$file" 2>&1 | grep "Wormhole code is:" | cut -d' ' -f4)
    CODES+=("$file:$CODE")
done

echo ""
echo "========================================="
echo "Transfer Complete"
echo "========================================="
for entry in "${CODES[@]}"; do
    IFS=':' read -r FILE CODE <<< "$entry"
    echo "$FILE: $CODE"
done
```

### Connection Pooling

Magic-wormhole automatically manages connections. For high-volume transfers, consider:

```bash
# Increase connection timeout for slow networks
export WORMHOLE_TRANSIT_TIMEOUT=300  # 5 minutes
wormhole send large-file.tar
```

### Memory Optimization

For large file transfers:

```bash
# Use streaming to reduce memory usage
cat large-file.bin | wormhole send --text "$(cat)"

# Or use zstd compression
wormhole send --zstd large-file.tar
```

---

## Security Hardening

### Stronger Codes

```bash
# Use longer codes for production secrets
wormhole send --code-length 4 production-credentials.json
```

### Verification Mode

```bash
# Add extra verification step
wormhole send --verify filename

# Compare fingerprints before accepting
wormhole receive
# Shows fingerprint to verify
```

### Rate Limiting

Self-hosted servers can implement rate limiting:

```bash
# Use nginx as reverse proxy with rate limiting
# /etc/nginx/sites-available/wormhole-relay

limit_req_zone $binary_remote_addr zone=relay:10m rate=10r/s;

server {
    listen 4001;
    limit_req zone=relay burst=20 nodelay;

    location / {
        proxy_pass http://localhost:4001;
    }
}
```

### Logging and Auditing

Configure server logging:

```bash
# Start server with logging
wormhole-server start \
  --rendezvous-relay=ws://0.0.0.0:4000/v1 \
  --transit-relay=tcp:0.0.0.0:4001 \
  --log-level=info \
  --log-file=/var/log/wormhole/server.log
```

Log rotation (`/etc/logrotate.d/wormhole`):

```
/var/log/wormhole/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0640 wormhole wormhole
}
```

### Network Isolation

Run server in isolated network segment:

```bash
# iptables rules
iptables -A INPUT -p tcp --dport 4000 -s 10.0.0.0/8 -j ACCEPT
iptables -A INPUT -p tcp --dport 4001 -s 10.0.0.0/8 -j ACCEPT
iptables -A INPUT -p tcp --dport 4000 -j DROP
iptables -A INPUT -p tcp --dport 4001 -j DROP
```

---

## Integration with Other Tools

### Password Manager Integration

**pass (Git-based):**

```bash
# Send via wormhole
pass api/production-token | wormhole send --text "$(cat)"

# Receive and store
wormhole receive | pass insert -m api/new-token
```

**Bitwarden CLI:**

```bash
# Retrieve and send
bw get password "Production API" | wormhole send --text "$(cat)"

# Receive and store
wormhole receive | bw create item api-token
```

**1Password CLI:**

```bash
# Retrieve and send
op item get "Production API" --fields password | wormhole send --text "$(cat)"

# Receive and store
wormhole receive | op item create --title="New API Token" --password="@stdin"
```

### GPG Encryption

```bash
# Encrypt and send via wormhole
gpg --encrypt --recipient user@example.com secret.txt
wormhole send secret.txt.gpg

# Receive and decrypt
wormhole receive
gpg --decrypt secret.txt.gpg > secret.txt
```

### SSH Integration

```bash
# Send SSH private key
wormhole send ~/.ssh/id_rsa

# Add received key to ssh-agent
wormhole receive | ssh-add -
```

### Git Integration

```bash
# Send commit
git archive HEAD | gzip | wormhole send --text "$(cat)"

# Receive and apply
wormhole receive | gunzip | git apply
```

---

## Enterprise Deployment

### High Availability Setup

**Multiple servers behind load balancer:**

```
┌─────────────┐
│  Load       │
│  Balancer   │
└──────┬──────┘
       │
    ┌──┴──┐
    │     │
┌───▼──┐ ┌─▼────┐
│ WHS1 │ │ WHS2 │  (WHS = Wormhole Server)
└──────┘ └──────┘
```

**HAProxy Configuration:**

```
frontend wormhole-rendezvous
    bind *:4000
    default_backend wormhole-rendezvous-backend

backend wormhole-rendezvous-backend
    balance roundrobin
    server whs1 whs1.example.com:4000 check
    server whs2 whs2.example.com:4000 check

frontend wormhole-transit
    bind *:4001
    default_backend wormhole-transit-backend

backend wormhole-transit-backend
    balance roundrobin
    server whs1 whs1.example.com:4001 check
    server whs2 whs2.example.com:4001 check
```

### Monitoring

**Prometheus Metrics:**

```bash
# Use magic-wormhole with monitoring wrapper
wormhole-monitoring.py start \
  --rendezvous-relay=ws://0.0.0.0:4000/v1 \
  --transit-relay=tcp:0.0.0.0:4001 \
  --metrics-port=9090
```

**Grafana Dashboard:**

Metrics to track:
- Active connections
- Transfer throughput
- Transfer success/failure rate
- Response time
- Server resource usage

### Backup and Recovery

**Backup server configuration:**

```bash
# Backup wormhole server state
tar -czf wormhole-backup-$(date +%Y%m%d).tar.gz /var/lib/wormhole

# Restore
tar -xzf wormhole-backup-20250221.tar.gz -C /
```

**Database backup (if using storage):**

```bash
# Backup PostgreSQL (if storing metadata)
pg_dump wormhole > wormhole-db-$(date +%Y%m%d).sql
```

### Disaster Recovery

**Hot standby server:**

```bash
# Run secondary server in passive mode
wormhole-server start \
  --rendezvous-relay=ws://0.0.0.0:4000/v1 \
  --transit-relay=tcp:0.0.0.0:4001 \
  --standby

# Failover: update DNS to point to standby
```

**DNS failover:**

```
wormhole-relay.example.com. 300 IN A 10.0.0.1
wormhole-relay.example.com. 300 IN A 10.0.0.2
```

---

## Configuration Files

### Client Configuration (`~/.config/wormhole/relayconfig`)

```ini
[relay]
rendezvous-url = ws://relay.example.com:4000/v1
transit-relay = tcp://relay.example.com:4001

[tor]
enabled = false
control-port = 9051
socks-port = 9050

[compression]
enabled = true
level = 3
```

### Server Configuration (`/etc/wormhole/server.conf`)

```ini
[server]
rendezvous-bind = 0.0.0.0:4000
transit-bind = 0.0.0.0:4001

[logging]
level = info
file = /var/log/wormhole/server.log

[security]
code-length-default = 2
max-code-length = 4
rate-limit = 100
```

---

## Troubleshooting Advanced Issues

### Debug Mode

```bash
# Enable full debug logging
wormhole send --debug filename 2>&1 | tee debug.log

# Check for specific issues
grep "ERROR" debug.log
grep "WARNING" debug.log
```

### Network Issues

```bash
# Test WebSocket connection
wscat -c ws://relay.example.com:4000/v1

# Test TCP relay
nc -zv relay.example.com 4001

# Test Tor connection
curl --socks5 127.0.0.1:9050 https://check.torproject.org
```

### Performance Profiling

```bash
# Profile transfer speed
time wormhole send large-file.tar

# Monitor resource usage
/usr/bin/time -v wormhole send large-file.tar
```

### Connection Analysis

```bash
# Show connection strategy
wormhole send --debug filename 2>&1 | grep -A5 "connection"

# Show transit relay usage
wormhole send --debug filename 2>&1 | grep "transit"
```

---

## Best Practices Summary

### For Production

✅ **DO:**
- Use `--code-length 3` or `--code-length 4` for sensitive data
- Self-host servers for regulated environments
- Enable compression for large files
- Monitor server logs and metrics
- Implement rate limiting and DDoS protection
- Use HTTPS/TLS for server connections
- Regular security audits and updates

❌ **DON'T:**
- Use default servers for highly sensitive secrets
- Skip code verification
- Disable logging in production
- Use weak code lengths
- Ignore security warnings
- Run servers without firewall protection

---

## Resources

### Official Documentation

- **Server Documentation**: https://github.com/magic-wormhole/magic-wormhole/blob/master/docs/server.md
- **Protocol Specification**: https://github.com/magic-wormhole/magic-wormhole-protocols
- **Security Analysis**: https://github.com/magic-wormhole/magic-wormhole/blob/master/docs/security.md

### Community

- **GitHub Discussions**: https://github.com/magic-wormhole/magic-wormhole/discussions
- **IRC**: #magic-wormhole on Libera.chat
- **Mailing List**: magic-wormhole@lists.sourceforge.net

---

## Summary

Advanced magic-wormhole usage provides:

✅ **Custom security**: Adjust code length and server configuration
✅ **Performance**: Compression, parallel transfers, connection pooling
✅ **Enterprise**: Self-hosting, HA, monitoring, disaster recovery
✅ **Integration**: Password managers, GPG, SSH, Git
✅ **Hardening**: Rate limiting, logging, network isolation

Use these features to deploy magic-wormhole at scale while maintaining security and performance. 🚀
