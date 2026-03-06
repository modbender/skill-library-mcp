---
name: crypto-genie
displayName: Crypto Genie
version: 2.0.0
author: Trust Claw Team
description: AI-powered cryptocurrency safety assistant with database-first architecture. Protects users from phishing, honeypots, rug pulls, and ponzi schemes. No external API calls during checks!
category: security
tags: [crypto, scam-detection, ethereum, blockchain, security, fraud-prevention, web3, defi, database, etherscan, ai-assistant]
license: MIT
icon: 🧞
command: python3 crypto_check_db.py
---

# 🧞 Crypto Genie v2.0

**Your AI-powered cryptocurrency safety assistant for OpenClaw**

Analyzes crypto addresses for phishing, honeypots, rug pulls, and ponzi schemes using a local database with background sync from Etherscan. **Zero external API calls during user checks** = instant results!

## ✨ What's New in v2.0

### 🚀 Major Architecture Upgrade

- ✅ **Database-first design** - All checks query local SQLite database
- ✅ **Instant results** - No API latency during checks (<5ms)
- ✅ **No rate limits** - User queries never hit Etherscan API
- ✅ **Background sync worker** - Separate process pulls from Etherscan
- ✅ **Transaction message analysis** - Decodes and analyzes hex data
- ✅ **Auto-queue system** - Unknown addresses automatically queued for sync
- ✅ **Deep scanning** - Detects suspicious keywords in transaction data

### 🔍 Enhanced Detection

Now catches scams the old version missed:
- ✅ "Lazarus Vanguard" hacking group references
- ✅ "Orbit Bridge Hacker" mentions
- ✅ Private key phishing attempts
- ✅ Exploit recruitment messages
- ✅ And much more...

## 📦 What's Included

```
crypto-genie/
├── SKILL.md                    # This file
├── DATABASE_ARCHITECTURE.md    # Technical documentation
├── database.py                 # SQLite database layer
├── crypto_check_db.py          # Database-only checker (instant)
├── sync_worker.py              # Background Etherscan sync worker
├── secure_key_manager.py       # Encrypted API key storage
├── install.sh                  # Auto-installer
├── setup.sh                    # API key setup wizard
├── check_address.sh            # Convenience script (sync if needed)
├── requirements.txt            # Python dependencies
└── venv/                       # Virtual environment (created on install)
```

## 🚀 Quick Start

### 1. Install

```bash
cd ~/.openclaw/workspace/skills/crypto-genie
bash install.sh
```

### 2. Configure Etherscan API Key (Optional but Recommended)

**Option A: Interactive Setup** (Encrypted storage)
```bash
./setup.sh
# Follow the wizard to encrypt your API key
```

**Option B: Environment Variable**
```bash
export ETHERSCAN_API_KEY="your_key_here"
```

Get free API key: https://etherscan.io/myapikey

### 3. Check an Address

```bash
# Check address (instant, database-only)
python3 crypto_check_db.py 0x1234567890abcdef1234567890abcdef12345678
```

### 4. Run Background Sync Worker

**Manual mode:**
```bash
python3 sync_worker.py
# Runs continuously, processes queue
```

**Batch mode:**
```bash
python3 sync_worker.py --max-jobs 20
# Process 20 addresses then exit
```

**Cron schedule (recommended):**
```bash
# Add to crontab
*/10 * * * * cd ~/.openclaw/workspace/skills/crypto-genie && source venv/bin/activate && ETHERSCAN_API_KEY="key" python3 sync_worker.py --max-jobs 30
```

## 💡 How It Works

### Architecture Flow

```
User checks address
       ↓
┌──────────────────┐
│ crypto_check_db  │ ← Queries local database ONLY
└────────┬─────────┘   (No external API calls)
         │
         ↓
┌──────────────────────┐
│ Local SQLite DB      │
│ ~/.config/crypto-    │
│  scam-detector/      │
│                      │
│ • Addresses          │
│ • Transactions       │
│ • Risk scores        │
│ • Scam indicators    │
│ • Sync queue         │
└────────▲─────────────┘
         │
         │ Background sync
         │
┌────────┴─────────────┐
│ sync_worker.py       │ ← Pulls from Etherscan
│                      │   (Uses your API key)
│ • Reads queue        │
│ • Calls Etherscan    │
│ • Decodes TX data    │
│ • Analyzes messages  │
│ • Stores in DB       │
└──────────────────────┘
```

### User Flow

1. **Check address:** `python3 crypto_check_db.py 0x...`
2. **If in database:** Instant results with full analysis
3. **If NOT in database:** 
   - Returns "unknown" status
   - **Automatically adds to sync queue**
   - Shows: "⏳ Check again in a few minutes"
4. **Background worker syncs it** (next cron run or manual trigger)
5. **Check again:** Full analysis now available

## 🔍 Detection Capabilities

### Scam Types Detected

| Type | Detection Method |
|------|------------------|
| **Phishing** | Keyword analysis: "private key", "seed phrase", "verify wallet" |
| **Honeypot** | Contract code analysis (unverified contracts) |
| **Rug Pull** | Transaction pattern analysis |
| **Exploit Groups** | Keywords: "Lazarus", "hack", "exploit", "breach" |
| **Social Engineering** | Keywords: "urgent", "claim reward", "airdrop winner" |

### Risk Scoring

**Algorithm factors:**
- Suspicious transaction count (+25 per TX, max +50)
- Account age (new addresses: +10)
- Balance patterns (large balance + suspicious TX: +20)
- Contract verification (unverified: +30)

**Risk Levels:**
- **0-19**: ✅ Low Risk
- **20-49**: ℹ️ Medium Risk
- **50-79**: ⚠️ High Risk
- **80-100**: 🚨 Critical Risk

## 📋 Commands Reference

### Check Address
```bash
# Human-readable output
python3 crypto_check_db.py 0x...

# JSON output
python3 crypto_check_db.py 0x... --json
```

### Sync Worker
```bash
# Add address to queue
python3 sync_worker.py --add-address 0x...

# Run worker (continuous)
python3 sync_worker.py

# Process N addresses then stop
python3 sync_worker.py --max-jobs 20

# Custom delay between addresses
python3 sync_worker.py --delay 2.0

# Show database stats
python3 sync_worker.py --stats
```

### Convenience Script
```bash
# Check and auto-sync if needed
./check_address.sh 0x...
# Automatically syncs if not in DB, then shows results
```

## 🎯 Example Output

### Critical Risk Address
```
🚨 Analysis for 0x098b716b8aaf21512996dc57eb0615e2383e2f96

Risk Score: 100/100 - CRITICAL RISK
Last Updated: 2026-02-20 07:14:32

🚨 KNOWN SCAM DETECTED!

⚙️ Smart Contract
⚠️ NOT VERIFIED on Etherscan
   Transactions: 38
   Balance: 101.802430 ETH

🚨 5 Scam Indicator(s) Detected:
   • Suspicious keyword detected: 'lazarus' (confidence: 80%)
   • Suspicious keyword detected: 'hack' (confidence: 80%)
   • Suspicious keyword detected: 'exploit' (confidence: 80%)
   • Suspicious keyword detected: 'private key' (confidence: 80%)

⚠️ 5 Suspicious Transaction(s):
   • 0x74f7fbfe5a0bd3...
     Reason: Suspicious keyword detected: 'lazarus'
     Message: "Greetings Lazarus Vanguard..."

📋 Recommendations:
  🚫 DO NOT send funds to this address
  ⚠️ This address has been flagged as high risk
  📞 Report the source that gave you this address
```

### Unknown Address (Not Yet Synced)
```
⏳ Analysis for 0xnew_address_not_in_db

Risk Score: 0/100 - UNKNOWN
Last Updated: N/A

⏳ Address not yet in database
   Address not in database. Added to sync queue.

📋 Recommendations:
  ⏳ This address will be analyzed soon
  🔍 Check again in a few minutes
  ⚠️ Exercise caution until analysis completes
```

## ⚙️ Configuration

### Database Location
Default: `~/.config/crypto-genie/crypto_data.db`

### Etherscan API Rate Limits
- **Free tier:** 5 calls/second, 100,000 calls/day
- **Each address:** 4 API calls (balance, TX count, TX list, code)
- **Default delay:** 1.5 seconds between addresses (safe for free tier)

### Recommended Cron Schedule
```bash
# Every 10 minutes, process 30 addresses
*/10 * * * * cd ~/.openclaw/workspace/skills/crypto-genie && source venv/bin/activate && ETHERSCAN_API_KEY="key" python3 sync_worker.py --max-jobs 30 --delay 2.0

# Handles ~4,320 addresses per day
```

## 🛡️ Security

- ✅ **Encrypted API key storage** - AES-256 with PBKDF2
- ✅ **No third-party sharing** - API key only sent to Etherscan
- ✅ **Local processing** - All analysis happens on your machine
- ✅ **No telemetry** - Zero data collection
- ✅ **Open source** - Fully auditable code

## 📊 Database Schema

### Tables
- **addresses** - Address info, risk scores, balances, metadata
- **transactions** - Suspicious transactions with decoded messages
- **scam_indicators** - Individual red flags per address
- **sync_queue** - Addresses waiting to be synced

See `DATABASE_ARCHITECTURE.md` for full technical details.

## 🔄 Sync Frequency

**Default behavior:**
- First check → address queued for sync
- Worker processes queue (manual or cron)
- Subsequent checks → instant from database

**Recommended:** Run worker via cron every 5-10 minutes

## 💻 OpenClaw Integration

### Via Chat
```
"Check if 0x1234... is a scam"
"Is this address safe: 0xabc..."
"Verify 0xdef... before I send ETH"
```

### Automatic Detection
When you check an address, OpenClaw:
1. Runs `crypto_check_db.py`
2. If not in DB → queues for sync
3. Returns current status
4. Suggests checking again after sync

## 🐛 Troubleshooting

### "Address not in database"
**Solution:** Wait for background worker to sync it, or manually trigger:
```bash
python3 sync_worker.py --add-address 0x...
python3 sync_worker.py --max-jobs 1
```

### "Etherscan API key not configured"
**Solution:** Set API key via environment or setup wizard:
```bash
./setup.sh  # or
export ETHERSCAN_API_KEY="your_key"
```

### Rate limit errors
**Solution:** Increase delay between addresses:
```bash
python3 sync_worker.py --delay 3.0
```

## 📈 Performance

- ✅ **Check latency:** <5ms (database query)
- ✅ **Sync time:** ~2 seconds per address (4 API calls)
- ✅ **Database size:** ~1KB per address
- ✅ **Capacity:** Handles millions of addresses

## 🆚 Comparison: v1 vs v2

| Feature | v1.1.3 (Old) | v2.0.0 (New) |
|---------|--------------|--------------|
| **Check speed** | 2-5 seconds (API calls) | <5ms (database) |
| **Rate limits** | Yes (every check) | No (checks only query DB) |
| **TX message analysis** | ❌ Not analyzed | ✅ Fully analyzed |
| **False negatives** | High (missed scams) | Low (deep analysis) |
| **Architecture** | Direct API calls | Database + background worker |
| **API key usage** | Every check | Only background worker |

## 📜 License

MIT License - Free and open source

## 🤝 Support

- **ClawHub:** https://clawhub.com/crypto-genie
- **Hackathon:** NeoClaw Hackathon 2026

## 🏆 Credits

**Developed by Trust Claw Team** for NeoClaw Hackathon 2026

**Built with:**
- SQLite - Local database
- Etherscan API - Blockchain data
- ChainAbuse API - Community scam reports
- Python asyncio - Async operations

---

**🔐 Stay safe in crypto! Always verify addresses before sending funds.**
