# Configuration Guide

**Crypto Sniper Oracle v3.3.0 - Complete Setup**

---

## Quick Start

### **Minimum Setup (No Telegram)**

```bash
git clone https://github.com/georges91560/crypto-sniper-oracle.git
cp -r crypto-sniper-oracle/* /workspace/skills/crypto-sniper-oracle/
chmod +x /workspace/skills/crypto-sniper-oracle/*.py
```

**Test:**
```bash
python3 /workspace/skills/crypto-sniper-oracle/crypto_oracle.py --symbol BTCUSDT
```

---

## Telegram Setup (Optional)

### **Step 1: Create Telegram Bot**

1. **Open Telegram app**
2. **Search:** `@BotFather`
3. **Send:** `/newbot`
4. **Follow prompts:**
   - Bot name: `Crypto Sniper Bot` (or your choice)
   - Bot username: `your_crypto_sniper_bot` (must end in `bot`)
5. **Save the BOT_TOKEN:**
   ```
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567
   ```

---

### **Step 2: Get Your Chat ID**

**Method 1: Via API**
1. Send any message to your bot
2. Visit (replace YOUR_TOKEN):
   ```
   https://api.telegram.org/botYOUR_TOKEN/getUpdates
   ```
3. Look for:
   ```json
   "chat": {
     "id": 123456789
   }
   ```

**Method 2: Via @userinfobot**
1. Search `@userinfobot` in Telegram
2. Start chat
3. It will show your Chat ID

---

### **Step 3: Set Environment Variables**

**Temporary (current session):**
```bash
export TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567"
export TELEGRAM_CHAT_ID="123456789"
```

**Permanent (add to ~/.bashrc or ~/.profile):**
```bash
echo 'export TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"' >> ~/.bashrc
echo 'export TELEGRAM_CHAT_ID="123456789"' >> ~/.bashrc
source ~/.bashrc
```

---

### **Step 4: Test Telegram**

```bash
python3 /workspace/skills/crypto-sniper-oracle/reporter.py --mode test
```

**Expected output:**
```
[INFO] Fetching data for 0 symbols...
[OK] Report saved to /workspace/reports/test_2026-02-27.md
[OK] Telegram message sent
```

**Expected in Telegram:**
```
✅ Crypto Sniper Oracle - Telegram Test

If you see this, Telegram is configured correctly!
```

---

## Cron Jobs Setup (Optional)

### **Editing Crontab**

```bash
crontab -e
```

If first time, select editor (nano recommended).

---

### **Recommended Cron Jobs**

**Add these lines to crontab:**

```bash
# Daily market report at 9am UTC
0 9 * * * /usr/bin/python3 /workspace/skills/crypto-sniper-oracle/reporter.py --mode daily --symbols BTCUSDT,ETHUSDT,SOLUSDT,BNBUSDT,ADAUSDT

# Hourly status check
0 * * * * /usr/bin/python3 /workspace/skills/crypto-sniper-oracle/reporter.py --mode hourly --symbols BTCUSDT,ETHUSDT,SOLUSDT

# Anomaly alerts every 15 minutes
*/15 * * * * /usr/bin/python3 /workspace/skills/crypto-sniper-oracle/reporter.py --mode alerts --symbols BTCUSDT,ETHUSDT,SOLUSDT

# Weekly summary (Sunday 18:00 UTC)
0 18 * * 0 /usr/bin/python3 /workspace/skills/crypto-sniper-oracle/reporter.py --mode daily --symbols BTCUSDT,ETHUSDT,SOLUSDT,BNBUSDT,ADAUSDT,DOTUSDT,LINKUSDT,MATICUSDT,AVAXUSDT,UNIUSDT
```

**Important:** Use FULL paths (`/usr/bin/python3`, not just `python3`)

---

### **Find Python Path**

```bash
which python3
# Output: /usr/bin/python3
```

---

### **Verify Cron Jobs**

```bash
# List all cron jobs
crontab -l

# Check cron logs
grep CRON /var/log/syslog
```

---

## Configuration Options

### **Environment Variables**

```bash
# Telegram (optional)
TELEGRAM_BOT_TOKEN="your_bot_token"
TELEGRAM_CHAT_ID="your_chat_id"

# Cache TTL (optional, default: 45s)
ORACLE_CACHE_TTL="45"

# Logging (optional, default: INFO)
ORACLE_LOG_LEVEL="INFO"
```

---

### **Reporter Arguments**

```bash
python3 reporter.py [OPTIONS]

Options:
  --mode {daily|hourly|alerts|test}
        Report mode (required)
  
  --symbols SYMBOL1,SYMBOL2,...
        Comma-separated list of trading pairs
        Default: BTCUSDT,ETHUSDT,SOLUSDT,BNBUSDT,ADAUSDT

Examples:
  # Daily report for 5 pairs
  reporter.py --mode daily --symbols BTCUSDT,ETHUSDT,SOLUSDT,BNBUSDT,ADAUSDT
  
  # Hourly check for BTC only
  reporter.py --mode hourly --symbols BTCUSDT
  
  # Alerts for top 3 pairs
  reporter.py --mode alerts --symbols BTCUSDT,ETHUSDT,SOLUSDT
```

---

## Testing

### **Test Data Fetcher**

```bash
python3 crypto_oracle.py --symbol BTCUSDT
```

**Expected:** JSON output with OBI, VWAP, spread

---

### **Test Reporter (No Telegram)**

```bash
# Unset Telegram vars
unset TELEGRAM_BOT_TOKEN
unset TELEGRAM_CHAT_ID

python3 reporter.py --mode daily --symbols BTCUSDT,ETHUSDT
```

**Expected:**
- Report saved to `/workspace/reports/daily_YYYY-MM-DD.md`
- No Telegram delivery

---

### **Test Reporter (With Telegram)**

```bash
# Set Telegram vars
export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID="..."

python3 reporter.py --mode daily --symbols BTCUSDT,ETHUSDT
```

**Expected:**
- Report saved locally
- Report sent to Telegram

---

## File Locations

```
/workspace/
├── skills/crypto-sniper-oracle/
│   ├── crypto_oracle.py       # Data fetcher
│   ├── reporter.py            # Report generator
│   └── SKILL.md               # Skill definition
├── .oracle_cache.json         # Cache (auto-created)
├── TRADING_LOGS.md            # Execution logs (auto-created)
└── reports/                   # Reports directory (auto-created)
    ├── daily_2026-02-27.md
    ├── hourly_2026-02-27.md
    └── alerts_2026-02-27.log
```

---

## Permissions

### **Make Scripts Executable**

```bash
chmod +x /workspace/skills/crypto-sniper-oracle/crypto_oracle.py
chmod +x /workspace/skills/crypto-sniper-oracle/reporter.py
```

### **Create Reports Directory**

```bash
mkdir -p /workspace/reports
chmod 755 /workspace/reports
```

---

## Troubleshooting

### **"No module named ..."**

**Problem:** Missing Python dependencies

**Solution:**
This skill uses ONLY standard library. No pip install needed.

---

### **"Telegram message not sent"**

**Checklist:**
1. Verify bot token: `echo $TELEGRAM_BOT_TOKEN`
2. Verify chat ID: `echo $TELEGRAM_CHAT_ID`
3. Test connectivity:
   ```bash
   curl https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe
   ```
4. Run test:
   ```bash
   python3 reporter.py --mode test
   ```

---

### **"Cron job not running"**

**Checklist:**
1. **Use full paths:**
   ```bash
   # WRONG
   */15 * * * * reporter.py --mode alerts
   
   # CORRECT
   */15 * * * * /usr/bin/python3 /workspace/skills/crypto-sniper-oracle/reporter.py --mode alerts
   ```

2. **Check cron logs:**
   ```bash
   grep CRON /var/log/syslog | tail -20
   ```

3. **Test command manually:**
   ```bash
   /usr/bin/python3 /workspace/skills/crypto-sniper-oracle/reporter.py --mode daily
   ```

4. **Verify crontab syntax:**
   ```bash
   crontab -l
   ```

---

### **"Rate limit exceeded"**

**Problem:** Too many API calls to Binance

**Solution:**
- Cache prevents most rate limits (45s TTL)
- Don't query same symbol < 45s apart
- Spread out cron jobs (not all at same time)

---

### **"Report file not created"**

**Problem:** Permissions or path issue

**Solution:**
```bash
# Check directory exists
ls -la /workspace/reports/

# Create if needed
mkdir -p /workspace/reports

# Fix permissions
chmod 755 /workspace/reports
```

---

## Advanced Configuration

### **Custom Symbols List**

Create file `/workspace/my_symbols.txt`:
```
BTCUSDT
ETHUSDT
SOLUSDT
BNBUSDT
ADAUSDT
```

Use in cron:
```bash
0 9 * * * /usr/bin/python3 /workspace/skills/crypto-sniper-oracle/reporter.py --mode daily --symbols $(cat /workspace/my_symbols.txt | tr '\n' ',')
```

---

### **Multiple Telegram Destinations**

Send to multiple chats:
```bash
# Export multiple chat IDs
export TELEGRAM_CHAT_ID_MAIN="123456789"
export TELEGRAM_CHAT_ID_ALERTS="987654321"

# Modify reporter.py to send to both
```

---

### **Custom Report Templates**

Create `/workspace/skills/crypto-sniper-oracle/templates/custom_daily.md`

Modify `reporter.py` to use custom template.

---

## Best Practices

### ✅ **Do:**

- Test Telegram before enabling cron
- Use full paths in crontab
- Monitor logs regularly
- Archive old reports monthly
- Review anomaly alerts promptly

### ❌ **Don't:**

- Spam Telegram (respect rate limits)
- Run multiple identical cron jobs
- Delete TRADING_LOGS.md (audit trail)
- Share bot token publicly
- Ignore persistent errors

---

## Support

**Issues:** https://github.com/georges91560/crypto-sniper-oracle/issues  
**Documentation:** https://github.com/georges91560/crypto-sniper-oracle

---

**END OF CONFIGURATION GUIDE**
