---
name: crypto-sniper-oracle
description: Institutional-grade quantitative market oracle with Order Book Imbalance (OBI), VWAP analysis, automated reports, and Telegram alerts.
version: 3.3.0
metadata:
  openclaw:
    emoji: "🎯"
    requires:
      bins: ["python3"]
      env: []
    network_behavior:
      makes_requests: true
      endpoints_allowed:
        - "https://api.binance.com/api/v3/*"
        - "https://api.telegram.org/bot*"
      optional_credentials: ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
    security_level: "L1 - Read-Only Public Data (L2 with Telegram)"
    author: "Georges Andronescu (Wesley Armando)"
    license: "MIT"
    homepage: "https://github.com/georges91560/crypto-sniper-oracle"
    repository: "https://github.com/georges91560/crypto-sniper-oracle"
---

# Crypto Sniper Oracle — Quantitative Market Intelligence + Reporting

## ⚠️ SCOPE & CAPABILITIES

**Core Function:** Fetch public market data and generate quantitative analysis.

**What it does:**
- ✅ Fetches public ticker data from Binance API
- ✅ Fetches public order book data from Binance API
- ✅ Calculates Order Book Imbalance (OBI)
- ✅ Calculates VWAP divergence
- ✅ Scores liquidity quality (spread in bps)
- ✅ Generates formatted analysis reports
- ✅ **[OPTIONAL]** Sends reports via Telegram
- ✅ **[OPTIONAL]** Scheduled cron jobs for automated reports

**What it does NOT do:**
- ❌ Place orders or execute trades
- ❌ Transfer funds
- ❌ Access private exchange data
- ❌ Read agent memory (beyond its own logs)
- ❌ Intercept or block other skills

---

## 🔧 Configuration Options

### **Mode 1: Analysis Only (Default)**

**No Telegram, manual invocation:**
```bash
# Just fetch data and analyze
python3 crypto_oracle.py --symbol BTCUSDT
```

**Use case:** Manual analysis on demand.

---

### **Mode 2: Telegram Reports (Optional)**

**Enable Telegram alerts and reports:**

**Required environment variables:**
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"
```

**Configuration:**
```json
{
  "skills": {
    "crypto-sniper-oracle": {
      "enabled": true,
      "config": {
        "telegram_enabled": true
      }
    }
  }
}
```

**Use case:** Automated reports sent to Telegram.

---

### **Mode 3: Cron Jobs + Telegram (Automated)**

**Scheduled market reports:**

**Example cron jobs:**
```bash
# Daily report at 9am UTC
0 9 * * * /workspace/skills/crypto-sniper-oracle/reporter.py --mode daily

# Hourly anomaly check
0 * * * * /workspace/skills/crypto-sniper-oracle/reporter.py --mode hourly

# Price alerts every 15min
*/15 * * * * /workspace/skills/crypto-sniper-oracle/reporter.py --mode alerts
```

**Use case:** Fully automated market monitoring.

---

## 📊 Report Templates

### **1. Daily Market Report**

**Trigger:** Cron (9am daily) or manual command

**Content:**
```markdown
📊 CRYPTO MARKET DAILY REPORT
{date} | Powered by Wesley

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 MARKET OVERVIEW (10 pairs analyzed)

🟢 BULLISH SETUPS (OBI > +0.15)
• BTCUSDT: OBI +0.18, Spread 2.1 bps
  Price vs VWAP: +0.5% (above average)
  Signal: Strong buying pressure

• ETHUSDT: OBI +0.12, Spread 3.5 bps
  Price vs VWAP: +0.3%
  Signal: Moderate bullish

🔴 BEARISH SETUPS (OBI < -0.15)
• SOLUSDT: OBI -0.16, Spread 8.2 bps
  Price vs VWAP: -0.8%
  Signal: Selling pressure

💰 LIQUIDITY QUALITY
Excellent (< 5 bps): 5 pairs
Good (5-10 bps): 3 pairs
Poor (> 30 bps): 2 pairs

📈 TOP MOVERS (24h)
+12.3% SOLUSDT (volatility: HIGH)
+8.1% ETHUSDT (volatility: MODERATE)
-5.2% BNBUSDT (volatility: MODERATE)

🎯 TRADING OPPORTUNITIES
→ BTC: Bullish setup confirmed (OBI +0.18)
→ ETH: Moderate strength, watch for breakout
→ SOL: Avoid - selling pressure + poor liquidity

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated: 2026-02-27 09:00:00 UTC
Next report: 2026-02-28 09:00:00 UTC
```

---

### **2. Anomaly Alert**

**Trigger:** OBI spike, spread explosion, or volume surge

**Content:**
```markdown
🚨 MARKET ANOMALY DETECTED

Time: 15:23:45 UTC
Asset: BTCUSDT

📊 Anomaly Type: OBI SPIKE
• Previous OBI: +0.05
• Current OBI: +0.22
• Change: +340% in 15 minutes

💰 Liquidity: EXCELLENT (2.3 bps)
📈 Price vs VWAP: +0.6%

💡 Implication:
Strong buying pressure surge detected.
Potential upward price movement imminent.

🎯 Suggested Action:
Consider LONG entry if other signals align.
Monitor closely for next 30 minutes.

[View Full Analysis]
```

---

### **3. Hourly Summary**

**Trigger:** Cron (every hour)

**Content:**
```markdown
⚡ HOURLY MARKET CHECK
{timestamp}

🔍 Scanned: 10 pairs
🟢 Bullish: 3
🔴 Bearish: 2
⚪ Neutral: 5

📊 Notable Changes:
• BTC OBI: +0.05 → +0.12 (↑)
• ETH Spread: 3.2 → 5.8 bps (↑)

⚠️ Alerts: None
Next check: {next_hour}
```

---

## 🔐 File Access (Expanded)

**READ:**
- `/workspace/skills/crypto-sniper-oracle/crypto_oracle.py` (data fetcher)
- `/workspace/skills/crypto-sniper-oracle/reporter.py` (report generator)
- `/workspace/skills/crypto-sniper-oracle/templates/*.md` (report templates)

**WRITE:**
- `/workspace/.oracle_cache.json` (45s cache)
- `/workspace/MARKET_ANALYSIS.md` (analysis reports)
- `/workspace/TRADING_LOGS.md` (audit trail)
- `/workspace/reports/daily_{date}.md` (archived reports)
- `/workspace/reports/alerts_{date}.log` (alert history)

---

## 🌐 Network Access (Expanded)

**Always allowed:**
- ✅ `https://api.binance.com/api/v3/*` (public market data)

**Conditionally allowed (if Telegram enabled):**
- ✅ `https://api.telegram.org/bot{token}/*` (send messages only)

**Never allowed:**
- ❌ Binance private endpoints
- ❌ Order placement endpoints
- ❌ Withdrawal endpoints

---

## 📋 Cron Job Specifications

### **Daily Report**

```bash
# Schedule: 9am UTC daily
0 9 * * * /workspace/skills/crypto-sniper-oracle/reporter.py --mode daily --symbols BTCUSDT,ETHUSDT,SOLUSDT,BNBUSDT,ADAUSDT

# What it does:
1. Fetch data for all symbols
2. Calculate OBI, VWAP, spread for each
3. Aggregate into daily report
4. Send via Telegram (if enabled)
5. Archive to /workspace/reports/daily_{date}.md
```

---

### **Hourly Check**

```bash
# Schedule: Every hour
0 * * * * /workspace/skills/crypto-sniper-oracle/reporter.py --mode hourly --symbols BTCUSDT,ETHUSDT

# What it does:
1. Quick scan of key pairs
2. Compare vs previous hour
3. Detect significant changes
4. Alert if anomaly detected
```

---

### **Price Alerts**

```bash
# Schedule: Every 15 minutes
*/15 * * * * /workspace/skills/crypto-sniper-oracle/reporter.py --mode alerts --symbols BTCUSDT

# What it does:
1. Check for OBI spikes (>50% change)
2. Check for spread explosions (>100% increase)
3. Check for volume surges (>200% of average)
4. Send immediate Telegram alert if detected
```

---

## 🛠️ How It Works

### **LAYER 1 — Data Acquisition (Unchanged)**

Same as v3.2.1 - uses `crypto_oracle.py` to fetch data.

---

### **LAYER 2 — Report Generation (NEW)**

```
PROCEDURE Generate_Report(mode, symbols):

  1. FETCH DATA FOR ALL SYMBOLS
     For each symbol in symbols:
       data[symbol] = call_oracle(symbol)

  2. AGGREGATE METRICS
     Calculate:
     - How many bullish (OBI > 0.15)
     - How many bearish (OBI < -0.15)
     - Average spread across all symbols
     - Top movers by price change %

  3. LOAD TEMPLATE
     template = load_template(f"{mode}_report.md")

  4. POPULATE TEMPLATE
     report = template.format(
       date=now(),
       bullish_pairs=format_bullish(data),
       bearish_pairs=format_bearish(data),
       liquidity_summary=format_liquidity(data),
       top_movers=format_movers(data)
     )

  5. SAVE REPORT
     Write to /workspace/reports/{mode}_{date}.md

  6. IF TELEGRAM ENABLED:
       send_telegram_message(report)

  7. LOG EXECUTION
     Write to /workspace/TRADING_LOGS.md
```

---

### **LAYER 3 — Telegram Delivery (NEW)**

```
PROCEDURE Send_Telegram_Report(report):

  1. VALIDATE CREDENTIALS
     IF TELEGRAM_BOT_TOKEN not set:
       → Log error: "Telegram not configured"
       → ABORT
     
     IF TELEGRAM_CHAT_ID not set:
       → Log error: "Chat ID not configured"
       → ABORT

  2. FORMAT MESSAGE
     # Telegram has 4096 char limit
     IF len(report) > 4000:
       → Split into multiple messages
       → Send sequentially

  3. SEND VIA API
     POST https://api.telegram.org/bot{token}/sendMessage
     Body:
     {
       "chat_id": "{chat_id}",
       "text": "{report}",
       "parse_mode": "Markdown"
     }

  4. HANDLE RESPONSE
     IF success:
       → Log: "Report sent to Telegram"
     
     IF error:
       → Log error details
       → Retry once after 5s
       → If still fails: Save to /workspace/failed_reports/
```

---

## 🔒 Security & Privacy

### **Data Collection:**
- Public market data only
- No authentication for Binance API
- No personal data

### **Data Processing:**
- All calculations local
- Cache temporary (45s TTL)
- Reports stored locally

### **Telegram (Optional):**
- User must explicitly enable
- User provides bot token + chat ID
- Only sends TO user's Telegram
- No data sent to third parties
- Can be disabled anytime

### **Transparency:**
- All Telegram sends logged
- All reports archived
- Full audit trail in TRADING_LOGS.md

---

## 📚 Installation & Setup

### **Basic Setup (No Telegram):**

```bash
git clone https://github.com/georges91560/crypto-sniper-oracle.git
cd crypto-sniper-oracle

cp -r * /workspace/skills/crypto-sniper-oracle/
chmod +x /workspace/skills/crypto-sniper-oracle/*.py
```

---

### **Telegram Setup (Optional):**

**Step 1: Create Telegram Bot**
```
1. Open Telegram, search @BotFather
2. Send: /newbot
3. Follow prompts, get BOT_TOKEN
```

**Step 2: Get Chat ID**
```
1. Send message to your bot
2. Visit: https://api.telegram.org/bot{YOUR_TOKEN}/getUpdates
3. Find "chat":{"id":123456789}
```

**Step 3: Configure**
```bash
export TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
export TELEGRAM_CHAT_ID="123456789"
```

**Step 4: Test**
```bash
python3 /workspace/skills/crypto-sniper-oracle/reporter.py --mode test
```

Expected: "✅ Test message sent to Telegram"

---

### **Cron Setup (Optional):**

```bash
# Edit crontab
crontab -e

# Add jobs:
0 9 * * * /workspace/skills/crypto-sniper-oracle/reporter.py --mode daily
0 * * * * /workspace/skills/crypto-sniper-oracle/reporter.py --mode hourly
*/15 * * * * /workspace/skills/crypto-sniper-oracle/reporter.py --mode alerts
```

---

## 📊 Usage Examples

### **Example 1: Manual Analysis**

```bash
python3 crypto_oracle.py --symbol BTCUSDT
```

**Output:** JSON data (same as v3.2.1)

---

### **Example 2: Generate Report (No Telegram)**

```bash
python3 reporter.py --mode daily --symbols BTCUSDT,ETHUSDT
```

**Output:** 
- Report saved to `/workspace/reports/daily_2026-02-27.md`
- No Telegram send

---

### **Example 3: Generate + Send Telegram**

```bash
# With env vars set
export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID="..."

python3 reporter.py --mode daily --symbols BTCUSDT,ETHUSDT
```

**Output:**
- Report saved locally
- Report sent to Telegram
- Logged in TRADING_LOGS.md

---

### **Example 4: Alert Check**

```bash
python3 reporter.py --mode alerts --symbols BTCUSDT
```

**If anomaly detected:**
```
🚨 Alert sent to Telegram
📝 Logged to /workspace/reports/alerts_2026-02-27.log
```

**If no anomaly:**
```
✅ No alerts - market normal
```

---

## 🎯 Transparency Statement

### **What This Skill Does:**

**Without Telegram:**
- Fetches public data
- Calculates metrics
- Generates reports
- Saves locally

**With Telegram (User Opt-In):**
- All of above PLUS
- Sends reports to user's Telegram
- User must provide bot token + chat ID
- User can disable anytime

### **What This Skill Does NOT Do:**

- Does NOT read agent memory
- Does NOT intercept other skills
- Does NOT trade or place orders
- Does NOT access private data
- Does NOT send data to third parties (except user's own Telegram if enabled)

### **Network Behavior:**

**Default:**
- Binance public API only

**With Telegram Enabled:**
- Binance public API
- Telegram API (send messages only, to user's bot)

---

## 📄 License

MIT License - See [LICENSE](LICENSE)

---

**Version:** 3.3.0  
**Security Level:** L1 (Default) / L2 (With Telegram)  
**Author:** Georges Andronescu (Wesley Armando)  
**Repository:** https://github.com/georges91560/crypto-sniper-oracle

---

**END OF SKILL**
