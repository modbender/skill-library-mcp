# Gateway Errors

Complete guide to diagnosing and fixing OpenClaw gateway networking issues.

## Error Types

### 502 Bad Gateway

**Symptoms:**
- HTTP 502 status from gateway
- "Bad gateway" or "upstream error" messages
- Channels cannot connect to gateway
- Intermittent connection failures

**Common Causes:**
- Gateway service crashed or not running
- Upstream AI provider unreachable
- Network connectivity issues
- Reverse proxy misconfiguration

**Diagnostic Ladder:**
```bash
# Step 1: Check if gateway is running
openclaw status

# Step 2: Test gateway port
curl http://localhost:18789/health

# Step 3: Check upstream connectivity
curl -I https://api.openai.com/v1/models

# Step 4: Review gateway logs
openclaw logs --level error --last 10m

# Step 5: Test with verbose output
openclaw start --verbose --foreground
```

**Fix:**
```bash
# If gateway not running
openclaw start

# If gateway crashed, restart
openclaw restart

# If upstream unreachable, check network
ping api.openai.com
traceroute api.openai.com

# If reverse proxy issue, check config
nginx -t  # For nginx
apache2ctl configtest  # For Apache

# If persistent, rebuild
openclaw rebuild
```

**Auto-Fix Available:** Partial (can restart gateway)

---

### EADDRINUSE

**Symptoms:**
- Error: "Address already in use"
- "Port 18789 is already in use"
- Gateway fails to start
- Cannot bind to port

**Common Causes:**
- Previous OpenClaw instance still running
- Another service using port 18789
- Zombie process holding port
- Docker container port conflict

**Diagnostic Commands:**
```bash
# Find what's using port 18789
lsof -i :18789              # Linux/macOS
netstat -ano | findstr 18789  # Windows

# Check for openclaw processes
ps aux | grep openclaw

# Check Docker containers
docker ps | grep 18789
```

**Fix:**
```bash
# Option 1: Kill process using port
kill $(lsof -t -i:18789)

# Option 2: Use different port
openclaw config set gateway.port 18790
openclaw restart

# Option 3: Stop all OpenClaw instances
openclaw stop --all
killall openclaw
openclaw start

# Option 4: Stop Docker containers
docker stop $(docker ps -q --filter "expose=18789")
```

**Auto-Fix Available:** Yes
```bash
python3 scripts/error-fixer.py --error EADDRINUSE --auto-fix
```

---

### ECONNREFUSED

**Symptoms:**
- "Connection refused" error
- Cannot connect to localhost:18789
- Gateway appears running but unreachable
- Channel connections fail

**Common Causes:**
- Gateway bound to wrong interface (127.0.0.1 vs 0.0.0.0)
- Firewall blocking port 18789
- Gateway listening but not accepting connections
- SELinux/AppArmor blocking connections

**Diagnostic Commands:**
```bash
# Check gateway binding
netstat -tulpn | grep 18789
ss -tulpn | grep 18789

# Test local connection
curl http://127.0.0.1:18789/health
curl http://localhost:18789/health
curl http://0.0.0.0:18789/health

# Check firewall
sudo ufw status          # Linux
sudo firewall-cmd --list-all  # RHEL/CentOS

# Check if process listening
openclaw status --detailed
```

**Fix:**
```bash
# Bind to all interfaces
openclaw config set gateway.host "0.0.0.0"
openclaw restart

# Allow firewall
sudo ufw allow 18789/tcp          # Linux
sudo firewall-cmd --add-port=18789/tcp --permanent  # RHEL

# Disable SELinux temporarily (testing only)
sudo setenforce 0

# Check logs for binding errors
openclaw logs --filter="bind" --last 5m
```

**Auto-Fix Available:** Partial

---

### NETWORK_TIMEOUT

**Symptoms:**
- Requests time out waiting for response
- "Request timeout" errors
- Gateway slow to respond
- Channels report timeout

**Common Causes:**
- Slow AI provider response
- Network congestion
- Timeout setting too low
- Gateway under heavy load

**Diagnostic Commands:**
```bash
# Measure response times
time curl http://localhost:18789/health

# Check gateway load
openclaw status --metrics

# Test provider latency
openclaw benchmark --provider openai

# Monitor active requests
openclaw requests --status pending
```

**Fix:**
```bash
# Increase timeout
openclaw config set gateway.timeout.requestMs 60000
openclaw config set gateway.timeout.responseMs 120000

# Increase AI provider timeout
openclaw config set ai.timeout.requestMs 90000

# Enable request queuing
openclaw config set gateway.queueing.enabled true

# Reduce concurrent load
openclaw config set gateway.concurrency.max 50

# Scale gateway (if using cluster)
openclaw scale --instances 3
```

**Auto-Fix Available:** No (requires tuning)

---

### DNS_RESOLUTION

**Symptoms:**
- "Cannot resolve hostname" errors
- "getaddrinfo ENOTFOUND" messages
- Gateway cannot reach AI providers
- Network requests fail with DNS errors

**Common Causes:**
- DNS server unreachable
- /etc/resolv.conf misconfigured
- Corporate firewall blocking DNS
- VPN interfering with DNS

**Diagnostic Commands:**
```bash
# Test DNS resolution
nslookup api.openai.com
dig api.openai.com
host api.anthropic.com

# Check DNS config
cat /etc/resolv.conf

# Test with different DNS
nslookup api.openai.com 8.8.8.8
```

**Fix:**
```bash
# Use public DNS temporarily
openclaw config set gateway.dns.servers '["8.8.8.8", "1.1.1.1"]'

# Fix system DNS
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# Use IP addresses (emergency only)
openclaw config set ai.openai.endpoint "https://13.107.21.200/v1"

# Check VPN/proxy
openclaw config set gateway.proxy.enabled false

# Flush DNS cache
sudo systemd-resolve --flush-caches  # Linux
sudo dscacheutil -flushcache         # macOS
ipconfig /flushdns                   # Windows
```

**Auto-Fix Available:** No (system-level issue)

---

## Gateway Health Monitoring

### Health Check Endpoint
```bash
# Basic health
curl http://localhost:18789/health

# Detailed status
curl http://localhost:18789/health/detailed

# Provider connectivity
curl http://localhost:18789/health/providers

# Expected response
{
  "status": "healthy",
  "uptime": 3600,
  "providers": {
    "openai": "connected",
    "anthropic": "connected"
  },
  "channels": {
    "whatsapp": "active",
    "telegram": "active"
  }
}
```

### Continuous Monitoring
```bash
# Watch health status
watch -n 5 'curl -s http://localhost:18789/health | jq'

# Monitor logs
openclaw logs --follow --level warn

# Set up alerts
openclaw alerts add --metric gateway_health --action restart
```

## Network Diagnostic Workflow

```
Gateway won't start?
├─ Check port 18789 in use? → Kill process or change port
├─ Check gateway process running? → Start gateway
└─ Check logs for errors → Review and fix

Gateway unreachable?
├─ Test localhost:18789/health → Fix binding/firewall
├─ Check if listening on 0.0.0.0 → Update config
└─ Check firewall/SELinux → Allow port

Requests timing out?
├─ Check gateway load → Scale or reduce concurrency
├─ Test provider latency → Increase timeout
└─ Monitor active requests → Enable queuing

Cannot reach providers?
├─ Test DNS resolution → Fix DNS config
├─ Check network connectivity → Fix routing/proxy
└─ Verify API endpoints → Update endpoints
```

## Performance Tuning

```yaml
gateway:
  port: 18789
  host: "0.0.0.0"

  timeout:
    requestMs: 60000
    responseMs: 120000
    keepAliveMs: 5000

  concurrency:
    max: 100
    perChannel: 20

  queueing:
    enabled: true
    maxSize: 1000

  monitoring:
    healthCheck: true
    metricsInterval: 10000
```

## Related Files

- [Error Catalog](error-catalog.md) - All error types
- [Channel Errors](channel-errors.md) - Channel-specific issues
- [Diagnostic Commands](diagnostic-commands.md) - CLI reference
- [Installation Errors](installation-errors.md) - Setup issues
