# Systemd Setup for Polymarket Oracle

**Run polymarket-oracle as a professional systemd service**

Auto-start on boot · Auto-restart on crash · Centralized logs · Easy control

---

## 🎯 Why Use Systemd?

**systemd makes your scanner run like a professional service:**

✅ **Auto-starts** when server boots  
✅ **Auto-restarts** if scanner crashes  
✅ **Centralized logs** (journalctl)  
✅ **Easy control** (start/stop/restart)  
✅ **Runs in background** (no SSH needed)  
✅ **Resource limits** (memory, CPU)  

---

## 📋 Prerequisites

- Linux server (Ubuntu, Debian, CentOS, etc.)
- Root/sudo access
- polymarket-oracle already installed and tested

---

## 🚀 Installation

### **Step 1: Create Service File**

```bash
sudo nano /etc/systemd/system/polymarket-oracle.service
```

**Paste this content:**

```ini
[Unit]
Description=Polymarket Oracle - Multi-Strategy Arbitrage Scanner
Documentation=https://github.com/georges91560/polymarket-oracle
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=your_username
Group=your_username
WorkingDirectory=/workspace/skills/polymarket-oracle

# Environment Variables - REPLACE WITH YOUR CREDENTIALS
Environment="POLYMARKET_API_KEY=your_polymarket_api_key_here"
Environment="POLYMARKET_SECRET=your_polymarket_secret_here"
Environment="POLYMARKET_PASSPHRASE=your_polymarket_passphrase_here"
Environment="WALLET_PRIVATE_KEY=your_wallet_private_key_here"
Environment="TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here"
Environment="TELEGRAM_CHAT_ID=your_telegram_chat_id_here"

# Optional - Capital Management
Environment="POLYMARKET_CAPITAL=10000"

# Execution
ExecStart=/usr/bin/python3 /workspace/skills/polymarket-oracle/polymarket_oracle.py

# Restart Policy
Restart=on-failure
RestartSec=15
StartLimitInterval=300
StartLimitBurst=5

# Security
NoNewPrivileges=true
PrivateTmp=true

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=polymarket-oracle

# Resource Limits (optional)
MemoryMax=2G
CPUQuota=200%

[Install]
WantedBy=multi-user.target
```

**Important - Replace these values:**

- `User=your_username` → Your Linux username (e.g., `ubuntu`, `root`)
- `Group=your_username` → Usually same as User
- `WorkingDirectory=/workspace/skills/polymarket-oracle` → Full path to scanner directory
- `POLYMARKET_API_KEY=...` → Your Polymarket API key
- `POLYMARKET_SECRET=...` → Your Polymarket secret
- `POLYMARKET_PASSPHRASE=...` → Your Polymarket passphrase
- `WALLET_PRIVATE_KEY=...` → Your Polygon wallet private key
- `TELEGRAM_BOT_TOKEN=...` → Your Telegram bot token
- `TELEGRAM_CHAT_ID=...` → Your Telegram chat ID
- `POLYMARKET_CAPITAL=10000` → Your trading capital in USD

**Save:** Ctrl+X, Y, Enter

---

### **Step 2: Reload systemd**

```bash
sudo systemctl daemon-reload
```

This tells systemd to read your new service file.

---

### **Step 3: Enable Auto-Start**

```bash
sudo systemctl enable polymarket-oracle
```

**Output:**
```
Created symlink /etc/systemd/system/multi-user.target.wants/polymarket-oracle.service → /etc/systemd/system/polymarket-oracle.service
```

✅ Service will now start automatically when server boots!

---

### **Step 4: Start Service**

```bash
sudo systemctl start polymarket-oracle
```

---

### **Step 5: Verify It's Running**

```bash
sudo systemctl status polymarket-oracle
```

**Expected output:**

```
● polymarket-oracle.service - Polymarket Oracle - Multi-Strategy Arbitrage Scanner
   Loaded: loaded (/etc/systemd/system/polymarket-oracle.service; enabled)
   Active: active (running) since Thu 2026-02-27 14:30:10 UTC; 10s ago
 Main PID: 12346 (python3)
   Memory: 89.1M
   
Feb 27 14:30:10 systemd[1]: Started Polymarket Oracle Scanner.
Feb 27 14:30:11 polymarket-oracle[12346]: [CONFIG] Capital: $10,000
Feb 27 14:30:12 polymarket-oracle[12346]: [GAMMA] Fetched 2,341 markets
Feb 27 14:30:15 polymarket-oracle[12346]: [MARKETS] Categories: {'crypto': 127, 'politics': 543, ...}
Feb 27 14:30:20 polymarket-oracle[12346]: [SCAN] Scanning 2,341 markets with 50 workers...
Feb 27 14:30:35 polymarket-oracle[12346]: [SCAN] Found 27 opportunities
```

**Key indicators:**
- ✅ `Active: active (running)` - Scanner is running!
- ✅ `enabled` - Will start on boot
- ✅ `Main PID: 12346` - Process is alive

---

## 📊 Daily Operations

### **View Live Logs**

```bash
sudo journalctl -u polymarket-oracle -f
```

**Press Ctrl+C to exit**

---

### **View Recent Logs**

```bash
# Last 100 lines
sudo journalctl -u polymarket-oracle -n 100

# Since today
sudo journalctl -u polymarket-oracle --since today

# Since specific time
sudo journalctl -u polymarket-oracle --since "2026-02-27 10:00:00"
```

---

### **Control Service**

```bash
# Stop
sudo systemctl stop polymarket-oracle

# Start
sudo systemctl start polymarket-oracle

# Restart
sudo systemctl restart polymarket-oracle

# Check if running
sudo systemctl is-active polymarket-oracle
# Output: "active" or "inactive"
```

---

### **Disable Auto-Start**

```bash
# Disable (service stays running but won't start on boot)
sudo systemctl disable polymarket-oracle

# Re-enable
sudo systemctl enable polymarket-oracle
```

---

## 🔧 Troubleshooting

### **Service Won't Start**

```bash
# Check for errors
sudo systemctl status polymarket-oracle

# View detailed logs
sudo journalctl -u polymarket-oracle -n 50
```

**Common issues:**

1. **Wrong User/Group**
   ```bash
   # Find your username
   whoami
   
   # Edit service file
   sudo nano /etc/systemd/system/polymarket-oracle.service
   
   # Change User= and Group= to match
   ```

2. **Wrong WorkingDirectory**
   ```bash
   # Find scanner location
   ls -l /workspace/skills/polymarket-oracle/polymarket_oracle.py
   
   # Update WorkingDirectory in service file
   ```

3. **Wrong Python Path**
   ```bash
   # Find Python
   which python3
   # Output: /usr/bin/python3
   
   # Update ExecStart in service file
   ```

4. **Missing Credentials**
   ```bash
   # Check credentials set correctly
   sudo systemctl status polymarket-oracle
   # Look for authentication errors in logs
   ```

---

### **"Failed to fetch markets"**

```bash
# Check Polymarket API status
curl https://gamma-api.polymarket.com/markets?limit=1

# If API is working, check credentials
sudo journalctl -u polymarket-oracle -n 50 | grep ERROR
```

---

### **"Found 0 opportunities"**

**This is normal!** Opportunities are sporadic.

```bash
# Check that scanner is working
sudo journalctl -u polymarket-oracle -n 20

# You should see:
# [GAMMA] Fetched X markets
# [SCAN] Scanning X markets...
# [SCAN] Found 0 opportunities (or more)
```

Opportunities come in waves. Scanner keeps looking!

---

### **Service Keeps Crashing**

```bash
# View crash logs
sudo journalctl -u polymarket-oracle -n 100

# Common causes:
# - Polymarket API rate limits
# - Network issues
# - Insufficient USDC balance (if trading enabled)
# - Python errors in code
```

**Increase restart delay:**

```bash
sudo nano /etc/systemd/system/polymarket-oracle.service

# Change:
RestartSec=30  # Wait 30s before restart (was 15s)

# Reload
sudo systemctl daemon-reload
sudo systemctl restart polymarket-oracle
```

---

## 🔒 Security Tips

### **Protect Credentials**

**Option 1: Use Environment File**

```bash
# Create credentials file
sudo mkdir -p /etc/polymarket-oracle
sudo nano /etc/polymarket-oracle/credentials.env

# Content:
POLYMARKET_API_KEY=your_key
POLYMARKET_SECRET=your_secret
POLYMARKET_PASSPHRASE=your_passphrase
WALLET_PRIVATE_KEY=your_private_key
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_id
POLYMARKET_CAPITAL=10000

# Protect file
sudo chmod 600 /etc/polymarket-oracle/credentials.env
sudo chown root:root /etc/polymarket-oracle/credentials.env
```

**Edit service file:**

```bash
sudo nano /etc/systemd/system/polymarket-oracle.service

# Replace all Environment= lines with:
EnvironmentFile=/etc/polymarket-oracle/credentials.env

# Reload
sudo systemctl daemon-reload
sudo systemctl restart polymarket-oracle
```

---

## 📈 Monitoring

### **Check Resource Usage**

```bash
systemctl status polymarket-oracle | grep -E "Memory|CPU|Tasks"
```

**Output:**
```
   Tasks: 52 (limit: 4915)
   Memory: 89.1M
   CPU: 2.4s
```

Polymarket Oracle uses more workers (50 parallel threads) so higher memory is normal.

---

### **Monitor Opportunities Found**

```bash
# Count opportunities in log
sudo journalctl -u polymarket-oracle --since today | grep "Found.*opportunities" | tail -20
```

---

### **View Opportunities Log File**

```bash
# Real-time opportunities
tail -f /workspace/polymarket_opportunities.jsonl

# Count by strategy
cat /workspace/polymarket_opportunities.jsonl | grep -o '"strategy":"[^"]*"' | sort | uniq -c
```

---

## ✅ Verification Checklist

After installation:

- [ ] `systemctl status polymarket-oracle` shows "active (running)"
- [ ] `systemctl is-enabled polymarket-oracle` shows "enabled"
- [ ] Logs show scanner activity: `journalctl -u polymarket-oracle -n 20`
- [ ] Markets being fetched: Check for "[GAMMA] Fetched X markets"
- [ ] No error messages in logs
- [ ] Telegram alerts working (if opportunities found)
- [ ] Can restart: `sudo systemctl restart polymarket-oracle`
- [ ] Scanner restarts automatically after kill: `sudo kill <PID>`

---

## 🚀 Test Auto-Restart

**Test that scanner restarts automatically on crash:**

```bash
# Get PID
systemctl status polymarket-oracle | grep "Main PID"

# Kill process
sudo kill -9 <PID>

# Wait 15 seconds

# Check status
sudo systemctl status polymarket-oracle
# Should show new PID and "active (running)"
```

✅ If scanner restarted automatically, systemd is working correctly!

---

## 🎯 Performance Tuning

### **Reduce Resource Usage**

If scanner uses too much memory/CPU:

```bash
sudo nano /etc/systemd/system/polymarket-oracle.service

# Reduce limits:
MemoryMax=1G      # Limit to 1GB (was 2G)
CPUQuota=100%     # Limit to 1 CPU core (was 200%)

# In scanner code, reduce workers:
# Edit polymarket_oracle.py line 59:
# MAX_WORKERS = 25  # Instead of 50

# Reload
sudo systemctl daemon-reload
sudo systemctl restart polymarket-oracle
```

---

### **Increase Scan Frequency**

Default is 60 seconds. To scan more frequently:

```bash
# Edit polymarket_oracle.py line 58
nano /workspace/skills/polymarket-oracle/polymarket_oracle.py

# Change:
SCAN_INTERVAL = 30  # 30 seconds instead of 60

# Restart service
sudo systemctl restart polymarket-oracle
```

---

## 🎯 Quick Reference

```bash
# START
sudo systemctl start polymarket-oracle

# STOP
sudo systemctl stop polymarket-oracle

# RESTART
sudo systemctl restart polymarket-oracle

# STATUS
sudo systemctl status polymarket-oracle

# LOGS (real-time)
sudo journalctl -u polymarket-oracle -f

# LOGS (last 100)
sudo journalctl -u polymarket-oracle -n 100

# ENABLE boot auto-start
sudo systemctl enable polymarket-oracle

# DISABLE boot auto-start
sudo systemctl disable polymarket-oracle

# CHECK if running
sudo systemctl is-active polymarket-oracle

# CHECK if enabled
sudo systemctl is-enabled polymarket-oracle
```

---

## 💰 View Opportunities

```bash
# View opportunities log
tail -f /workspace/polymarket_opportunities.jsonl

# Pretty print last opportunity
tail -1 /workspace/polymarket_opportunities.jsonl | python3 -m json.tool

# Count opportunities by strategy
cat /workspace/polymarket_opportunities.jsonl | \
  python3 -c "import sys, json; strategies = [json.loads(l)['strategy'] for l in sys.stdin]; \
  from collections import Counter; print(Counter(strategies))"
```

---

**Your polymarket-oracle now runs 24/7 scanning ALL markets! 🎯💰**
