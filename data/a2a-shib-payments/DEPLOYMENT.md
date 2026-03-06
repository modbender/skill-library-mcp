# SHIB Payment Agent - Deployment Guide

## 🚀 Deployment Options

### Option 1: Local Deployment (Current)
**Status:** ✅ Running on localhost:8003

**Pros:**
- Already working
- No external dependencies
- Full control
- Free

**Cons:**
- Not accessible from internet
- Requires machine to stay on
- No public discovery

**Current Setup:**
```bash
cd /home/marc/clawd/skills/shib-payments
node a2a-agent-full.js
```

---

### Option 2: Expose via Cloudflare Tunnel (Recommended)
**Best for:** Production deployment with free HTTPS

**Steps:**

1. **Install Cloudflare Tunnel:**
```bash
# Already have cloudflared installed
cloudflared tunnel login
```

2. **Create Tunnel:**
```bash
cloudflared tunnel create shib-payment-agent
```

3. **Configure Tunnel:**
Create `/home/marc/.cloudflared/config.yml`:
```yaml
tunnel: <tunnel-id>
credentials-file: /home/marc/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: shib-agent.your-domain.com
    service: http://localhost:8003
  - service: http_status:404
```

4. **Run Tunnel:**
```bash
cloudflared tunnel run shib-payment-agent
```

5. **Set DNS:**
```bash
cloudflared tunnel route dns shib-payment-agent shib-agent.your-domain.com
```

**Result:** Agent accessible at `https://shib-agent.your-domain.com`

**Pros:**
- Free HTTPS
- No port forwarding
- DDoS protection
- Automatic reconnection
- No firewall changes

**Cons:**
- Requires Cloudflare account
- Need domain name

---

### Option 3: Systemd Service (Auto-Start)
**Best for:** Always-on local deployment

**Create Service File:**
`/etc/systemd/system/shib-payment-agent.service`
```ini
[Unit]
Description=SHIB Payment Agent (Full-Featured)
After=network.target

[Service]
Type=simple
User=marc
WorkingDirectory=/home/marc/clawd/skills/shib-payments
ExecStart=/usr/bin/node a2a-agent-full.js
Restart=always
RestartSec=10
Environment=NODE_ENV=production

# Security
PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

**Install & Start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable shib-payment-agent
sudo systemctl start shib-payment-agent
sudo systemctl status shib-payment-agent
```

**View Logs:**
```bash
sudo journalctl -u shib-payment-agent -f
```

---

### Option 4: Docker Container
**Best for:** Portable deployment

**Dockerfile:**
```dockerfile
FROM node:22-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm install --production

# Copy source
COPY *.js ./
COPY *.json ./
COPY *.md ./

# Create data directories
RUN mkdir -p audit-logs

# Environment
ENV NODE_ENV=production
ENV PORT=8003

EXPOSE 8003

CMD ["node", "a2a-agent-full.js"]
```

**Build & Run:**
```bash
cd /home/marc/clawd/skills/shib-payments
docker build -t shib-payment-agent .
docker run -d \
  --name shib-agent \
  -p 8003:8003 \
  -v $(pwd)/.env.local:/app/.env.local \
  -v $(pwd)/audit-logs:/app/audit-logs \
  -v $(pwd)/escrow-state.json:/app/escrow-state.json \
  -v $(pwd)/negotiation-state.json:/app/negotiation-state.json \
  -v $(pwd)/reputation-state.json:/app/reputation-state.json \
  --restart unless-stopped \
  shib-payment-agent
```

---

### Option 5: VPS Deployment
**Best for:** Production with full control

**Recommended Providers:**
- **DigitalOcean:** $6/month droplet
- **Linode:** $5/month nanode
- **Hetzner:** €4.5/month CX11
- **Oracle Cloud:** Free tier (ARM instance)

**Setup:**
```bash
# 1. Create VPS and SSH in
ssh user@your-vps-ip

# 2. Install dependencies
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs git

# 3. Clone repo
git clone git@github.com:marcus20232023/clawd.git
cd clawd/skills/shib-payments

# 4. Configure
cp .env.example .env.local
nano .env.local  # Add your private key

# 5. Install dependencies
npm install

# 6. Set up systemd service (see Option 3)

# 7. Configure firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# 8. Set up reverse proxy (nginx/Caddy)
```

**Nginx Config:**
```nginx
server {
    listen 80;
    server_name shib-agent.your-domain.com;
    
    location / {
        proxy_pass http://localhost:8003;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

**Then add HTTPS with Let's Encrypt:**
```bash
sudo certbot --nginx -d shib-agent.your-domain.com
```

---

## 🔒 Security Checklist

### Before Public Deployment:

- [ ] Change all default API keys in `auth-config.json`
- [ ] Set strong rate limits (adjust `rate-limiter.js` config)
- [ ] Enable HTTPS (Cloudflare/Let's Encrypt)
- [ ] Set up firewall rules (only allow necessary ports)
- [ ] Configure backup for state files
- [ ] Set up monitoring & alerting
- [ ] Review audit logs regularly
- [ ] Implement log rotation
- [ ] Secure private keys (use hardware wallet for production)
- [ ] Test disaster recovery
- [ ] Set up automated backups

### Environment Variables:
```bash
# .env.local (chmod 600)
POLYGON_WALLET_ADDRESS=0x...
POLYGON_PRIVATE_KEY=0x...
NODE_ENV=production
PORT=8003
LOG_LEVEL=info
```

---

## 📊 Monitoring Setup

### Prometheus Metrics (Future Enhancement)
```javascript
// Add to agent:
const prometheus = require('prom-client');
const register = new prometheus.Registry();

// Metrics
const paymentsCounter = new prometheus.Counter({
  name: 'shib_payments_total',
  help: 'Total SHIB payments'
});

const escrowsGauge = new prometheus.Gauge({
  name: 'escrows_active',
  help: 'Active escrows count'
});
```

### Grafana Dashboard
- Active escrows
- Payment volume
- Reputation scores
- Rate limit hits
- Error rates
- Gas costs

---

## 🔄 Backup Strategy

**Critical Files:**
```bash
# State files (backup every hour)
escrow-state.json
negotiation-state.json
reputation-state.json
auth-config.json

# Audit logs (backup daily)
audit-logs/*.jsonl

# Wallet (backup once, store securely)
.env.local
```

**Automated Backup Script:**
```bash
#!/bin/bash
# backup.sh
BACKUP_DIR=/home/marc/backups/shib-agent
DATE=$(date +%Y%m%d-%H%M%S)

mkdir -p $BACKUP_DIR

# Backup state files
tar -czf $BACKUP_DIR/state-$DATE.tar.gz \
  escrow-state.json \
  negotiation-state.json \
  reputation-state.json

# Backup audit logs
tar -czf $BACKUP_DIR/audit-$DATE.tar.gz audit-logs/

# Keep only last 7 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

**Cron:**
```bash
# Backup every hour
0 * * * * cd /home/marc/clawd/skills/shib-payments && ./backup.sh
```

---

## 🧪 Testing Deployment

### Health Check Endpoint
Add to agent:
```javascript
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    uptime: process.uptime(),
    timestamp: Date.now(),
    version: '2.0.0'
  });
});
```

### Test Checklist:
```bash
# 1. Agent card accessible
curl https://your-domain.com/.well-known/agent-card.json

# 2. JSON-RPC working
curl -X POST https://your-domain.com/a2a/jsonrpc \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"message/send",...}'

# 3. SSL certificate valid
curl -vI https://your-domain.com 2>&1 | grep "SSL certificate"

# 4. Rate limiting working
for i in {1..11}; do curl https://your-domain.com/...; done

# 5. Audit logs writing
tail -f audit-logs/audit-*.jsonl
```

---

## 🚀 Recommended: Cloudflare Tunnel + Systemd

**Best Production Setup:**

1. **Systemd service** for auto-start
2. **Cloudflare Tunnel** for HTTPS access
3. **Automated backups** via cron
4. **Monitoring** via audit logs

**Full Setup Script:**
```bash
#!/bin/bash
# deploy.sh

# 1. Install service
sudo cp shib-payment-agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable shib-payment-agent

# 2. Set up Cloudflare Tunnel
cloudflared tunnel create shib-agent
# (Configure DNS and config.yml manually)

# 3. Set up backups
chmod +x backup.sh
(crontab -l 2>/dev/null; echo "0 * * * * cd $(pwd) && ./backup.sh") | crontab -

# 4. Start everything
sudo systemctl start shib-payment-agent
cloudflared tunnel run shib-agent &

echo "✅ Deployment complete!"
echo "Agent running at: https://shib-agent.your-domain.com"
```

---

## 📝 Post-Deployment

### Update Registry
Add your agent to public registry:
```json
{
  "id": "shib-payment-agent-prod",
  "name": "SHIB Payment Agent (Production)",
  "agentCardUrl": "https://shib-agent.your-domain.com/.well-known/agent-card.json",
  "endpoints": {
    "jsonrpc": "https://shib-agent.your-domain.com/a2a/jsonrpc"
  },
  "capabilities": ["payments", "escrow", "negotiation", "reputation"]
}
```

### Announce
- Post on social media
- Share on agent marketplaces
- Add to A2A registry
- Document API for developers

---

## 💰 Cost Estimate

**Monthly Costs:**
- **Local (current):** $0 (electricity only)
- **Cloudflare Tunnel:** $0 (free tier)
- **VPS (DigitalOcean):** $6
- **Domain:** $12/year (~$1/month)
- **Total minimal:** $1-7/month

**Transaction Costs:**
- Gas per payment: ~$0.003
- 1,000 payments/month: $3
- Still 3,000x cheaper than traditional!

---

## ✅ Quick Start (Local Production)

```bash
# 1. Go to agent directory
cd /home/marc/clawd/skills/shib-payments

# 2. Install as systemd service
sudo cp shib-payment-agent.service /etc/systemd/system/
sudo systemctl enable shib-payment-agent
sudo systemctl start shib-payment-agent

# 3. Check status
sudo systemctl status shib-payment-agent

# 4. View logs
sudo journalctl -u shib-payment-agent -f
```

**Done!** Agent auto-starts on boot.

Want internet access? Add Cloudflare Tunnel (see Option 2).

---

**Current Status:** Running on localhost:8003  
**Ready for:** Local production (systemd) or public deployment (Cloudflare)  
**Recommendation:** Start with systemd, add Cloudflare Tunnel when ready for public
