# 🔍 Crypto Scam Detector v2.0

**Database-first cryptocurrency scam detection for OpenClaw**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Compatible-green.svg)](https://openclaw.ai)

Protects users from cryptocurrency scams by analyzing addresses for phishing, honeypots, rug pulls, and ponzi schemes. Features a local database with background sync for instant, rate-limit-free checks.

## 🎯 Key Features

- ✅ **Instant Checks** - Database queries complete in <5ms
- ✅ **No Rate Limits** - User checks never hit external APIs
- ✅ **Deep Analysis** - Decodes and analyzes transaction messages
- ✅ **Auto-Queue** - Unknown addresses automatically queued for sync
- ✅ **Background Worker** - Separate process handles Etherscan sync
- ✅ **Encrypted Storage** - AES-256 encrypted API key storage
- ✅ **Multi-Source** - Combines Etherscan, ChainAbuse, and local data

## 🚀 Quick Start

### Installation

```bash
# Via ClawHub
clawhub install crypto-scam-detector

# Or manual
cd ~/.openclaw/workspace/skills/crypto-scam-detector
bash install.sh
```

### Setup

```bash
# Interactive setup (recommended)
./setup.sh

# Or set environment variable
export ETHERSCAN_API_KEY="your_key_here"
```

Get free API key: https://etherscan.io/myapikey

### Usage

```bash
# Check an address (instant)
python3 crypto_check_db.py 0x1234567890abcdef1234567890abcdef12345678

# Check with auto-sync if needed
./check_address.sh 0x1234567890abcdef1234567890abcdef12345678

# Run background worker
python3 sync_worker.py
```

## 📖 Documentation

- **[SKILL.md](SKILL.md)** - Complete usage guide
- **[DATABASE_ARCHITECTURE.md](DATABASE_ARCHITECTURE.md)** - Technical deep dive
- **[SECURITY.md](SECURITY.md)** - Security practices

## 🎨 Example Output

### Critical Risk Detection

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

⚠️ 5 Suspicious Transaction(s):
   • 0x74f7fbfe5a0bd3...
     Reason: Suspicious keyword detected: 'lazarus'
     Message: "Greetings Lazarus Vanguard..."

📋 Recommendations:
  🚫 DO NOT send funds to this address
  ⚠️ This address has been flagged as high risk
  📞 Report the source that gave you this address
```

## 🏗️ Architecture

```
User Check → crypto_check_db.py → Local SQLite DB
                                         ↑
                                         │
                            sync_worker.py (background)
                                         │
                                         ↓
                                   Etherscan API
```

**Benefits:**
- User checks are instant (no API calls)
- Background worker handles all external requests
- No rate limits on user queries
- Full transaction message analysis

## 🔍 What It Detects

| Scam Type | Detection Method |
|-----------|------------------|
| **Phishing** | Keywords: "private key", "seed phrase", "verify wallet" |
| **Honeypot** | Unverified contracts, suspicious patterns |
| **Rug Pull** | Transaction analysis, sudden liquidity |
| **Exploit Groups** | Keywords: "Lazarus", "hack", "exploit" |
| **Social Engineering** | "Urgent", "claim reward", "airdrop winner" |

## 📊 Risk Scoring

- **0-19** ✅ Low Risk
- **20-49** ℹ️ Medium Risk
- **50-79** ⚠️ High Risk
- **80-100** 🚨 Critical Risk

## 🔧 Configuration

### Sync Frequency (Recommended)

Add to crontab:
```bash
# Every 10 minutes, process 30 addresses
*/10 * * * * cd ~/.openclaw/workspace/skills/crypto-scam-detector && source venv/bin/activate && ETHERSCAN_API_KEY="key" python3 sync_worker.py --max-jobs 30
```

### Database Location

Default: `~/.config/crypto-scam-detector/crypto_data.db`

### Commands

```bash
# Check address
python3 crypto_check_db.py 0x... [--json]

# Add to sync queue
python3 sync_worker.py --add-address 0x...

# Run worker
python3 sync_worker.py [--max-jobs N] [--delay SECONDS]

# Show stats
python3 sync_worker.py --stats

# Auto-sync check
./check_address.sh 0x...
```

## 🆚 v1 vs v2

| Feature | v1.1.3 | v2.0.0 |
|---------|--------|--------|
| Check Speed | 2-5s | <5ms |
| Rate Limits | Yes | No |
| TX Analysis | ❌ | ✅ |
| Architecture | Direct API | DB + Worker |

## 🛡️ Security

- AES-256 encrypted API key storage
- No third-party data sharing
- Local processing only
- Open source and auditable
- No telemetry or tracking

## 🐛 Troubleshooting

**"Address not in database"**
```bash
./check_address.sh 0x...  # Auto-syncs
```

**"API key not configured"**
```bash
./setup.sh  # or export ETHERSCAN_API_KEY="key"
```

**Rate limit errors**
```bash
python3 sync_worker.py --delay 3.0
```

## 📈 Performance

- Check latency: <5ms
- Sync time: ~2s per address
- Database size: ~1KB per address
- Capacity: Millions of addresses

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📜 License

MIT License - See [LICENSE](LICENSE) file

## 🏆 Credits

**Developed by Trust Claw Team**
For NeoClaw Hackathon 2026

**Built with:**
- SQLite - Local database
- Etherscan API - Blockchain data
- ChainAbuse API - Community reports
- Python asyncio - Async operations

## 🔗 Links

- **ClawHub:** https://clawhub.com/crypto-scam-detector
- **GitHub:** https://github.com/trustclaw/crypto-scam-detector
- **Issues:** https://github.com/trustclaw/crypto-scam-detector/issues
- **Discord:** https://discord.com/invite/clawd

---

**🔐 Stay safe! Always verify addresses before sending funds.**
