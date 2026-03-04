# Crypto Genie - Database Architecture

## Overview

**New Design:** Decoupled architecture with local database and background sync worker.

- ✅ **Instant checks** - Query local database (no API latency)
- ✅ **No rate limits** - User queries don't hit Etherscan API
- ✅ **Deep analysis** - Analyzes transaction messages for suspicious content
- ✅ **Centralized data** - All data in one place
- ✅ **Background sync** - Separate worker fetches from Etherscan

## Architecture

```
┌─────────────────┐
│  User Request   │
│ Check address?  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  crypto_check_db.py     │ ◄── Queries local DB only
│  (Instant check)        │     (No external API calls)
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Local SQLite Database  │
│  ~/.config/crypto-scam- │
│   detector/crypto_data  │
│                         │
│  • Addresses            │
│  • Transactions         │
│  • Risk scores          │
│  • Scam indicators      │
└────────▲────────────────┘
         │
         │ Background sync
         │
┌────────┴────────────────┐
│  sync_worker.py         │ ◄── Pulls from Etherscan
│  (Background job)       │     Analyzes messages
│                         │     Calculates risk
│  • Reads sync queue     │
│  • Calls Etherscan API  │
│  • Decodes TX messages  │
│  • Stores in DB         │
└─────────────────────────┘
```

## Components

### 1. Database Layer (`database.py`)

SQLite database with tables:
- **addresses** - Address info, risk scores, balances
- **transactions** - Suspicious transactions with decoded messages
- **scam_indicators** - Individual red flags
- **sync_queue** - Addresses waiting to be synced

**Key functions:**
- `get_address(address)` - Retrieve address data
- `upsert_address(data)` - Store/update address
- `add_transaction(tx)` - Store suspicious transaction
- `add_scam_indicator(...)` - Add red flag
- `add_to_sync_queue(address)` - Queue for background sync

### 2. Background Worker (`sync_worker.py`)

Fetches data from Etherscan and stores in database.

**Features:**
- Queries Etherscan API for address data
- Decodes transaction input data (hex → UTF-8)
- **Analyzes messages for suspicious keywords**
  - "lazarus", "hack", "exploit", "private key"
  - Scam domains, phishing phrases
- Calculates risk score (0-100)
- Stores everything in local database

**Usage:**
```bash
# Add address to sync queue
python3 sync_worker.py --add-address 0x...

# Run worker (processes queue continuously)
python3 sync_worker.py

# Process only 10 addresses then stop
python3 sync_worker.py --max-jobs 10

# Show database statistics
python3 sync_worker.py --stats
```

### 3. Database-Only Checker (`crypto_check_db.py`)

Checks addresses against local database **only**.

**No external API calls** - instant results!

**Usage:**
```bash
# Check an address
python3 crypto_check_db.py 0x...

# JSON output
python3 crypto_check_db.py 0x... --json
```

**Behavior:**
- If address **in database** → Return full analysis
- If address **not in database** → Add to sync queue, return "pending"

## Risk Scoring Algorithm

Risk score is calculated based on multiple factors:

1. **Suspicious transactions** (+25 per transaction, max +50)
2. **Transaction count**
   - 0 transactions: +10 (very new)
   - 1-4 transactions: +5 (low activity)
3. **Balance patterns**
   - Large balance (>100 ETH) + suspicious TX: +20
4. **Contract verification**
   - Unverified contract: +30

**Risk Levels:**
- **0-19**: Low risk ✅
- **20-49**: Medium risk ℹ️
- **50-79**: High risk ⚠️
- **80-100**: Critical risk 🚨

## Suspicious Content Detection

The worker analyzes transaction input data for:

### Keywords
- Hacking groups: "lazarus", "vanguard"
- Threats: "hack", "exploit", "breach", "rug pull"
- Phishing: "private key", "seed phrase", "verify wallet"
- Social engineering: "urgent", "claim reward", "airdrop winner"

### Domains
- "metamask-support"
- "wallet-verify"
- "claim-eth"
- "free-crypto"

All detected in the example address `0x098B716B8Aaf21512996dC57EB0615e2383E2f96`!

## Database Schema

### addresses table
```sql
address TEXT PRIMARY KEY
chain TEXT
risk_score INTEGER (0-100)
risk_level TEXT (low/medium/high/critical)
is_known_scam BOOLEAN
is_contract BOOLEAN
is_verified BOOLEAN
scam_type TEXT
balance_eth REAL
transaction_count INTEGER
last_etherscan_sync TIMESTAMP
metadata JSON
```

### transactions table
```sql
tx_hash TEXT PRIMARY KEY
address TEXT
block_number INTEGER
from_address TEXT
to_address TEXT
input_data TEXT
decoded_message TEXT
is_suspicious BOOLEAN
suspicion_reason TEXT
```

### scam_indicators table
```sql
address TEXT
indicator_type TEXT
indicator_value TEXT
confidence INTEGER
source TEXT
detected_at TIMESTAMP
```

### sync_queue table
```sql
address TEXT PRIMARY KEY
chain TEXT
priority INTEGER
status TEXT (pending/processing/completed/failed)
retry_count INTEGER
```

## Deployment

### Development Mode

```bash
# Terminal 1: Run worker continuously
cd ~/.openclaw/workspace/skills/crypto-genie
source venv/bin/activate
export ETHERSCAN_API_KEY="your_key"
python3 sync_worker.py

# Terminal 2: Check addresses
python3 crypto_check_db.py 0x...
```

### Production Mode (Cron)

Add to crontab:
```bash
# Run worker every 5 minutes
*/5 * * * * cd ~/.openclaw/workspace/skills/crypto-genie && source venv/bin/activate && ETHERSCAN_API_KEY="key" python3 sync_worker.py --max-jobs 20
```

### Systemd Service

Create `/etc/systemd/system/crypto-sync-worker.service`:
```ini
[Unit]
Description=Crypto Genie Sync Worker
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/.openclaw/workspace/skills/crypto-genie
ExecStart=/home/ubuntu/.openclaw/workspace/skills/crypto-genie/venv/bin/python3 sync_worker.py
Environment="ETHERSCAN_API_KEY=your_key"
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable crypto-sync-worker
sudo systemctl start crypto-sync-worker
```

## Performance

- **Database size**: ~1KB per address
- **Check latency**: <5ms (database query)
- **Sync time**: ~2 seconds per address (Etherscan API)
- **Rate limit**: 5 requests/second (Etherscan free tier)

## Test Results

### Address: `0x098B716B8Aaf21512996dC57EB0615e2383E2f96`

**Before (v1.1.3):**
- ❌ Missed suspicious messages
- Risk score: 0/100 (false negative)

**After (Database mode):**
- ✅ Detected 5 suspicious transactions
- ✅ Found "Lazarus Vanguard" message
- ✅ Found "Orbit Bridge Hacker" reference
- ✅ Correct risk score: 100/100
- ✅ Flagged as CRITICAL RISK

## Migration from Old Version

The old `crypto_check.py` still works but doesn't use the database.

**New workflow:**
1. User checks address with `crypto_check_db.py`
2. If not in DB → queued for sync
3. Background worker syncs from Etherscan
4. Future checks are instant from DB

## Future Enhancements

- [ ] Support more chains (BSC, Polygon, Arbitrum)
- [ ] Machine learning for pattern detection
- [ ] Real-time monitoring of high-risk addresses
- [ ] API endpoint for web integration
- [ ] Webhook notifications for new scams
- [ ] Community reporting system

---

**Built for NeoClaw Hackathon 2026**
**Trust Claw Team**
