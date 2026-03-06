# Configuration Guide

**Polymarket Oracle v1.0.0 - Complete Setup**

---

## Prerequisites

- Python 3.7+ (standard library only)
- Polygon wallet with USDC
- Polymarket account
- Telegram bot (optional but recommended)
- Capital: $1K-$50K+

---

## Step 1: Polymarket Account Setup

### **Create Account**

1. Go to https://polymarket.com
2. Click "Connect Wallet"
3. Use MetaMask, WalletConnect, or email
4. Complete onboarding

---

### **Fund Wallet with USDC**

**On Polygon network:**

1. **Buy USDC** on exchange (Coinbase, Binance, etc.)
2. **Bridge to Polygon:**
   - Use https://wallet.polygon.technology/polygon/bridge
   - Or use exchange withdrawal directly to Polygon
3. **Send to your wallet address**

**Amounts:**
- Minimum: $1,000 (limited opportunities)
- Recommended: $5,000-$10,000 (balanced)
- Professional: $50,000+ (full strategies)

---

## Step 2: API Credentials

### **Generate Polymarket API Keys**

**Method 1: Using py-clob-client (Recommended)**

```bash
# Install official client
pip install py-clob-client

# Generate credentials
python3 << 'EOF'
from py_clob_client.client import ClobClient

# Initialize client
client = ClobClient(
    host="https://clob.polymarket.com",
    key="YOUR_WALLET_PRIVATE_KEY",  # From MetaMask
    chain_id=137  # Polygon
)

# Create API credentials
creds = client.create_api_key()

print("=== SAVE THESE CREDENTIALS ===")
print(f"API Key: {creds['apiKey']}")
print(f"Secret: {creds['secret']}")
print(f"Passphrase: {creds['passphrase']}")
print("===============================")
EOF
```

---

**Method 2: Via Polymarket Dashboard**

1. Go to https://polymarket.com/settings/api
2. Click "Create API Key"
3. Save credentials (shown once!)

---


## ⚠️ CRITICAL SECURITY - WALLET PRIVATE KEY

**IMPORTANT:** Your wallet private key is needed **ONLY ONCE** to create Polymarket API credentials.

### **🔒 DO THIS (Secure Setup):**

#### **Step 1: Generate API Keys Locally (One-Time)**

```bash
# On your LOCAL MACHINE (not server!)
pip install py-clob-client

python3 << 'EOF'
from py_clob_client.client import ClobClient

client = ClobClient(
    host="https://clob.polymarket.com",
    key="YOUR_WALLET_PRIVATE_KEY",  # Used ONCE here
    chain_id=137
)

creds = client.create_api_key()

print("=== SAVE THESE - YOU'LL NEED THEM ===")
print(f"API Key: {creds['apiKey']}")
print(f"Secret: {creds['secret']}")
print(f"Passphrase: {creds['passphrase']}")
print("======================================")
EOF

# Your private key was used ONCE above.
# You will NOT need it again for the bot!
```

---

#### **Step 2: Store API Keys Securely on Server**

```bash
# On your SERVER (where bot runs)
# Create secure credentials file
sudo mkdir -p /etc/polymarket-oracle
sudo nano /etc/polymarket-oracle/credentials.env

# Paste ONLY these (NO private key!):
POLYMARKET_API_KEY=your_api_key_from_step1
POLYMARKET_SECRET=your_secret_from_step1
POLYMARKET_PASSPHRASE=your_passphrase_from_step1
TELEGRAM_BOT_TOKEN=your_telegram_token  # Optional
TELEGRAM_CHAT_ID=your_chat_id          # Optional
POLYMARKET_CAPITAL=10000

# Secure the file
sudo chmod 600 /etc/polymarket-oracle/credentials.env
sudo chown root:root /etc/polymarket-oracle/credentials.env
```

---

#### **Step 3: Use Credentials File**

```bash
# Load credentials before running bot
source /etc/polymarket-oracle/credentials.env

# Or add to your systemd service (see SYSTEMD_SETUP.md):
EnvironmentFile=/etc/polymarket-oracle/credentials.env
```

---

### **❌ DO NOT DO THIS (Insecure):**

```bash
# ❌ NEVER store private key on server
❌ export WALLET_PRIVATE_KEY=... in ~/.bashrc
❌ Put WALLET_PRIVATE_KEY in systemd service file
❌ Put WALLET_PRIVATE_KEY in /etc/polymarket-oracle/credentials.env
❌ Commit WALLET_PRIVATE_KEY to git
❌ Store private key anywhere long-term

# ❌ NEVER use .env file in project directory
❌ cat > .env << 'EOF'
❌ WALLET_PRIVATE_KEY="..."
❌ EOF
```

---

### **🎯 Why This Matters**

**Private key gives FULL CONTROL of your wallet:**
- Can withdraw all funds
- Can sign any transaction
- Cannot be revoked

**API keys give LIMITED CONTROL:**
- Can only trade on Polymarket
- Cannot withdraw funds
- Can be revoked anytime

**Your private key should NEVER be on the server where the bot runs!**

**The bot code uses ONLY API credentials at runtime.**

chmod 600 .env
```

---

## Step 3: Telegram Setup (Optional)

### **Create Bot**

1. Open Telegram
2. Search: `@BotFather`
3. Send: `/newbot`
4. Name: `Polymarket Oracle`
5. Username: `your_polymarket_oracle_bot`
6. Save **BOT_TOKEN**

---

### **Get Chat ID**

```bash
# Method 1: Send message then check
# 1. Send any message to your bot
# 2. Visit (replace TOKEN):
https://api.telegram.org/botYOUR_TOKEN/getUpdates

# 3. Find "chat":{"id":123456789}

# Method 2: Use @userinfobot
# Search @userinfobot in Telegram
# Start chat → bot shows your ID
```

---

### **Test Telegram**

```bash
python3 << 'EOF'
import urllib.request, json, os

token = "YOUR_BOT_TOKEN"
chat_id = "YOUR_CHAT_ID"

url = f"https://api.telegram.org/bot{token}/sendMessage"
data = json.dumps({
    "chat_id": chat_id,
    "text": "✅ Polymarket Oracle - Telegram configured!"
}).encode()

req = urllib.request.Request(url, data, {'Content-Type': 'application/json'})
urllib.request.urlopen(req)
print("✅ Test message sent")
EOF
```

---

## Step 4: Environment Variables

### **Set Variables**

```bash
# Polymarket credentials
export POLYMARKET_API_KEY="your_api_key"
export POLYMARKET_SECRET="your_secret"
export POLYMARKET_PASSPHRASE="your_passphrase"
export WALLET_PRIVATE_KEY="0x..."

# Telegram (optional)
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"

# Capital allocation
export POLYMARKET_CAPITAL="10000"  # $10K default
```

---

### **Make Permanent**

```bash
# Add to ~/.bashrc or ~/.zshrc
cat >> ~/.bashrc << 'EOF'
# Polymarket Oracle
export POLYMARKET_API_KEY="..."
export POLYMARKET_SECRET="..."
export POLYMARKET_PASSPHRASE="..."
export WALLET_PRIVATE_KEY="..."
export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID="..."
export POLYMARKET_CAPITAL="10000"
EOF

# Reload
source ~/.bashrc
```

---

## Step 5: Installation

### **Clone Repository**

```bash
git clone https://github.com/georges91560/polymarket-oracle.git
cd polymarket-oracle
```

---

### **Verify**

```bash
# Check Python version
python3 --version
# Should be 3.7+

# Check script
ls -lh polymarket_oracle.py
# Should exist

# Permissions
chmod +x polymarket_oracle.py
```

---

## Step 6: Test Run

### **Simulation Mode (No API)**

```bash
# Run without API credentials
python3 polymarket_oracle.py
```

**Expected:**
```
============================================================
POLYMARKET ORACLE - Multi-Strategy Scanner
============================================================
[CONFIG] Capital: $10,000
[CONFIG] Max per market: $1,000
[WARNING] No API credentials - simulation mode only
[GAMMA] Fetched 2,341 markets
[MARKETS] Categories: {'crypto': 127, 'politics': 543, ...}
[SCAN] Scanning 2,341 markets with 50 workers...
[SCAN] Found 12 opportunities
```

**Simulation mode:**
- ✅ Scans all markets
- ✅ Detects opportunities
- ✅ Logs to files
- ✅ Sends Telegram alerts
- ❌ Cannot place real orders

---

### **Live Mode (With API)**

```bash
# Set credentials first
export POLYMARKET_API_KEY="..."
export POLYMARKET_SECRET="..."
export POLYMARKET_PASSPHRASE="..."

# Run
python3 polymarket_oracle.py
```

**Expected:**
```
[CONFIG] Capital: $10,000
[CONFIG] Max per market: $1,000
✅ API credentials configured
```

**Live mode:**
- ✅ Can place real orders
- ✅ Executes trades
- ⚠️ Uses real money!

---

## Configuration Options

### **Capital Settings**

```python
# In polymarket_oracle.py or via env vars

# Total capital
TOTAL_CAPITAL = 10000  # $10K

# Max per market (1-10% of capital)
MAX_POSITION_PER_MARKET = 1000  # $1K

# Strategy-specific
parity_max = 500  # $500 for parity arb
tail_end_max = 5000  # $5K for tail-end (safest)
```

---

### **Strategy Thresholds**

```python
# Minimum profit requirements

MIN_PARITY_PROFIT = 0.02  # 2% minimum
# Lower = more opportunities, less profit each
# Higher = fewer opportunities, more profit each

MIN_TAIL_END_CERTAINTY = 0.95  # 95% minimum
# Higher = safer but fewer opportunities
# Lower = more opportunities but riskier

MIN_MARKET_MAKING_SPREAD = 0.025  # 2.5%
# Account for fees (2% winner fee on some markets)
```

---

### **Scan Settings**

```python
SCAN_INTERVAL = 60  # Seconds between scans
# Lower = more frequent scans, higher API usage
# Higher = less frequent, might miss fast opportunities

MAX_WORKERS = 50  # Parallel scanning threads
# More = faster scanning but higher CPU usage
# Less = slower but lighter on resources
```

---

## Risk Configuration

### **Conservative (Safest)**

```python
# Focus on guaranteed/near-guaranteed profits
TOTAL_CAPITAL = 5000
MAX_POSITION_PER_MARKET = 500

MIN_PARITY_PROFIT = 0.025  # 2.5%
MIN_TAIL_END_CERTAINTY = 0.97  # 97%

# Enable only safest strategies
# In scanner, comment out risky strategies
```

**Target:** 8-12% monthly, 95%+ win rate

---

### **Balanced (Recommended)**

```python
# Mix of safe + moderate risk
TOTAL_CAPITAL = 10000
MAX_POSITION_PER_MARKET = 1000

MIN_PARITY_PROFIT = 0.02  # 2%
MIN_TAIL_END_CERTAINTY = 0.95  # 95%

# Enable parity + tail-end + market making
```

**Target:** 12-20% monthly, 88-92% win rate

---

### **Aggressive (High Risk)**

```python
# All strategies, lower thresholds
TOTAL_CAPITAL = 50000
MAX_POSITION_PER_MARKET = 5000

MIN_PARITY_PROFIT = 0.015  # 1.5%
MIN_TAIL_END_CERTAINTY = 0.90  # 90%

# Enable all 6 strategies
```

**Target:** 15-30% monthly, 80-85% win rate

---

## Monitoring

### **Real-Time Logs**

```bash
# Terminal output
python3 polymarket_oracle.py

# Or run in background
nohup python3 polymarket_oracle.py > oracle.log 2>&1 &

# Watch logs
tail -f oracle.log
```

---

### **Opportunities Detected**

```bash
# View all detected opportunities
tail -f /workspace/polymarket_opportunities.jsonl

# Count by strategy
cat /workspace/polymarket_opportunities.jsonl | jq '.strategy' | sort | uniq -c
```

---

### **Trades Executed**

```bash
# View trades
tail -f /workspace/polymarket_trades.jsonl

# Calculate total profit
cat /workspace/polymarket_trades.jsonl | jq '.profit' | awk '{sum+=$1} END {print sum}'
```

---

## Troubleshooting

### **"Failed to fetch markets"**

**Cause:** Gamma API timeout or rate limit

**Fix:**
```bash
# Check API status
curl https://gamma-api.polymarket.com/markets?limit=1

# If working, increase timeout or retry
```

---

### **"API error: Unauthorized"**

**Cause:** Wrong credentials or expired

**Fix:**
```bash
# Regenerate API credentials
# Update environment variables
# Restart bot
```

---

### **"Order rejected: Insufficient balance"**

**Cause:** Not enough USDC

**Fix:**
```bash
# Check balance on Polygon
# Add more USDC to wallet
# Reduce MAX_POSITION_PER_MARKET
```

---

### **"Found 0 opportunities"**

**Normal** - Opportunities are sporadic

**Reasons:**
- Efficient markets (bots already took arb)
- Strict thresholds
- Low activity period

**Actions:**
- Lower MIN thresholds
- Wait longer (opportunities come in waves)
- Check if specific categories are active
```

---

## Running as Service

### **Systemd Service (Linux)**

```bash
sudo nano /etc/systemd/system/polymarket-oracle.service
```

**Content:**
```ini
[Unit]
Description=Polymarket Oracle Scanner
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/polymarket-oracle
Environment="POLYMARKET_API_KEY=..."
Environment="POLYMARKET_SECRET=..."
Environment="POLYMARKET_PASSPHRASE=..."
Environment="WALLET_PRIVATE_KEY=..."
Environment="TELEGRAM_BOT_TOKEN=..."
Environment="TELEGRAM_CHAT_ID=..."
Environment="POLYMARKET_CAPITAL=10000"
ExecStart=/usr/bin/python3 /path/to/polymarket-oracle/polymarket_oracle.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable polymarket-oracle
sudo systemctl start polymarket-oracle
sudo systemctl status polymarket-oracle
```

---

## Best Practices

### ✅ **DO:**

- Start with small capital ($1K-$5K)
- Run in simulation mode first
- Monitor daily for first week
- Review opportunities before live trading
- Use Telegram alerts
- Keep API keys secure
- Check Polymarket terms of service

### ❌ **DON'T:**

- Trade without understanding strategies
- Exceed your risk tolerance
- Ignore position limits
- Share API credentials
- Deploy without testing
- Use capital you can't afford to lose

---

## Advanced Tips

### **Focus on Specific Markets**

```python
# In main(), filter markets
categories_to_scan = ['crypto', 'sports']
markets = [m for m in all_markets 
           if MarketCategorizer.categorize(m.get('question', '')) in categories_to_scan]
```

---

### **Adjust Scan Speed**

```python
# Faster scanning (more CPU, more opportunities)
SCAN_INTERVAL = 30  # Every 30s
MAX_WORKERS = 100  # More parallel workers

# Slower scanning (less CPU, lower costs)
SCAN_INTERVAL = 120  # Every 2 minutes
MAX_WORKERS = 20
```

---

## Support

**Issues:** https://github.com/georges91560/polymarket-oracle/issues  
**Docs:** https://github.com/georges91560/polymarket-oracle  
**Polymarket Docs:** https://docs.polymarket.com

---

**Scan everything. Configure wisely. Profit systematically. 🎯💰**

---

**END OF CONFIGURATION GUIDE**


---

**Scan everything. Configure wisely. Profit systematically. 🎯💰**

---

**END OF CONFIGURATION GUIDE**
