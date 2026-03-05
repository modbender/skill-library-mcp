---
name: lp-agent
description: Run automated liquidity provision strategies on concentrated liquidity (CLMM) DEXs using Hummingbot API.
metadata:
  author: hummingbot
commands:
  start:
    description: Onboarding wizard — check setup status and get started
  deploy-hummingbot-api:
    description: Deploy Hummingbot API trading infrastructure
  setup-gateway:
    description: Start Gateway and configure network RPC endpoints
  add-wallet:
    description: Add or import a Solana wallet for trading
  explore-pools:
    description: Find and explore Meteora DLMM pools
  select-strategy:
    description: Choose between LP Executor or Rebalancer Controller strategy
  run-strategy:
    description: Run, monitor, and manage LP strategies
  analyze-performance:
    description: Export data and visualize LP position performance
---

# lp-agent

This skill helps you run automated liquidity provision strategies on concentrated liquidity (CLMM) DEXs using Hummingbot API.

**Commands** (run as `/lp-agent <command>`):

| Command | Description |
|---------|-------------|
| `start` | Onboarding wizard — check setup status and get started |
| `deploy-hummingbot-api` | Deploy Hummingbot API trading infrastructure |
| `setup-gateway` | Start Gateway, configure network RPC endpoints |
| `add-wallet` | Add or import a Solana wallet |
| `explore-pools` | Find and explore Meteora DLMM pools |
| `select-strategy` | Choose LP Executor or Rebalancer Controller |
| `run-strategy` | Run, monitor, and manage LP strategies |
| `analyze-performance` | Visualize LP position performance |

**New here?** Run `/lp-agent start` to check your setup and get a guided walkthrough.

**Typical workflow:** `start` → `deploy-hummingbot-api` → `setup-gateway` → `add-wallet` → `explore-pools` → `select-strategy` → `run-strategy` → `analyze-performance`

---

## Command: start

Welcome the user and guide them through setup. This is a conversational onboarding wizard — check infrastructure state, interpret results, and walk them through each step.

### Step 1: Welcome & Explain

Introduce yourself and explain what lp-agent does:

> I'm your LP agent — I help you run automated liquidity provision strategies on Meteora DLMM pools (Solana). I can:
>
> - **Deploy infrastructure** — Hummingbot API + Gateway for DEX trading
> - **Manage wallets** — Add Solana wallets, check balances
> - **Explore pools** — Search Meteora DLMM pools, compare APR/volume/TVL
> - **Run strategies** — Auto-rebalancing LP controller or single-position executor
> - **Analyze performance** — Dashboards with PnL, fees, and position history

### Step 2: Check Infrastructure Status

Run these scripts and interpret the JSON output:

```bash
bash scripts/check_api.sh --json      # Is Hummingbot API running?
bash scripts/check_gateway.sh --json  # Is Gateway running?
python scripts/add_wallet.py list     # Any wallets connected?
```

**Interpreting Results:**

| Script | Success Output | Failure Output |
|--------|---------------|----------------|
| `check_api.sh --json` | `{"running": true, "url": "http://localhost:8000", ...}` | `{"running": false, ...}` or connection error |
| `check_gateway.sh --json` | `{"running": true, ...}` | `{"running": false, ...}` |
| `add_wallet.py list` | Shows wallet addresses like `[solana] ABC123...` | `No wallets found.` or empty list `[]` |

### Step 3: Show Progress

Present a checklist showing what's done and what's remaining based on the script outputs:

```
Setup Progress:
  [x] Hummingbot API    — Running at http://localhost:8000
  [x] Gateway           — Running
  [ ] Wallet            — No wallet connected

Next step: Add a Solana wallet so you can start trading.
```

Adapt the checklist to the actual state. If everything is unchecked, start from the top. If everything is checked, skip to the LP lifecycle overview.

### Step 4: Guide Next Action

Based on the first unchecked item, offer to help:

| Missing | What to say |
|---------|-------------|
| Hummingbot API | "Let's deploy the API first — it's the trading backend. Need Docker installed. Want me to run the installer?" → `/lp-agent deploy-hummingbot-api` |
| Gateway | "API is running! Now we need Gateway for DEX connectivity. Want me to start it?" → `/lp-agent setup-gateway` |
| Wallet | See **Adding a Wallet** below |
| All ready | Move to Step 5 |

**Adding a Wallet:**

When wallet is the next step, tell the user:

> Infrastructure is ready. You need a Solana wallet with SOL for transaction fees (~0.06 SOL per LP position).
>
> To add a wallet, run:
> ```
> python scripts/add_wallet.py add
> ```
> You'll be prompted to paste your private key (secure, not saved in shell history).

**Interpreting add_wallet.py output:**

| Output | Meaning |
|--------|---------|
| `✓ Wallet added successfully` + address | Success — wallet is connected |
| `Enter private key (base58):` then `✓ Wallet added` | Success after prompt |
| `Error: HTTP 400` or validation error | Invalid private key format |
| `Error: Cannot connect to API` | API not running — run `check_api.sh` first |

After wallet is added, verify with `python scripts/add_wallet.py list` — should show the new address.

### Step 5: LP Lifecycle Overview

Once infrastructure is ready (or if user wants to understand the flow first), explain the LP lifecycle:

> **How LP strategies work:**
>
> 1. **Explore pools** (`/lp-agent explore-pools`) — Find a Meteora DLMM pool. Look at volume, APR, and fee/TVL ratio to pick a good one.
>
> 2. **Select strategy** (`/lp-agent select-strategy`) — Choose between:
>    - **Rebalancer Controller** (recommended) — Automatically repositions when price moves out of range. Set-and-forget.
>    - **LP Executor** — Single fixed position. You control when to close/reopen. Good for testing or limit-order-style LP.
>
> 3. **Run strategy** (`/lp-agent run-strategy`) — Configure parameters (amount, width, price limits) and deploy. Monitor status and stop when done.
>
> 4. **Analyze** (`/lp-agent analyze-performance`) — View PnL dashboard, fees earned, position history. Works for both running and stopped strategies.
>
> Want to explore some pools to get started?

---

## Command: deploy-hummingbot-api

Deploy the Hummingbot API trading infrastructure. This is the first step before using any LP features.

### What Gets Installed

**Hummingbot API** — A personal trading server that exposes a REST API for trading, market data, and deploying bot strategies across CEXs and DEXs.

- Repository: [hummingbot/hummingbot-api](https://github.com/hummingbot/hummingbot-api)

### Usage

```bash
# Check if already installed
bash scripts/deploy_hummingbot_api.sh status

# Install (interactive, prompts for credentials)
bash scripts/deploy_hummingbot_api.sh install

# Install with defaults (non-interactive: admin/admin)
bash scripts/deploy_hummingbot_api.sh install --defaults

# Upgrade existing installation
bash scripts/deploy_hummingbot_api.sh upgrade

# View container logs
bash scripts/deploy_hummingbot_api.sh logs

# Reset (stop and remove everything)
bash scripts/deploy_hummingbot_api.sh reset
```

### Prerequisites

- Docker and Docker Compose
- Git

### Interpreting Output

| Output | Meaning | Next Step |
|--------|---------|-----------|
| `✓ Hummingbot API deployed successfully` | Success | Proceed to `setup-gateway` |
| `✓ Already installed and running` | Already set up | Proceed to `setup-gateway` |
| `Error: Docker not found` | Docker not installed | Install Docker first |
| `Error: Port 8000 already in use` | Another service on port | Stop conflicting service or use different port |

### After Installation

Once the API is running:
1. Swagger UI is at `http://localhost:8000/docs`
2. Default credentials: admin/admin
3. Proceed to `setup-gateway` to enable DEX trading

---

## Command: setup-gateway

Start the Gateway service, check its status, and configure key network parameters like RPC node URLs. Gateway is required for all LP operations on DEXs.

**Prerequisite:** Hummingbot API must be running (`deploy-hummingbot-api`). The script checks this automatically.

### Usage

```bash
# Check Gateway status
bash scripts/setup_gateway.sh --status

# Start Gateway with defaults
bash scripts/setup_gateway.sh

# Start Gateway with custom image (e.g., development build)
bash scripts/setup_gateway.sh --image hummingbot/gateway:development

# Start with custom Solana RPC (recommended to avoid rate limits)
bash scripts/setup_gateway.sh --rpc-url https://your-rpc-endpoint.com

# Configure RPC for a different network
bash scripts/setup_gateway.sh --network ethereum-mainnet --rpc-url https://your-eth-rpc.com

# Start with custom passphrase and port
bash scripts/setup_gateway.sh --passphrase mypassword --port 15888
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--status` | | Check Gateway status only (don't start) |
| `--image IMAGE` | `hummingbot/gateway:development` | Docker image to use |
| `--passphrase TEXT` | `hummingbot` | Gateway passphrase |
| `--rpc-url URL` | | Custom RPC endpoint for `--network` |
| `--network ID` | `solana-mainnet-beta` | Network to configure RPC for |
| `--port PORT` | `15888` | Gateway port |

### Advanced: manage_gateway.py

For finer control (stop, restart, logs, per-network config), use `manage_gateway.py`:

```bash
python scripts/manage_gateway.py status                    # Check status
python scripts/manage_gateway.py start                     # Start Gateway
python scripts/manage_gateway.py stop                      # Stop Gateway
python scripts/manage_gateway.py restart                   # Restart Gateway
python scripts/manage_gateway.py logs                      # View logs
python scripts/manage_gateway.py networks                  # List all networks
python scripts/manage_gateway.py network solana-mainnet-beta                          # Get network config
python scripts/manage_gateway.py network solana-mainnet-beta --node-url https://...   # Set RPC node
```

### Interpreting Output

| Output | Meaning | Next Step |
|--------|---------|-----------|
| `✓ Gateway is running` or `✓ Gateway started` | Success | Proceed to `add-wallet` |
| `✓ Gateway is already running` | Already set up | Proceed to `add-wallet` |
| `✗ Cannot connect to Hummingbot API` | API not running | Run `/lp-agent deploy-hummingbot-api` first |
| `✗ Failed to start Gateway` | Docker issue | Check Docker is running, check logs |
| `✓ RPC configured` + `✓ Gateway restarted` | Custom RPC set | Ready to use |

### Custom RPC Nodes

Gateway uses public RPC nodes by default, which can hit rate limits. Set a custom nodeUrl per network to avoid this.

Popular Solana RPC providers:
- [Helius](https://helius.dev/) — Free tier available
- [QuickNode](https://quicknode.com/)
- [Alchemy](https://alchemy.com/)
- [Triton](https://triton.one/)

---

## Command: add-wallet

Add a Solana wallet for trading.

**Requires:** `deploy-hummingbot-api` and `setup-gateway` completed first.

### Adding a Wallet

```bash
python scripts/add_wallet.py add
```

You'll be prompted to paste your private key (base58 format). The key is entered securely and won't appear in shell history.

**Interpreting Output:**

| Output | Meaning | Next Step |
|--------|---------|-----------|
| `✓ Wallet added successfully` + `Address: ABC...` | Success | Verify with `list` command |
| `Error: HTTP 400 - Bad Request` | Invalid private key format | Check key is base58 encoded |
| `Error: HTTP 503` | Gateway not available | Run `bash scripts/check_gateway.sh` |
| `Error: Cannot connect to API` | API not running | Run `/lp-agent deploy-hummingbot-api` |

### Listing Wallets

```bash
python scripts/add_wallet.py list
```

**Interpreting Output:**

| Output | Meaning |
|--------|---------|
| `[solana] ABC123...XYZ` | Wallet connected on Solana |
| `No wallets found.` | No wallets added yet |
| Empty list `[]` (with --json) | No wallets added yet |

### Checking Balances

```bash
# Check all balances
python scripts/add_wallet.py balances

# Filter by account
python scripts/add_wallet.py balances --account master_account

# Show zero balances too
python scripts/add_wallet.py balances --all
```

### Requirements

- **SOL for fees**: Wallet needs SOL for transaction fees (~0.06 SOL per LP position for rent)
- **Default chain**: Solana mainnet-beta

---

## Command: explore-pools

Find and explore Meteora DLMM pools before creating LP positions.

**Note:** Pool listing (`list_meteora_pools.py`) works without any prerequisites — it queries the Meteora API directly. Pool details (`get_meteora_pool.py`) optionally uses Gateway for real-time price and liquidity charts.

### List Pools

Search and list pools by name, token, or address:

```bash
# Top pools by 24h volume
python scripts/list_meteora_pools.py

# Search by token symbol
python scripts/list_meteora_pools.py --query SOL
python scripts/list_meteora_pools.py --query USDC

# Search by pool name
python scripts/list_meteora_pools.py --query SOL-USDC

# Sort by different metrics
python scripts/list_meteora_pools.py --query SOL --sort tvl
python scripts/list_meteora_pools.py --query SOL --sort apr
python scripts/list_meteora_pools.py --query SOL --sort fees

# Pagination
python scripts/list_meteora_pools.py --query SOL --limit 50 --page 2
```

**Output columns:**
- **Pool**: Trading pair name
- **Pool Address**: Pool contract address (shortened, use `get_meteora_pool.py` for full address)
- **Base (mint)**: Base token symbol with shortened mint address
- **Quote (mint)**: Quote token symbol with shortened mint address
- **TVL**: Total value locked
- **Vol 24h**: 24-hour trading volume
- **Fees 24h**: Fees earned in last 24 hours
- **APR**: Annual percentage rate
- **Fee**: Base fee percentage
- **Bin**: Bin step (affects max position width)

**Note:** Token mints help identify the correct token when multiple tokens share the same name (e.g., multiple "PERCOLATOR" tokens).

### Get Pool Details

Get detailed information about a specific pool. Fetches from both Meteora API (historical data) and Gateway (real-time data):

```bash
python scripts/get_meteora_pool.py <pool_address>

# Example
python scripts/get_meteora_pool.py ATrBUW2reZiyftzMQA1hEo8b7w7o8ZLrhPd7M7sPMSms

# Output as JSON for programmatic use
python scripts/get_meteora_pool.py ATrBUW2reZiyftzMQA1hEo8b7w7o8ZLrhPd7M7sPMSms --json

# Skip Gateway (faster, no bin distribution)
python scripts/get_meteora_pool.py ATrBUW2reZiyftzMQA1hEo8b7w7o8ZLrhPd7M7sPMSms --no-gateway
```

**Data sources:**
- **Meteora API**: Historical volume, fees, APR, token info, market caps
- **Gateway** (requires running Gateway): Real-time price, liquidity distribution by bin

**Details shown:**
- Token info (symbols, mints, decimals, prices)
- Pool configuration (bin step, fees, max range width)
- Real-time price from Gateway (SOL/token ratio)
- Liquidity distribution chart showing bins around current price
- Liquidity and reserves
- Volume across time windows (30m, 1h, 4h, 12h, 24h)
- Fees earned across time windows
- Yield (APR, APY, farm rewards)
- Fee/TVL ratio (profitability indicator)

### Choosing a Pool

When selecting a pool, consider:

1. **TVL**: Higher TVL = more stable, but also more competition
2. **Volume**: Higher volume = more fee opportunities
3. **Fee/TVL Ratio**: Higher = more profitable per $ of liquidity
4. **Bin Step**: Determines max position width
   - `bin_step=1` → max ~0.69% width (tight ranges)
   - `bin_step=10` → max ~6.9% width (medium ranges)
   - `bin_step=100` → max ~69% width (wide ranges)

---

## Command: select-strategy

Help the user choose the right LP strategy. See `references/` for detailed guides.

### LP Rebalancer Controller (Recommended)

> **Reference:** `references/lp_rebalancer_guide.md`

A controller that automatically manages LP positions with rebalancing logic.

| Feature | Description |
|---------|-------------|
| **Auto-rebalance** | Closes and reopens positions when price exits range |
| **Price limits** | Configure BUY/SELL zones with anchor points |
| **KEEP logic** | Avoids unnecessary rebalancing when at optimal position |
| **Hands-off** | Set and forget - controller manages everything |

**Best for:** Longer-term LP strategies, range-bound markets, automated fee collection.

### LP Executor (Single Position)

> **Reference:** `references/lp_executor_guide.md`

Creates ONE liquidity position with fixed price bounds. No auto-rebalancing.

| Feature | Description |
|---------|-------------|
| **Fixed bounds** | Position stays at configured price range |
| **Manual control** | User decides when to close/reopen |
| **Limit orders** | Can auto-close when price exits range (like limit orders) |
| **Simple** | Direct control over single position |

**Best for:** Short-term positions, limit-order-style LP, manual management, testing.

### Quick Comparison

| Aspect | Rebalancer Controller | LP Executor |
|--------|----------------------|-------------|
| Rebalancing | Automatic | Manual |
| Position count | One at a time, auto-managed | One, fixed |
| Price limits | Yes (anchor points) | No (but has auto-close) |
| Complexity | Higher (more config) | Lower (simpler) |
| Use case | Set-and-forget | Precise control |

---

## Command: run-strategy

Run, monitor, and manage LP strategies.

**Requires:** `deploy-hummingbot-api`, `setup-gateway`, and `add-wallet` completed first.

### LP Rebalancer Controller (Recommended)

> **Reference:** See `references/lp_rebalancer_guide.md` for full configuration details, rebalancing logic, and KEEP vs REBALANCE scenarios.

Auto-rebalances positions when price moves out of range. Best for hands-off LP management.

> **Key concepts:**
> - `--amount` (`total_amount_quote`) = amount in **quote asset** (2nd token in pair). For `Percolator-SOL` → SOL. For `SOL-USDC` → USDC. Always quote, regardless of side.
> - All `*_pct` params are already in percent. `position_width_pct: 10` = 10% width. Do NOT pass decimals (not 0.10).
> - Price limits (`--buy-min/max`, `--sell-min/max`) default to `0` = no limit. Only set if you want a stop zone.

```bash
# 1. Create LP Rebalancer config (pool and pair are required)
python scripts/manage_controller.py create-config my_lp_config \
    --pool <pool_address> \
    --pair SOL-USDC \
    --amount 10 \       # 10 USDC (quote asset for SOL-USDC)
    --side 0 \          # 0=BOTH, 1=BUY (quote only), 2=SELL (base only)
    --width 10 \        # 10% range around current price
    --offset 1 \        # center range 1% from current price
    --rebalance-seconds 300 \
    --rebalance-threshold 1

# Side=2 example: deploy base token only (e.g. 110k PRCLT ≈ 1.33 SOL)
python scripts/manage_controller.py create-config percolator_sell \
    --pool ATrBUW2reZiyftzMQA1hEo8b7w7o8ZLrhPd7M7sPMSms \
    --pair Percolator-SOL \
    --amount 1.33 \     # 1.33 SOL worth (quote for Percolator-SOL pair)
    --side 2

# 2. Deploy bot with the config
python scripts/manage_controller.py deploy my_lp_bot --configs my_lp_config

# 3. Monitor status
python scripts/manage_controller.py status
```

**Key Parameters:**

| Parameter | Field | Default | Description |
|-----------|-------|---------|-------------|
| `--amount` | `total_amount_quote` | required | Amount in **quote asset** (2nd token). SOL for X-SOL pairs, USDC for X-USDC pairs. |
| `--side` | `side` | `0` | `0`=BOTH, `1`=BUY (quote only), `2`=SELL (base only) |
| `--width` | `position_width_pct` | `10` | Range width in % (e.g. `10` = ±10% around price). Already in pct — do not use decimals. |
| `--offset` | `position_offset_pct` | `1` | Center offset from current price in %. Already in pct. |
| `--rebalance-seconds` | `rebalance_seconds` | `300` | Seconds out-of-range before closing and reopening |
| `--rebalance-threshold` | `rebalance_threshold_pct` | `1` | Min price move % to trigger rebalance. Already in pct. |
| `--sell-max/--sell-min` | `sell_price_max/min` | `0` | Price limits for SELL side (`0` = no limit) |
| `--buy-max/--buy-min` | `buy_price_max/min` | `0` | Price limits for BUY side (`0` = no limit) |
| `--strategy-type` | `strategy_type` | `0` | Meteora shape: `0`=Spot (uniform), `1`=Curve (center-heavy), `2`=Bid-Ask (edge-heavy) |

### Single LP Executor (Alternative)

> **Reference:** See `references/lp_executor_guide.md` for state machine, single/double-sided positions, and limit range orders.

Creates ONE position with fixed bounds. Does NOT auto-rebalance.

```bash
python scripts/manage_executor.py create \
    --pool <pool_address> \
    --pair SOL-USDC \
    --quote-amount 100 \
    --lower 180 \
    --upper 185 \
    --side 1
```

**Key Parameters:**

| Parameter | Description |
|-----------|-------------|
| `--connector` | Must include `/clmm` suffix (default: `meteora/clmm`) |
| `--lower/--upper` | Position price bounds |
| `--base-amount/--quote-amount` | Token amounts (set one to 0 for single-sided) |
| `--side` | 0=BOTH, 1=BUY, 2=SELL |
| `--auto-close-above` | Auto-close when price above range (for limit orders) |
| `--auto-close-below` | Auto-close when price below range (for limit orders) |

### Monitor & Manage

**Check Status:**
```bash
# Bot status
python scripts/manage_controller.py status

# Executor list
python scripts/manage_executor.py list --type lp_executor

# Executor details
python scripts/manage_executor.py get <executor_id>

# Executor summary
python scripts/manage_executor.py summary
```

**Executor States:**
- `OPENING` - Creating position on-chain
- `IN_RANGE` - Position active, earning fees
- `OUT_OF_RANGE` - Price outside position bounds
- `CLOSING` - Removing position
- `FAILED` - Transaction failed

**Stop:**
```bash
# Stop bot (stops all its controllers)
python scripts/manage_controller.py stop my_lp_bot

# Stop individual executor (closes position)
python scripts/manage_executor.py stop <executor_id>

# Stop executor but keep position on-chain
python scripts/manage_executor.py stop <executor_id> --keep-position
```

### After Stopping — Analyze Results

**If the user ran an LP Executor** (via `manage_executor.py create` or direct API), immediately offer to analyze it:

> Your executor has been stopped. Want me to generate a performance dashboard?

Then run:
```bash
python scripts/visualize_lp_executor.py --id <executor_id>
```

The executor ID is returned when the executor is created (printed as `Executor ID: <id>`). If the user doesn't have it handy, fetch it from the API:

```bash
curl -s -u admin:admin -X POST http://localhost:8000/executors/search \
  -H "Content-Type: application/json" \
  -d '{"type":"lp_executor"}' | python3 -c "
import json,sys
data=json.load(sys.stdin)
items=data.get('data',data) if isinstance(data,dict) else data
for ex in (items if isinstance(items,list) else [items]):
    print(ex.get('executor_id') or ex.get('id'), ex.get('trading_pair'), ex.get('status'))
"
```

To also export the raw data to CSV:
```bash
python scripts/export_lp_executor.py --id <executor_id>
```

**If the user ran a Rebalancer Controller bot**, the data lives in a SQLite file — use `analyze-performance` with the SQLite-based scripts instead.

---

## Command: analyze-performance

Export data and generate visual dashboards from LP position events. Scripts are in this skill's `scripts/` directory.

### Which Script to Use?

**Always ask yourself: was this position deployed as an LP Executor (via `manage_executor.py` or direct API) or via a Rebalancer Controller bot?**

| How it was deployed | Script to use |
|---------------------|--------------|
| **LP Executor** — `manage_executor.py create` or direct `POST /executors/` API | `visualize_lp_executor.py --id <executor_id>` ✅ |
| **Rebalancer Controller** — `manage_controller.py deploy` (bot container, SQLite) | `visualize_lp_positions.py --pair <pair>` |
| Not sure? | Run `curl -s -u admin:admin -X POST http://localhost:8000/executors/search -H "Content-Type: application/json" -d '{"type":"lp_executor"}'` — if the executor ID appears, use the executor scripts |

**If the user has been running an LP Executor in this session** (executor ID is known from context), skip the question and go straight to:
```bash
python scripts/visualize_lp_executor.py --id <executor_id>
```

### Available Scripts

| Script | Purpose |
|--------|---------|
| `scripts/export_lp_positions.py` | Export LP position events to CSV (SQLite/bot-container based) |
| `scripts/visualize_lp_positions.py` | Generate HTML dashboard from position events (SQLite/bot-container based) |
| `scripts/export_lp_executor.py` | Export a single LP executor to CSV by `--id` (REST API, no SQLite) |
| `scripts/visualize_lp_executor.py` | Generate HTML dashboard for a single LP executor by `--id` (REST API) |

### Visualize LP Positions

Shows position ADD/REMOVE events from the blockchain. **Works for both running and stopped bots.**

```bash
# Basic usage (auto-detects database in data/)
python scripts/visualize_lp_positions.py --pair SOL-USDC

# Specify database explicitly
python scripts/visualize_lp_positions.py --db data/my_bot.sqlite --pair SOL-USDC

# Filter by connector
python scripts/visualize_lp_positions.py --pair SOL-USDC --connector meteora/clmm

# Last 24 hours only
python scripts/visualize_lp_positions.py --pair SOL-USDC --hours 24
```

**Dashboard Features:**
- KPI cards (total PnL, fees, IL, win/loss counts)
- Cumulative PnL & fees chart
- Price at open/close with LP range bounds
- Per-position PnL bar chart
- Duration vs PnL scatter plot
- Sortable positions table with Solscan links

### Export to CSV

```bash
# Export all position events
python scripts/export_lp_positions.py --db data/my_bot.sqlite

# Filter by trading pair
python scripts/export_lp_positions.py --pair SOL-USDC --output exports/positions.csv

# Show summary without exporting
python scripts/export_lp_positions.py --summary
```

### Executor Performance (API-based)

These scripts work directly from the **Hummingbot REST API** — no SQLite database needed.
Use them when executors were deployed via the API directly (e.g., via `manage_executor.py`),
because those do not always produce SQLite records the way bot containers do.

**Export a single LP executor to CSV:**

```bash
python scripts/export_lp_executor.py --id <executor_id>
python scripts/export_lp_executor.py --id <executor_id> --output exports/my_run.csv
python scripts/export_lp_executor.py --id <executor_id> --print   # JSON to stdout
```

CSV columns (LP executor schema):
- **Identity:** `id, account_name, controller_id, connector_name, trading_pair`
- **State:** `status, close_type, is_active, is_trading, error_count`
- **Timing:** `created_at, closed_at, close_timestamp, duration_seconds`
- **PnL:** `net_pnl_quote, net_pnl_pct, cum_fees_quote, filled_amount_quote`
- **Config (deployment):** `pool_address, lower_price, upper_price, base_amount_config, quote_amount_config, side, position_offset_pct, auto_close_above_range_seconds, auto_close_below_range_seconds, keep_position`
- **custom_info (live/final):** `state, position_address, current_price, lower_price_actual, upper_price_actual, base_amount_current, quote_amount_current, base_fee, quote_fee, fees_earned_quote, total_value_quote, unrealized_pnl_quote, position_rent, position_rent_refunded, tx_fee, out_of_range_seconds, max_retries_reached, initial_base_amount, initial_quote_amount`

**Visualize a single LP executor (HTML dashboard):**

```bash
python scripts/visualize_lp_executor.py --id <executor_id>
python scripts/visualize_lp_executor.py --id <executor_id> --output report.html
python scripts/visualize_lp_executor.py --id <executor_id> --no-open
```

**Dashboard panels:**
- KPI cards: status, net PnL, fees earned, duration, LP range
- Price chart with LP lower/upper bounds + open/close markers (5m KuCoin candles; auto-skipped for exotic pairs)
- Token balance bar: initial vs final base + quote amounts
- PnL breakdown: fees earned vs IL/price impact vs net PnL
- Full position summary table with Solscan links for pool and position addresses
- Dark theme (`#0d1117` / `#161b27`), responsive layout, Chart.js from CDN
- Auth auto-loaded from `.env` or `~/.hummingbot/.env` or `~/.env` (keys: `HUMMINGBOT_API_URL`, `API_USER`, `API_PASS`)

---

## Quick Reference

### Common Workflows

**Full Setup (first time):**
```bash
# 1. Deploy API
bash scripts/deploy_hummingbot_api.sh install

# 2. Start Gateway
bash scripts/setup_gateway.sh --rpc-url https://your-rpc-endpoint.com

# 3. Add wallet
python scripts/add_wallet.py add

# 4. Find pool
python scripts/list_meteora_pools.py --query SOL-USDC

# 5. Check bin_step
python scripts/get_meteora_pool.py <pool_address>

# 6. Create config and deploy
python scripts/manage_controller.py create-config my_lp --pool <pool_address> --pair SOL-USDC --amount 100
python scripts/manage_controller.py deploy my_bot --configs my_lp

# 7. Verify
python scripts/manage_controller.py status
```

**Analyze LP Positions:**
```bash
# Visualize
python scripts/visualize_lp_positions.py --pair SOL-USDC

# Export CSV
python scripts/export_lp_positions.py --pair SOL-USDC
```

### Checking Prerequisites

Before running commands that need the API or Gateway, verify they're running:

```bash
bash scripts/check_api.sh       # Is Hummingbot API running?
bash scripts/check_gateway.sh   # Is Gateway running? (also checks API)
```

Both support `--json` output. These scripts are also used internally by `setup_gateway.sh` and can be sourced by other shell scripts.

### Scripts Reference

| Script | Purpose |
|--------|---------|
| `check_api.sh` | Check if Hummingbot API is running (shared) |
| `check_gateway.sh` | Check if Gateway is running (shared) |
| `deploy_hummingbot_api.sh` | Install/upgrade/manage Hummingbot API |
| `setup_gateway.sh` | Start Gateway and configure RPC |
| `add_wallet.py` | Add wallets and check balances |
| `manage_gateway.py` | Advanced Gateway management |
| `list_meteora_pools.py` | Search and list pools |
| `get_meteora_pool.py` | Get pool details with liquidity chart |
| `manage_executor.py` | Create, list, stop LP executors |
| `manage_controller.py` | Create configs, deploy bots, get status |
| `export_lp_positions.py` | Export position events to CSV (SQLite/bot-container) |
| `visualize_lp_positions.py` | Generate HTML dashboard (SQLite/bot-container) |
| `export_lp_executor.py` | Export single LP executor to CSV by `--id` (REST API) |
| `visualize_lp_executor.py` | HTML dashboard for single LP executor by `--id` (REST API) |

### Error Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| "InvalidRealloc" | Position range too wide | Reduce `--width` (check bin_step limits) |
| State stuck "OPENING" | Transaction failed | Stop executor, reduce range, retry |
| "Insufficient balance" | Not enough tokens | Check wallet has tokens + 0.06 SOL for rent |
