# Multi-Chain Support

Version 2.2.0 adds support for multiple blockchain networks.

## Supported Blockchains

### ✅ Fully Supported

| Blockchain | Status | Scanner | Notes |
|------------|--------|---------|-------|
| **Ethereum** | ✅ Full | Etherscan API | Transaction analysis, contract verification |
| **Polygon** | ✅ Full | Same as Ethereum | EVM-compatible, shares address format |
| **BSC** | ✅ Full | Same as Ethereum | EVM-compatible, shares address format |

### 🔧 Partial Support

| Blockchain | Status | Scanner | Notes |
|------------|--------|---------|-------|
| **Solana** | 🔧 Basic | Solscan API | Basic address validation, full scanner coming soon |

### 🚧 Coming Soon

| Blockchain | Status | Notes |
|------------|--------|-------|
| **Bitcoin** | 🚧 Planned | Address validation works, scanner in development |
| **XRP (Ripple)** | 🚧 Planned | Address validation works, scanner in development |
| **Cardano** | 🚧 Planned | Pattern recognition in development |
| **Tron** | 🚧 Planned | Pattern recognition in development |

## How It Works

### 1. Automatic Detection

The system automatically detects which blockchain an address belongs to based on its format:

```bash
# Ethereum/EVM
python3 crypto_check_db.py 0x098B716B8Aaf21512996dC57EB0615e2383E2f96

# Solana
python3 crypto_check_db.py DYw8jCTfwHNRJhhmFcbXvVDTqWMEVFBX6ZKUmG5CNSKK

# XRP
python3 crypto_check_db.py rN7n7otQDd6FczFgLdlqtyMVrn3hBoQh8F

# Bitcoin
python3 crypto_check_db.py 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
```

### 2. Smart Routing

Once the blockchain is detected, the system:

1. **Checks local database** for cached data
2. **Routes to appropriate scanner** (Etherscan, Solscan, etc.)
3. **Fetches and analyzes** blockchain-specific data
4. **Stores in database** with blockchain tag
5. **Returns unified risk assessment**

### 3. Address Formats

#### Ethereum / EVM Chains
- **Format:** `0x` followed by 40 hex characters
- **Example:** `0x098B716B8Aaf21512996dC57EB0615e2383E2f96`
- **Note:** Same format for Ethereum, Polygon, BSC, Arbitrum, Optimism, etc.

#### Solana
- **Format:** 32-44 base58 characters (no 0, O, I, l)
- **Example:** `DYw8jCTfwHNRJhhmFcbXvVDTqWMEVFBX6ZKUmG5CNSKK`

#### XRP Ledger
- **Format:** Starts with `r`, followed by 24-34 alphanumeric chars
- **Example:** `rN7n7otQDd6FczFgLdlqtyMVrn3hBoQh8F`

#### Bitcoin
- **Format:** 
  - Legacy: Starts with `1` or `3`, 25-34 base58 chars
  - SegWit: Starts with `bc1`, 39-59 bech32 chars
- **Example:** `1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa`

## API Keys

### Required API Keys

Each blockchain scanner requires its own API key:

| Blockchain | API Key | Get Key From |
|------------|---------|--------------|
| Ethereum | `ETHERSCAN_API_KEY` | https://etherscan.io/apis |
| Solana | `SOLANA_API_KEY` | https://pro.solscan.io/ (coming soon) |
| Bitcoin | `BLOCKCHAIN_API_KEY` | https://blockchain.com/api (coming soon) |

### Configuration

```bash
# Setup wizard (interactive)
./setup.sh

# Or set environment variables
export ETHERSCAN_API_KEY="your_key_here"
export SOLANA_API_KEY="your_key_here"
```

## Database Schema

The database stores multi-chain data in a unified schema:

```sql
CREATE TABLE addresses (
    address TEXT PRIMARY KEY,
    chain TEXT NOT NULL DEFAULT 'ethereum',  -- 'ethereum', 'solana', 'bitcoin', etc.
    risk_score INTEGER,
    ...
);
```

Each address is tagged with its blockchain, allowing:
- ✅ Same address on different chains (rare but possible)
- ✅ Chain-specific analysis
- ✅ Cross-chain risk correlation (future feature)

## Response Format

All blockchain scanners return a unified response format:

```json
{
  "address": "0x...",
  "blockchain": "ethereum",
  "chain_name": "Ethereum",
  "risk_score": 70,
  "risk_level": "high",
  "is_contract": true,
  "transaction_count": 42,
  "balance": "1.5 ETH",
  ...
}
```

## Limitations

### EVM Address Ambiguity

Ethereum, Polygon, BSC, and other EVM chains share the same address format (`0x...`). The system defaults to Ethereum but shows a note:

```
⚠️ Note: This address could also be on Polygon or Binance Smart Chain
```

To check a specific EVM chain, the user would need to specify it explicitly (feature coming in v2.3.0).

### Solana Scanner Status

Solana support is currently **basic**:
- ✅ Address format validation
- ✅ Database storage
- 🚧 Full transaction analysis (coming soon)
- 🚧 Scam pattern detection (coming soon)

## Roadmap

### v2.2.0 (Current)
- ✅ Multi-chain address detection
- ✅ Ethereum/EVM full support
- ✅ Solana basic support
- ✅ Bitcoin/XRP/others address validation

### v2.3.0 (Next)
- 🚧 Solana full scanner with Solscan API
- 🚧 Bitcoin scanner with Blockchain.com API
- 🚧 XRP scanner with XRP Scan API
- 🚧 Manual chain selection for ambiguous addresses

### v2.4.0 (Future)
- 🚧 Cardano support
- 🚧 Tron support
- 🚧 Cross-chain risk correlation
- 🚧 Multi-chain portfolio analysis

## Examples

### Check Ethereum Address
```bash
python3 crypto_check_db.py 0x098B716B8Aaf21512996dC57EB0615e2383E2f96
```
Output:
```
🔍 Detected: Ethereum
⏳ Fetching from etherscan.io...
🚨 CRITICAL RISK (100/100)
```

### Check Solana Address
```bash
python3 crypto_check_db.py DYw8jCTfwHNRJhhmFcbXvVDTqWMEVFBX6ZKUmG5CNSKK
```
Output:
```
🔍 Detected: Solana
⏳ Fetching from solscan.io...
✅ LOW RISK (0/100)
ℹ️ Note: Solana scanner is in development
```

### Check Unsupported Blockchain
```bash
python3 crypto_check_db.py rN7n7otQDd6FczFgLdlqtyMVrn3hBoQh8F
```
Output:
```
❌ Error: XRP Ledger support coming soon!
Currently only Ethereum and Solana are supported.
```

## Architecture

```
User Input
    ↓
Blockchain Detector (blockchain_detector.py)
    ↓
[Ethereum] → Etherscan API → Database
[Solana]   → Solscan API  → Database (basic)
[Bitcoin]  → Coming Soon   → Database
[XRP]      → Coming Soon   → Database
    ↓
Unified Response
```

## Contributing

Want to add support for a new blockchain? See `blockchain_detector.py` and `sync_worker.py` for implementation patterns.

Key files:
- `blockchain_detector.py` - Add address pattern
- `sync_worker.py` - Add scanner implementation
- `crypto_check_db.py` - Add routing logic
