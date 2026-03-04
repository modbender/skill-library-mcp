# Crypto Sniper Oracle 🎯

**Institutional-grade quantitative market oracle with automated reporting**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-3.3.0-blue.svg)](https://github.com/georges91560/crypto-sniper-oracle)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![Security](https://img.shields.io/badge/security-L1%20ReadOnly-green.svg)]()

Order Book Imbalance (OBI) · VWAP Analysis · Automated Reports · Telegram Alerts

---

## 🚀 What's New in v3.3.0

✅ **Telegram Integration** (optional)  
✅ **Automated Reports** (daily, hourly, alerts)  
✅ **Cron Job Support** (scheduled monitoring)  
✅ **Report Templates** (professional formatting)  
✅ **Multi-Symbol Analysis** (aggregate reports)  

---

## 🎯 Core Features

### **1. Quantitative Analysis**
- Order Book Imbalance (OBI) detection
- VWAP divergence calculation
- Liquidity scoring (spread in bps)
- Composite risk scoring (0-100)

### **2. Automated Reporting**
- Daily market summaries
- Hourly status checks
- Real-time anomaly alerts
- Multi-symbol aggregation

### **3. Telegram Delivery (Optional)**
- Sends reports to your Telegram
- Configurable (opt-in)
- Instant alerts on anomalies
- Full message history

---

## 📊 Usage Modes

### **Mode 1: Manual Analysis**

```bash
python3 crypto_oracle.py --symbol BTCUSDT
```

**Output:** JSON data with OBI, VWAP, spread

---

### **Mode 2: Generate Report (No Telegram)**

```bash
python3 reporter.py --mode daily --symbols BTCUSDT,ETHUSDT,SOLUSDT
```

**Output:** 
- Formatted report saved to `/workspace/reports/daily_2026-02-27.md`
- No Telegram delivery

---

### **Mode 3: Automated Reports + Telegram**

**Setup:**
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"

python3 reporter.py --mode daily --symbols BTCUSDT,ETHUSDT
```

**Output:**
- Report saved locally
- Report sent to Telegram
- Logged to TRADING_LOGS.md

---

### **Mode 4: Cron Jobs (Fully Automated)**

```bash
# Daily report at 9am UTC
0 9 * * * /workspace/skills/crypto-sniper-oracle/reporter.py --mode daily

# Hourly check
0 * * * * /workspace/skills/crypto-sniper-oracle/reporter.py --mode hourly

# Alerts every 15min
*/15 * * * * /workspace/skills/crypto-sniper-oracle/reporter.py --mode alerts
```

---

## 📋 Report Examples

### **Daily Report**

```markdown
📊 CRYPTO MARKET DAILY REPORT
2026-02-27 09:00 UTC | Powered by Wesley

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 MARKET OVERVIEW (5 pairs analyzed)

🟢 BULLISH SETUPS (OBI > +0.15)
• BTCUSDT: OBI +0.18, Spread 2.1 bps
  Price vs VWAP: +0.5%
  24h Change: +3.2%
  Signal: Strong buying pressure

• ETHUSDT: OBI +0.12, Spread 3.5 bps
  Price vs VWAP: +0.3%
  24h Change: +2.1%
  Signal: Strong buying pressure

🔴 BEARISH SETUPS (OBI < -0.15)
• SOLUSDT: OBI -0.16, Spread 8.2 bps
  Price vs VWAP: -0.8%
  24h Change: -4.5%
  Signal: Selling pressure

💰 LIQUIDITY QUALITY
Excellent (< 5 bps): 3 pairs
Good (5-10 bps): 1 pairs
Poor (> 10 bps): 1 pairs

📈 TOP MOVERS (24h)
-4.5% SOLUSDT
+3.2% BTCUSDT
+2.1% ETHUSDT

🎯 TRADING OPPORTUNITIES
→ BTCUSDT: Bullish setup confirmed (OBI +0.18)
→ SOLUSDT: Avoid - selling pressure (OBI -0.16)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated: 2026-02-27 09:00:00 UTC
Next report: 2026-02-28 09:00:00 UTC
```

---

### **Anomaly Alert**

```markdown
🚨 MARKET ANOMALY DETECTED

Time: 15:23:45 UTC
Asset: BTCUSDT

📊 Anomaly Type: OBI SPIKE (BUY)
• Current OBI: +0.22
• Threshold: ±0.20

💰 Liquidity: EXCELLENT (2.3 bps)
📈 Price vs VWAP: +0.6%

💡 Implication:
Strong buying pressure detected.
Potential upward movement.

🎯 Suggested Action:
Consider LONG entry if other signals align.
```

---

## 🔧 Installation

### **Step 1: Clone Repository**

```bash
git clone https://github.com/georges91560/crypto-sniper-oracle.git
cd crypto-sniper-oracle
```

### **Step 2: Copy to Workspace**

```bash
mkdir -p /workspace/skills/crypto-sniper-oracle

cp crypto_oracle.py /workspace/skills/crypto-sniper-oracle/
cp reporter.py /workspace/skills/crypto-sniper-oracle/
cp SKILL.md /workspace/skills/crypto-sniper-oracle/

chmod +x /workspace/skills/crypto-sniper-oracle/*.py
```

### **Step 3: Test**

```bash
# Test data fetcher
python3 /workspace/skills/crypto-sniper-oracle/crypto_oracle.py --symbol BTCUSDT

# Test reporter
python3 /workspace/skills/crypto-sniper-oracle/reporter.py --mode daily --symbols BTCUSDT
```

---

## 📱 Telegram Setup (Optional)

### **Step 1: Create Bot**

1. Open Telegram
2. Search `@BotFather`
3. Send `/newbot`
4. Follow prompts
5. Save **BOT_TOKEN**

### **Step 2: Get Chat ID**

1. Send a message to your bot
2. Visit: `https://api.telegram.org/bot{YOUR_TOKEN}/getUpdates`
3. Find `"chat":{"id":123456789}`
4. Save **CHAT_ID**

### **Step 3: Configure**

```bash
export TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
export TELEGRAM_CHAT_ID="123456789"
```

### **Step 4: Test**

```bash
python3 /workspace/skills/crypto-sniper-oracle/reporter.py --mode test
```

**Expected:** Message in Telegram: "✅ Telegram Test"

---

## ⏰ Cron Setup (Optional)

### **Edit Crontab**

```bash
crontab -e
```

### **Add Jobs**

```bash
# Daily report at 9am UTC
0 9 * * * /workspace/skills/crypto-sniper-oracle/reporter.py --mode daily --symbols BTCUSDT,ETHUSDT,SOLUSDT,BNBUSDT,ADAUSDT

# Hourly check
0 * * * * /workspace/skills/crypto-sniper-oracle/reporter.py --mode hourly --symbols BTCUSDT,ETHUSDT

# Alerts every 15 minutes
*/15 * * * * /workspace/skills/crypto-sniper-oracle/reporter.py --mode alerts --symbols BTCUSDT,ETHUSDT,SOLUSDT
```

### **Verify**

```bash
crontab -l
```

---

## 📊 Metrics Explained

### **OBI (Order Book Imbalance)**

```
Formula: (Bid Volume - Ask Volume) / Total Volume

+0.20 or higher → Strong buy pressure
+0.10 to +0.20 → Moderate buy pressure
-0.10 to +0.10 → Neutral
-0.20 to -0.10 → Moderate sell pressure
-0.20 or lower → Strong sell pressure
```

### **VWAP Divergence**

```
Price vs 24h Volume-Weighted Average

> +1.0% → Overextended above average
+0.2 to +1.0% → Bullish strength
-0.2 to +0.2% → Fair value
< -1.0% → Oversold
```

### **Spread (Basis Points)**

```
< 5 bps → Excellent liquidity
5-10 bps → Good liquidity
10-30 bps → Moderate (slippage risk)
> 30 bps → Poor (avoid)
```

---

## 📁 File Structure

```
crypto-sniper-oracle/
├── crypto_oracle.py       # Data fetcher
├── reporter.py            # Report generator
├── SKILL.md               # Skill definition
├── README.md              # This file
├── CONFIGURATION.md       # Setup guide
└── LICENSE                # MIT License
```

**Created by skill:**
```
/workspace/
├── .oracle_cache.json           # Cache (45s TTL)
├── TRADING_LOGS.md              # Execution logs
└── reports/
    ├── daily_2026-02-27.md      # Daily reports
    ├── hourly_2026-02-27.md     # Hourly summaries
    └── alerts_2026-02-27.log    # Alert history
```

---

## 🔒 Security & Privacy

### **Data Collection**
- ✅ Public market data only
- ❌ No authentication required
- ❌ No personal data

### **Telegram (Optional)**
- ✅ User must explicitly enable
- ✅ User provides bot token + chat ID
- ✅ Sends ONLY to user's Telegram
- ❌ No third-party data sharing

### **Network Access**
- ✅ Binance public API
- ✅ Telegram API (if enabled)
- ❌ No other endpoints

---

## 🐛 Troubleshooting

### **Telegram not sending**

**Check:**
```bash
echo $TELEGRAM_BOT_TOKEN
echo $TELEGRAM_CHAT_ID
```

**Test:**
```bash
python3 reporter.py --mode test
```

### **Cron not running**

**Check logs:**
```bash
grep CRON /var/log/syslog
```

**Verify paths:**
```bash
which python3
# Use full path in crontab
```

### **Reports not generated**

**Check permissions:**
```bash
ls -la /workspace/reports/
chmod 755 /workspace/reports/
```

---

## 📄 License

MIT License - See [LICENSE](LICENSE)

---

## 👤 Author

**Georges Andronescu (Wesley Armando)**

- GitHub: [@georges91560](https://github.com/georges91560)
- Repository: [crypto-sniper-oracle](https://github.com/georges91560/crypto-sniper-oracle)

---

**Quantitative analysis + Automated reporting = Data-driven decisions.** 🎯
