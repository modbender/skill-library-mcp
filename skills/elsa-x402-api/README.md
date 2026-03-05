<p align="center">
  <img src="assets/logo.svg" alt="Elsa + OpenClaw" width="400">
</p>

# elsa-openclaw

OpenClaw skill-pack for Elsa x402 DeFi API integration with micropayments.

This plugin enables OpenClaw agents to interact with the [Elsa DeFi API](https://x402.heyelsa.ai) using the x402 payment protocol for USDC micropayments on Base.

## Security Posture

- **Non-custodial**: Private keys never leave your machine
- **Local signing**: All transactions are signed locally using viem
- **Budget controls**: Per-call and daily USD limits enforced before any paid API call
- **Execution disabled by default**: Onchain execution tools require explicit opt-in
- **Confirmation tokens**: Dry-run required before confirmed execution (optional but recommended)
- **Separate wallets recommended**: Use different keys for API payments vs. trade execution

## Features

### Read-Only Tools (Always Available)
- `elsa_search_token` - Search tokens across blockchains
- `elsa_get_token_price` - Get real-time token pricing
- `elsa_get_balances` - Get wallet token balances
- `elsa_get_portfolio` - Comprehensive portfolio analysis
- `elsa_analyze_wallet` - Wallet behavior and risk assessment
- `elsa_get_swap_quote` - Get swap quotes and routing
- `elsa_execute_swap_dry_run` - Simulate swap execution (no onchain action)
- `elsa_budget_status` - Check current budget usage

### Execution Tools (Opt-In)
When `ELSA_ENABLE_EXECUTION_TOOLS=true`:
- `elsa_execute_swap_confirmed` - Execute swap with confirmation token
- `elsa_pipeline_get_status` - Check pipeline/transaction status
- `elsa_pipeline_submit_tx_hash` - Submit signed transaction hash
- `elsa_pipeline_run_and_wait` - Orchestrate full pipeline execution

## Installation

### 1. Clone and install

```bash
git clone https://github.com/HeyElsa/elsa-openclaw.git
cd elsa-openclaw
npm install
```

### 2. Configure OpenClaw

Edit `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "load": {
      "extraDirs": ["/path/to/elsa-openclaw"]
    },
    "entries": {
      "openclaw-elsa-x402": {
        "env": {
          "PAYMENT_PRIVATE_KEY": "0x_YOUR_WALLET_PRIVATE_KEY"
        }
      }
    }
  }
}
```

**Minimal config** - only `PAYMENT_PRIVATE_KEY` is required. All other settings have sensible defaults.

**With execution enabled** (for swaps):
```json
{
  "skills": {
    "load": {
      "extraDirs": ["/path/to/elsa-openclaw"]
    },
    "entries": {
      "openclaw-elsa-x402": {
        "env": {
          "PAYMENT_PRIVATE_KEY": "0x...",
          "TRADE_PRIVATE_KEY": "0x...",
          "ELSA_ENABLE_EXECUTION_TOOLS": "true"
        }
      }
    }
  }
}
```

### 3. Fund your payment wallet

The payment wallet needs USDC on Base to pay for API calls (~$0.01-0.05 per call).

### 4. Restart OpenClaw

The skill will load automatically. Verify with `/skills` in chat.

## Usage in OpenClaw

Once configured, just talk naturally:

| You say | Tool used |
|---------|-----------|
| "What's the price of WETH?" | `elsa_get_token_price` |
| "Search for PEPE token" | `elsa_search_token` |
| "Show portfolio for 0xd8dA..." | `elsa_get_portfolio` |
| "Get a quote to swap 10 USDC to WETH" | `elsa_get_swap_quote` |
| "How much have I spent on Elsa API?" | `elsa_budget_status` |
| "Swap 10 USDC to WETH on Base" | Full swap flow (with execution enabled) |

## Smoke Test

After installation, verify the setup:

```bash
# Search for a token
npx tsx scripts/index.ts elsa_search_token '{"query": "USDC", "limit": 3}'

# Get portfolio for a sample address
npx tsx scripts/index.ts elsa_get_portfolio '{"wallet_address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"}'

# Check budget status
npx tsx scripts/index.ts elsa_budget_status '{}'
```

> **Field Mapping Note**: This skill uses `wallet_address` in tool inputs, which maps internally to Elsa API's `evm_address` field.

Expected output includes:
- `ok: true` for successful calls
- `billing: { estimated_cost_usd, ... }` showing API cost
- `meta: { latency_ms, ... }` with request metadata

## Enabling Execution Tools

**WARNING**: Execution tools perform real onchain transactions.

```bash
# Required for x402 API payments
PAYMENT_PRIVATE_KEY=0x...

# Required for signing swap transactions (falls back to PAYMENT_PRIVATE_KEY if not set)
TRADE_PRIVATE_KEY=0x...

# Enable execution tools
ELSA_ENABLE_EXECUTION_TOOLS=true
```

1. Set `ELSA_ENABLE_EXECUTION_TOOLS=true`
2. Ensure `TRADE_PRIVATE_KEY` has sufficient funds for gas and swaps
3. Recommended: Use separate wallets for payments vs. trading

### Recommended Swap Flow

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────┐     ┌─────────────────────┐
│ 1. Get Quote        │ ──▶ │ 2. Dry Run          │ ──▶ │ 3. Confirm  │ ──▶ │ 4. Execute Pipeline │
│ elsa_get_swap_quote │     │ elsa_execute_swap_  │     │ [User says  │     │ elsa_pipeline_run_  │
│                     │     │ dry_run             │     │  "yes"]     │     │ and_wait            │
└─────────────────────┘     └─────────────────────┘     └─────────────┘     └─────────────────────┘
```

**Step 1: Get Quote** - Show user what they'll receive
```bash
npx tsx scripts/index.ts elsa_get_swap_quote '{
  "from_chain": "base", "from_token": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
  "from_amount": "10", "to_chain": "base", "to_token": "0x4200000000000000000000000000000000000006",
  "wallet_address": "0x...", "slippage": 0.5
}'
```

**Step 2: Dry Run** - Create pipeline, get `pipeline_id`
```bash
npx tsx scripts/index.ts elsa_execute_swap_dry_run '{...same params...}'
# Returns: { "pipeline_id": "abc-123", ... }
```

**Step 3: User Confirmation** - Present results and wait for explicit "yes"

**Step 4: Execute Pipeline** - Sign and broadcast transactions
```bash
ELSA_ENABLE_EXECUTION_TOOLS=true npx tsx scripts/index.ts elsa_pipeline_run_and_wait '{
  "pipeline_id": "abc-123",
  "timeout_seconds": 180,
  "poll_interval_seconds": 3,
  "mode": "local_signer"
}'
# Automatically: signs approve tx → submits → signs swap tx → submits → returns tx hashes
```

### Critical Rules

- **NEVER** execute swaps without showing the user the quote first
- **NEVER** call execution tools in a loop
- **NEVER** proceed if budget limits are exceeded
- **ALWAYS** check `elsa_budget_status` if unsure about remaining budget
- **ALWAYS** use dry-run mode first for any swap operation

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PAYMENT_PRIVATE_KEY` | Yes | - | Wallet for x402 API payments (hex with 0x prefix) |
| `TRADE_PRIVATE_KEY` | No | PAYMENT_PRIVATE_KEY | Wallet for tx signing (recommend separate) |
| `BASE_RPC_URL` | No | https://mainnet.base.org | Base RPC endpoint |
| `ELSA_API_URL` | No | https://x402-api.heyelsa.ai | Elsa API base URL |
| `ELSA_MAX_USD_PER_CALL` | No | 0.05 | Max USD per single API call |
| `ELSA_MAX_USD_PER_DAY` | No | 2.00 | Max USD spend per day |
| `ELSA_MAX_CALLS_PER_MINUTE` | No | 30 | Rate limit for API calls |
| `ELSA_TZ` | No | UTC | Timezone for daily budget reset (e.g., "Asia/Jakarta") |
| `ELSA_ENABLE_EXECUTION_TOOLS` | No | false | Enable onchain execution tools |
| `ELSA_REQUIRE_CONFIRMATION_TOKEN` | No | true | Require dry-run before execution |
| `ELSA_CONFIRMATION_TTL_SECONDS` | No | 600 | Token validity period |
| `ELSA_AUDIT_LOG_PATH` | No | - | Path for JSONL audit logs |
| `LOG_LEVEL` | No | info | Logging level (debug/info/warn/error) |

## API Pricing

Pricing may change. Actual costs are determined by x402 payment headers at request time.

See current pricing at [x402.heyelsa.ai](https://x402.heyelsa.ai).

## Supported Chains

- base (default)
- ethereum
- arbitrum
- optimism
- polygon
- bsc
- avalanche
- zksync

## Coming Soon

- **Hyperliquid Perp Endpoints** - Perpetual futures trading on Hyperliquid L1
- **Polymarket APIs** - Prediction market trading and data

## License

MIT
