# Self-Hosted SQ Setup for OpenClaw

**Want to run your own SQ endpoint instead of using SQ Cloud?** Here's how.

---

## Why Self-Host?

- **Free** - No monthly subscription
- **Privacy** - Your data stays on your machine
- **Learning** - Understand how SQ works under the hood
- **Customization** - Modify SQ to fit your needs

---

## Quick Start

### 1. Install SQ

**Option A: From source (Rust)**
```bash
git clone https://github.com/wbic16/SQ.git
cd SQ
cargo build --release
```

**Option B: Docker**
```bash
docker pull wbic16/sq
```

**Option C: Pre-built binary**
Download from: https://github.com/wbic16/SQ/releases

---

### 2. Start SQ Server

**Standalone mode:**
```bash
# From source
./target/release/sq 1337

# Docker
docker run -p 1337:1337 wbic16/sq 1337
```

**Systemd service (Linux):**
```bash
sudo nano /etc/systemd/system/sq.service
```

```ini
[Unit]
Description=SQ Server
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/SQ
ExecStart=/path/to/SQ/target/release/sq 1337
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable sq
sudo systemctl start sq
```

---

### 3. Test Your Endpoint

```bash
# Check version
curl http://localhost:1337/api/v2/version

# Should return:
{"version":"0.5.2","libphext":"0.3.1"}
```

---

### 4. Configure OpenClaw Skill

**Edit `.openclaw/config.yaml`:**

```yaml
skills:
  sq-memory:
    enabled: true
    endpoint: http://localhost:1337  # Your self-hosted endpoint
    api_key: ""                       # Leave empty for self-hosted
    namespace: my-assistant
```

**No API key needed** - self-hosted SQ has no authentication by default.

---

### 5. Test the Skill

```javascript
// Your agent can now use memory:
remember("test/message", "Hello from self-hosted SQ!")
recall("test/message")  // Returns: "Hello from self-hosted SQ!"
```

---

## Production Setup (Optional)

### Add HTTPS with nginx

**Install nginx + certbot:**
```bash
sudo apt install nginx certbot python3-certbot-nginx
```

**Nginx config (`/etc/nginx/sites-available/sq`):**
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:1337;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Get certificate:**
```bash
sudo certbot --nginx -d your-domain.com
```

**Update OpenClaw config:**
```yaml
endpoint: https://your-domain.com
```

---

### Add API Key Authentication (Optional)

**Nginx basic auth:**
```bash
sudo apt install apache2-utils
sudo htpasswd -c /etc/nginx/.htpasswd your-username
```

**Add to nginx config:**
```nginx
location / {
    auth_basic "SQ API";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://127.0.0.1:1337;
}
```

**Update OpenClaw config:**
```yaml
endpoint: https://your-domain.com
api_key: your-password-here  # The htpasswd password
```

The skill will send it as `Authorization: Bearer <api_key>`.

---

## Multi-User Setup

**For multi-agent or multi-user scenarios:**

1. **Run multiple SQ instances** (different ports):
   ```bash
   ./sq 1337  # Agent 1
   ./sq 1338  # Agent 2
   ./sq 1339  # Agent 3
   ```

2. **Configure agents with different endpoints:**
   ```yaml
   # Agent 1
   endpoint: http://localhost:1337
   
   # Agent 2
   endpoint: http://localhost:1338
   ```

3. **Use namespaces for isolation:**
   ```yaml
   # Even on same endpoint, different namespaces prevent collision
   namespace: agent-alice
   namespace: agent-bob
   ```

---

## Data Location

**SQ stores phext files in the working directory:**
```
/path/to/SQ/
  ├── .sq/                # Shared memory segments (daemon mode)
  ├── *.phext             # Your data files
  └── *.phext.json        # Metadata
```

**Backup your data:**
```bash
# Simple backup
cp *.phext /backup/location/

# Or use rsync
rsync -av --include='*.phext' --exclude='*' /path/to/SQ/ /backup/
```

---

## Troubleshooting

### SQ won't start
```bash
# Check if port is in use
sudo lsof -i :1337

# Check SQ logs
journalctl -u sq -f
```

### OpenClaw can't connect
```bash
# Test endpoint directly
curl http://localhost:1337/api/v2/version

# Check firewall
sudo ufw status
sudo ufw allow 1337/tcp
```

### Memory not persisting
SQ auto-saves on every write. If data disappears:
- Check disk space: `df -h`
- Check file permissions: `ls -la *.phext`
- Verify SQ is running: `ps aux | grep sq`

---

## Performance Tuning

**For large datasets:**

1. **Increase system limits:**
   ```bash
   # /etc/security/limits.conf
   * soft nofile 65536
   * hard nofile 65536
   ```

2. **Use SSD storage** for `.phext` files

3. **Monitor resource usage:**
   ```bash
   # Memory
   top -p $(pgrep sq)
   
   # Disk I/O
   iotop -p $(pgrep sq)
   ```

---

## Upgrading SQ

```bash
cd SQ
git pull
cargo build --release
sudo systemctl restart sq
```

**Check version:**
```bash
curl http://localhost:1337/api/v2/version
```

---

## Community & Support

- **Docs:** https://github.com/wbic16/SQ
- **Discord:** https://discord.gg/kGCMM5yQ
- **Issues:** https://github.com/wbic16/SQ/issues

---

## SQ Cloud vs Self-Hosted

| Feature | Self-Hosted | SQ Cloud |
|---------|-------------|----------|
| **Cost** | Free | $50/month |
| **Setup** | DIY | Managed |
| **Storage** | Limited by your disk | 1TB |
| **Backups** | You manage | Automatic |
| **Support** | Community | Email support |
| **Uptime** | Your responsibility | 99.9% SLA |
| **Auth** | Optional | Built-in |

**Choose self-hosted if:**
- Learning/experimenting
- Privacy is critical
- You have DevOps skills

**Choose SQ Cloud if:**
- You want it to just work
- You need reliability
- You value your time over $50/month

---

## Next Steps

1. Start SQ locally
2. Test with curl
3. Configure OpenClaw skill
4. Build agents that remember!

**Questions?** Join Discord or open a GitHub issue.

🔱 **Self-hosting is how phext stays open.**
