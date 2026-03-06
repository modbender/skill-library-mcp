---
name: x402-layer
version: 1.2.1
description: |
  This skill should be used when the user asks to "create x402 endpoint",
  "deploy monetized API", "pay for API with USDC", "check x402 credits",
  "consume API credits", "list endpoint on marketplace", "buy API credits",
  "topup endpoint", "browse x402 marketplace", "set up webhook",
  "receive payment notifications", "manage endpoint webhook",
  use "Coinbase Agentic Wallet (AWAL)", or manage x402 Singularity Layer
  operations on Base or Solana networks.
homepage: https://studio.x402layer.cc/docs/agentic-access/openclaw-skill
metadata:
  clawdbot:
    emoji: "⚡"
    homepage: https://studio.x402layer.cc
    os:
      - linux
      - darwin
    requires:
      bins:
        - python3
      env:
        # Core credentials (required for payments)
        - WALLET_ADDRESS
        - PRIVATE_KEY
        # Solana payments (required for Solana network)
        - SOLANA_SECRET_KEY
        # Provider operations (required for endpoint management)
        - X_API_KEY
        - API_KEY
        # AWAL mode (optional - for Coinbase Agentic Wallet)
        - X402_USE_AWAL
        - X402_AUTH_MODE
        - X402_PREFER_NETWORK
        - AWAL_PACKAGE
        - AWAL_BIN
        - AWAL_FORCE_NPX
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - WebFetch
---


# x402 Singularity Layer

x402 is a **Web3 payment layer** enabling AI agents to:
- 💰 **Pay** for API access using USDC
- 🚀 **Deploy** monetized endpoints
- 🔍 **Discover** services via marketplace
- 📊 **Manage** endpoints and credits
- 🔔 **Webhooks** — receive payment notifications

**Networks:** Base (EVM) • Solana  
**Currency:** USDC  
**Protocol:** HTTP 402 Payment Required

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r {baseDir}/requirements.txt
```

### 2. Set Up Wallet (Choose One Mode)

#### Option A: Private Keys (existing mode)
```bash
# For Base (EVM)
export PRIVATE_KEY="0x..."
export WALLET_ADDRESS="0x..."

# For Solana (optional)
export SOLANA_SECRET_KEY="[1,2,3,...]"  # JSON array
```

#### Option B: Coinbase Agentic Wallet (AWAL)

For Base payments without exposing private keys, use Coinbase Agentic Wallet:

```bash
# First, install and set up AWAL (one-time setup)
npx skills add coinbase/agentic-wallet-skills

# Then enable AWAL mode for this skill
export X402_USE_AWAL=1
```

> **Note**: See [Coinbase AWAL docs](https://docs.cdp.coinbase.com/agentic-wallet/welcome) for full setup instructions. You'll need to authenticate and fund your AWAL wallet with USDC on Base.

Once AWAL is configured, all Base payment scripts will automatically use it instead of PRIVATE_KEY.

---

## ⚠️ Security Notice

> **IMPORTANT**: This skill handles private keys for signing blockchain transactions.
>
> - **Never use your primary custody wallet** - Create a dedicated wallet with limited funds
> - **Private keys are used locally only** - They sign transactions locally and are never transmitted
> - **Signed payloads are sent to api.x402layer.cc** - Payment signatures and wallet addresses are transmitted to settle payments
> - **For testing**: Use a throwaway wallet with minimal USDC ($1-5 is enough for testing)
> - **API Keys**: When you create an endpoint, store the returned API key securely
> - **Review the code**: All scripts are auditable in the `scripts/` directory

---

## Scripts Overview

### 🛒 CONSUMER MODE (Buying Services)

| Script | Purpose |
|--------|---------|
| `pay_base.py` | Pay for endpoint on Base network |
| `pay_solana.py` | Pay for endpoint on Solana network |
| `consume_credits.py` | Use pre-purchased credits (fast) |
| `consume_product.py` | Purchase digital products (files) |
| `awal_cli.py` | Run Coinbase Agentic Wallet CLI commands (auth, bazaar, pay, discover) |
| `check_credits.py` | Check your credit balance |
| `recharge_credits.py` | Buy credit packs for an endpoint |
| `discover_marketplace.py` | Browse available services |

### 🏭 PROVIDER MODE (Selling Services)

| Script | Purpose |
|--------|---------|
| `create_endpoint.py` | Deploy new monetized endpoint ($1) |
| `manage_endpoint.py` | View/update your endpoints |
| `topup_endpoint.py` | Recharge YOUR endpoint with credits |
| `list_on_marketplace.py` | Update marketplace listing |
| `manage_webhook.py` | Set/update/remove webhook URL |

---

## Security: API Key Verification

> [!IMPORTANT]
> When you create an endpoint, x402 acts as a proxy to your origin server. You MUST verify that requests are coming from x402.

1. **Get your API Key**: Returned when you run `create_endpoint.py`.
2. **Verify Headers**: Your origin server MUST check for this header in every request:
   ```http
   x-api-key: <YOUR_API_KEY>
   ```
   If the header is missing or incorrect, reject the request (401 Unauthorized).

---

## Credit System: How It Works

> [!WARNING]
> **Credits are NOT test credits!** They are consumed with every API request.

### Flow

```
User pays $0.01 → Your wallet receives payment → 1 credit deducted from your endpoint
```

### Economics

| Item | Value |
|------|-------|
| **Creation cost** | $1 (one-time) |
| **Starting credits** | 4,000 credits |
| **Recharge rate** | 500 credits per $1 |
| **Consumption** | 1 credit per API request |
| **Your earnings** | Whatever price you set per call |

### Example

1. **Create endpoint**: Pay $1, get 4,000 credits
2. **Set price**: $0.01 per call
3. **User calls your API 1,000 times**: You earn $10, 1,000 credits deducted
4. **Remaining**: 19,000 credits + $10 profit
5. **Credits run low?** Recharge with `topup_endpoint.py`

### What Happens When Credits = 0?

Your endpoint **stops working** and returns an error. Users cannot access it until you recharge.

---

## Consumer Flows

### A. Pay-Per-Request (Recommended)

```bash
# Pay with Base (EVM) - 100% reliable
python {baseDir}/scripts/pay_base.py https://api.x402layer.cc/e/weather-data

# Pay with Solana - includes retry logic
python {baseDir}/scripts/pay_solana.py https://api.x402layer.cc/e/weather-data

# Pay with Coinbase Agentic Wallet (AWAL)
python {baseDir}/scripts/awal_cli.py pay-url https://api.x402layer.cc/e/weather-data
```

### B. Credit-Based Access (Fastest)

Pre-purchase credits for instant access without blockchain latency:

```bash
# Check your balance
python {baseDir}/scripts/check_credits.py weather-data

# Buy credits (consumer purchasing credits)
python {baseDir}/scripts/recharge_credits.py weather-data pack_100

# Use credits for instant access
python {baseDir}/scripts/consume_credits.py https://api.x402layer.cc/e/weather-data
```

### C. Discover Services

```bash
# Browse all services
python {baseDir}/scripts/discover_marketplace.py

# Search by keyword
python {baseDir}/scripts/discover_marketplace.py search weather

# AWAL bazaar discovery
python {baseDir}/scripts/awal_cli.py run bazaar list
```

---

## Provider Flows

### A. Create Endpoint ($1 one-time)

Deploy your own monetized API:

**Basic (not listed on marketplace):**
```bash
python {baseDir}/scripts/create_endpoint.py my-api "My AI Service" https://api.example.com 0.01 --no-list
```

**With marketplace listing (recommended):**
```bash
python {baseDir}/scripts/create_endpoint.py my-api "My AI Service" https://api.example.com 0.01 \
    --category ai \
    --description "AI-powered data analysis API" \
    --logo https://example.com/logo.png \
    --banner https://example.com/banner.jpg
```

**Available categories:** `ai`, `data`, `finance`, `utility`, `social`, `gaming`

> **Note**: Save the `API Key` from the output and use it to secure your origin server.

> ⚠️ **IMPORTANT - How Credits Work:**
> - **Cost:** $1 one-time, includes **4,000 credits** (NOT test credits!)
> - **Consumption:** 1 credit is deducted for **each API request** to your endpoint
> - **When credits reach 0:** Your endpoint **stops working** until you recharge
> - **Recharge:** Use `topup_endpoint.py` to add more credits ($1 = 500 credits)
> - **Users pay YOU:** Each user payment goes to your wallet, then 1 credit is used

Includes 4,000 starting credits.

### B. Manage Your Endpoint

```bash
# List your endpoints
python {baseDir}/scripts/manage_endpoint.py list

# View stats
python {baseDir}/scripts/manage_endpoint.py stats my-api

# Update price
python {baseDir}/scripts/manage_endpoint.py update my-api --price 0.02
```

### C. Recharge Your Endpoint (Required to Keep It Working)

**Your endpoint consumes 1 credit per request.** When credits run out, it stops working. Recharge to keep it active:

```bash
# Add $10 worth of credits (5,000 credits at 500 credits/$1)
python {baseDir}/scripts/topup_endpoint.py my-api 10

# Check remaining credits first
python {baseDir}/scripts/manage_endpoint.py stats my-api
```

> ⚠️ **Remember:** `topup_endpoint.py` is for **providers** to recharge THEIR endpoint.
> `recharge_credits.py` is for **consumers** to buy credits at someone else's endpoint.

### D. Marketplace Listing Management

Marketplace listing can be done **during creation** OR **separately afterward**:

**Option 1: During Creation** (Recommended)
```bash
python {baseDir}/scripts/create_endpoint.py my-api "My API" https://api.example.com 0.01 \
    --category ai \
    --description "AI-powered analysis" \
    --logo https://example.com/logo.png \
    --banner https://example.com/banner.jpg
```

**Option 2: After Creation** (Update or List Later)
```bash
# List or update marketplace listing
python {baseDir}/scripts/list_on_marketplace.py my-api \
    --category ai \
    --description "AI-powered analysis" \
    --logo https://example.com/logo.png \
    --banner https://example.com/banner.jpg

# Unlist from marketplace
python {baseDir}/scripts/list_on_marketplace.py my-api --unlist
```

> **Tip:** Use `list_on_marketplace.py` to update your listing anytime - change category, description, or images without recreating the endpoint.

### E. Webhooks (Payment Notifications)

Receive `payment.succeeded` events when someone pays for your endpoint. Optional — not required for endpoints to work.

**Set webhook at creation time:**
```bash
python {baseDir}/scripts/create_endpoint.py my-api "My API" https://api.example.com 0.01 \
    --webhook-url https://my-server.com/webhook
```

**Add or update webhook on existing endpoint:**
```bash
python {baseDir}/scripts/manage_webhook.py set my-api https://my-server.com/webhook
```

**Check webhook status:**
```bash
python {baseDir}/scripts/manage_webhook.py info my-api
```

**Remove webhook:**
```bash
python {baseDir}/scripts/manage_webhook.py remove my-api
```

> ⚠️ **IMPORTANT**: The `signing_secret` is returned only once when you set a webhook. Save it immediately.

#### Webhook Event Types

| Event | When | Key Fields |
|-------|------|-----------|
| `payment.succeeded` | Any payment for your endpoint | `amount`, `tx_hash`, `payer_wallet`, `network` |
| `credits.depleted` | Owner credits hit 0 | `remaining_credits`, `topup_endpoint` |
| `credits.low` | Credits drop to ≤100 | `remaining_credits` |
| `credits.recharged` | Top-up payment succeeds | `credits_added`, `new_balance`, `amount_paid` |

Your endpoint receives POST requests with:
```http
Content-Type: application/json
X-X402-Event: <event_type>
X-X402-Signature: t=<timestamp>,v1=<hmac_sha256>
```

**payment.succeeded example:**
```json
{
  "id": "event-uuid",
  "type": "payment.succeeded",
  "created_at": "2026-01-01T00:00:00.000Z",
  "data": {
    "source": "endpoint",
    "source_slug": "my-api",
    "amount": 0.01,
    "currency": "USDC",
    "tx_hash": "0x...",
    "payer_wallet": "0x...",
    "network": "base",
    "status": "confirmed"
  }
}
```

**credits.depleted example:**
```json
{
  "type": "credits.depleted",
  "data": {
    "source": "endpoint",
    "source_slug": "my-api",
    "remaining_credits": 0,
    "message": "Endpoint credits exhausted. Top up to resume service."
  }
}
```

**credits.recharged example:**
```json
{
  "type": "credits.recharged",
  "data": {
    "source": "endpoint",
    "source_slug": "my-api",
    "credits_added": 5000,
    "previous_balance": 0,
    "new_balance": 5000,
    "amount_paid": 10,
    "currency": "USDC"
  }
}
```

#### Verify Webhook Signature
```python
import hmac, hashlib
def verify(secret, timestamp, body, received_sig):
    expected = hmac.new(secret.encode(), f"{timestamp}.{body}".encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, received_sig)
```

> **When credits = 0**, no requests go through, so no payments happen and no webhook events fire. Self-regulating.

---

## Payment Technical Details

### Base (EVM) - EIP-712 Signatures

Uses USDC `TransferWithAuthorization` (EIP-3009):
- Gasless for payer
- Facilitator settles on-chain
- 100% reliable

### Solana - Versioned Transactions

Uses `VersionedTransaction` with `MessageV0`:
- Facilitator pays gas (from `extra.feePayer`)
- SPL Token `TransferChecked` instruction
- ~75% success rate (retry logic included)

---

## Environment Reference

| Variable | Required For | Description |
|----------|--------------|-------------|
| `PRIVATE_KEY` | Base payments (private-key mode) | EVM private key (0x...) |
| `WALLET_ADDRESS` | All operations | Your wallet address |
| `SOLANA_SECRET_KEY` | Solana payments | JSON array of bytes |
| `X402_USE_AWAL` | AWAL mode | Set `1` to enable Coinbase Agentic Wallet for Base |
| `X402_AUTH_MODE` | Auth selection (optional) | `auto`, `private-key`, or `awal` (default: auto) |
| `X402_PREFER_NETWORK` | Network selection (optional) | `base` or `solana` (default: base) |
| `AWAL_PACKAGE` | AWAL mode (optional) | NPM package/version for AWAL CLI (default: `awal@1.0.0`) |
| `AWAL_BIN` | AWAL mode (optional) | Preinstalled `awal` binary path/name |
| `AWAL_FORCE_NPX` | AWAL mode (optional) | Set `1` to force npx even when `awal` binary exists |

---

## API Base URL

- **Endpoints:** `https://api.x402layer.cc/e/{slug}`
- **Marketplace:** `https://api.x402layer.cc/api/marketplace`
- **Credits:** `https://api.x402layer.cc/api/credits/*`
- **Agent API:** `https://api.x402layer.cc/agent/*`

---

## Resources

- 📖 **Documentation:** [studio.x402layer.cc/docs/agentic-access/openclaw-skill](https://studio.x402layer.cc/docs/agentic-access/openclaw-skill)
- 💻 **GitHub Docs:** [github.com/ivaavimusic/SGL_DOCS_2025](https://github.com/ivaavimusic/SGL_DOCS_2025)
- 🐦 **OpenClaw:** [x.com/openclaw](https://x.com/openclaw)
- 🌐 **x402 Studio:** [studio.x402layer.cc](https://studio.x402layer.cc)

---

## Known Issues

⚠️ **Solana payments** have ~75% success rate due to facilitator-side fee payer infrastructure issue. Retry logic is included in `pay_solana.py`. **Base (EVM) payments are 100% reliable** and recommended for production.
