# LP Agent Scripts

Scripts for deploying infrastructure, exploring Meteora pools, managing LP positions, and analyzing performance.

## Scripts

**Infrastructure:**
- `deploy_hummingbot_api.sh` — Install/upgrade/manage Hummingbot API
- `setup_gateway.sh` — Start Gateway (with custom image), configure RPC per network
- `check_api.sh` — Shared: check if Hummingbot API is running (source or run directly)
- `check_gateway.sh` — Shared: check if Gateway is running (source or run directly)
- `add_wallet.py` — Add wallets and check balances

**Pool Explorer:**
- `list_meteora_pools.py` — Search and list Meteora DLMM pools
- `get_meteora_pool.py` — Get detailed pool information with liquidity distribution

**Position Management:**
- `manage_executor.py` — Create, monitor, and stop LP executors
- `manage_controller.py` — Deploy and manage LP Rebalancer controllers
- `manage_gateway.py` — Start/stop Gateway and configure RPC nodes (advanced)

**Analysis:**
- `export_lp_positions.py` — Export LP position events to CSV
- `visualize_lp_positions.py` — Generate interactive HTML dashboard from LP position events

---

## list_meteora_pools.py

Search and list Meteora DLMM pools by name, token, or address. Shows token mint addresses to identify correct tokens.

### Requirements

- Python 3.10+
- No pip dependencies — uses only the standard library

### Usage

```bash
# Top pools by 24h volume
python scripts/list_meteora_pools.py

# Search by token symbol
python scripts/list_meteora_pools.py --query SOL
python scripts/list_meteora_pools.py --query PERCOLATOR

# Sort by different metrics
python scripts/list_meteora_pools.py --query SOL --sort tvl
python scripts/list_meteora_pools.py --query SOL --sort apr
python scripts/list_meteora_pools.py --query SOL --sort fees

# Output as JSON
python scripts/list_meteora_pools.py --query SOL --json
```

### CLI Reference

```
list_meteora_pools.py [-q QUERY] [-s SORT] [--order ORDER] [-n LIMIT] [-p PAGE] [--json]
```

| Argument | Description |
|---|---|
| `-q`, `--query` | Search by pool name, token symbol, or address |
| `-s`, `--sort` | Sort by: `volume`, `tvl`, `fees`, `apr`, `apy` (default: `volume`) |
| `--order` | Sort order: `asc` or `desc` (default: `desc`) |
| `-n`, `--limit` | Number of results (default: 10, max: 1000) |
| `-p`, `--page` | Page number (default: 1) |
| `--json` | Output as JSON |

### Output

Outputs a markdown table with token mint addresses to identify correct tokens:

| # | Pool | Pool Address | Base (mint) | Quote (mint) | TVL | Vol 24h | Fees 24h | APR | Fee | Bin |
|---|------|--------------|-------------|--------------|-----|---------|----------|-----|-----|-----|
| 1 | Percolator-SOL | `ATrBUW..sPMSms` | Percolator (`8PzF..pump`) | SOL (`So11..1112`) | $8.9K | $15.5K | $348 | 3.9% | 2.00% | 100 |

---

## get_meteora_pool.py

Get detailed information about a specific Meteora DLMM pool. Fetches from both Meteora API (historical data) and Gateway (real-time price, liquidity distribution).

### Requirements

- Python 3.10+
- No pip dependencies — uses only the standard library
- Optional: Gateway running for real-time price and liquidity distribution chart

### Usage

```bash
# Get pool details (includes liquidity chart if Gateway is running)
python scripts/get_meteora_pool.py <pool_address>

# Skip Gateway API (faster, no liquidity distribution)
python scripts/get_meteora_pool.py <pool_address> --no-gateway

# Output as JSON
python scripts/get_meteora_pool.py <pool_address> --json
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GATEWAY_HOST` | `localhost` | Gateway API host |
| `GATEWAY_PORT` | `15888` | Gateway API port |

### Output Sections

1. **Pool Summary** - Current price, TVL, volume, fees, APR/APY, fee tier, bin step
2. **Token Info** - Base/quote token details (symbol, mint, price, decimals, market cap)
3. **Reserves** - Token amounts and USD values
4. **Volume & Fees by Time Window** - 30m, 1h, 4h, 12h, 24h metrics with Fee/TVL ratio
5. **Cumulative Metrics** - All-time volume and fees
6. **Real-Time Price** - Current price from Gateway (with subscript notation for small prices)
7. **Liquidity Distribution** - Vertical ASCII chart showing base/quote liquidity around current price
8. **Active Bin Info** - Active bin ID, min/max bin IDs, dynamic fee

### Liquidity Distribution Chart

The chart shows liquidity distribution like the Meteora UI:

```
Liquidity Distribution
▓ Percolator  ░ SOL  │ Current Price: 0.0₄169 SOL/Percolator

░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▓▓
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▓▓▓▓▓▓▓
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▓▓▓▓▓▓▓▓▓▓▓▓▓
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
──────────────────────────────┴─────────────────────────────
0.0₄125                    0.0₄169                   0.0₄225
```

- `▓` Base token (above current price = sell liquidity)
- `░` Quote token (below current price = buy liquidity)
- `│` Current price line
- Subscript notation: `0.0₄169` = 0.0000169

---

## export_lp_positions.py

Export LP position events from the `RangePositionUpdate` table to CSV. Events are stored immediately when they occur on-chain.

### Usage

```bash
# Export all LP position events (auto-detects database)
python scripts/export_lp_positions.py

# Show summary without exporting
python scripts/export_lp_positions.py --summary

# Filter by trading pair
python scripts/export_lp_positions.py --pair SOL-USDC

# Specify database
python scripts/export_lp_positions.py --db data/my_bot.sqlite

# Custom output path
python scripts/export_lp_positions.py -o exports/my_positions.csv
```

### CLI Reference

```
export_lp_positions.py [--db PATH] [--output PATH] [--pair PAIR] [--summary]
```

| Argument | Description |
|---|---|
| `--db PATH` | Path to SQLite database. Defaults to auto-detecting database with most LP data. |
| `-o`, `--output PATH` | Output CSV path. Defaults to `data/lp_positions_<timestamp>.csv`. |
| `-p`, `--pair PAIR` | Filter by trading pair (e.g., `SOL-USDC`). |
| `-s`, `--summary` | Show summary only, don't export. |

### Exported columns

- **id**: Database row ID
- **hb_id**: Hummingbot order ID
- **timestamp**: Unix timestamp in milliseconds
- **datetime**: Human-readable timestamp
- **tx_hash**: Transaction signature
- **connector**: Connector name (e.g., `meteora/clmm`)
- **action**: `ADD` or `REMOVE`
- **trading_pair**: Trading pair (e.g., `SOL-USDC`)
- **position_address**: LP position NFT address
- **lower_price, upper_price**: Position price bounds
- **mid_price**: Current price at time of event
- **base_amount, quote_amount**: Token amounts
- **base_fee, quote_fee**: Fees collected (for REMOVE)
- **position_rent**: SOL rent paid (ADD only)
- **position_rent_refunded**: SOL rent refunded (REMOVE only)

---

## visualize_lp_positions.py

Generate an interactive HTML dashboard from LP position events. Groups ADD/REMOVE events by position address to show complete position lifecycle with PnL, fees, and impermanent loss.

### Requirements

- Python 3.10+
- No pip dependencies — uses only the standard library
- A modern browser (the HTML loads React, Recharts, and Babel from CDN)

### Usage

```bash
# Basic usage (trading pair is required)
python scripts/visualize_lp_positions.py --pair SOL-USDC

# Filter by connector
python scripts/visualize_lp_positions.py --pair SOL-USDC --connector meteora/clmm

# Last 24 hours only
python scripts/visualize_lp_positions.py --pair SOL-USDC --hours 24

# Specify database
python scripts/visualize_lp_positions.py --db data/my_bot.sqlite --pair SOL-USDC

# Custom output path
python scripts/visualize_lp_positions.py --pair SOL-USDC -o reports/positions.html

# Skip auto-open
python scripts/visualize_lp_positions.py --pair SOL-USDC --no-open
```

### CLI Reference

```
visualize_lp_positions.py --pair PAIR [--db PATH] [--connector NAME] [--hours N] [-o PATH] [--no-open]
```

| Argument | Description |
|---|---|
| `-p`, `--pair PAIR` | **Required.** Trading pair (e.g., `SOL-USDC`). |
| `--db PATH` | Path to SQLite database. Defaults to auto-detecting database with most LP data. |
| `-c`, `--connector NAME` | Filter by connector (e.g., `meteora/clmm`). |
| `-H`, `--hours N` | Lookback period in hours (e.g., `24` for last 24 hours). |
| `-o`, `--output PATH` | Output HTML path. |
| `--no-open` | Don't auto-open the dashboard in the browser. |

### Dashboard Features

**KPI cards** — total PnL, fees earned (with bps calculation), IL (impermanent loss), win/loss counts, best/worst position, average duration.

**Cumulative PnL & Fees** — area chart showing PnL and fee accrual over closed positions.

**Price at Open/Close** — price when positions were opened vs closed, overlaid with LP range bounds.

**Per-Position PnL** — bar chart of each position's PnL. Click a bar to view details.

**Duration vs PnL** — scatter plot of position duration vs PnL.

**IL vs Fees Breakdown** — how impermanent loss compares to fees earned.

**Positions table** — sortable/filterable table with:
- Timing (opened, closed, duration)
- Price bounds and prices at ADD/REMOVE
- ADD liquidity with deposited amounts and Solscan TX link
- REMOVE liquidity with withdrawn amounts, fees, and Solscan TX link
- PnL breakdown (IL + fees)

---

## manage_executor.py

Create, monitor, and stop LP executors via hummingbot-api.

### Usage

```bash
# Create LP executor
python scripts/manage_executor.py create \
    --pool <pool_address> \
    --pair SOL-USDC \
    --quote-amount 100 \
    --lower 180 \
    --upper 185

# Get executor status
python scripts/manage_executor.py get <executor_id>

# List all executors
python scripts/manage_executor.py list
python scripts/manage_executor.py list --type lp_executor --json

# Get executor logs
python scripts/manage_executor.py logs <executor_id> --limit 50

# Stop executor (closes position)
python scripts/manage_executor.py stop <executor_id>

# Stop executor but keep position on-chain
python scripts/manage_executor.py stop <executor_id> --keep-position

# Get summary of all executors
python scripts/manage_executor.py summary
```

### Create Options

| Argument | Description |
|---|---|
| `--pool` | Pool address (required) |
| `--pair` | Trading pair e.g., SOL-USDC (required) |
| `--lower` | Lower price bound (required) |
| `--upper` | Upper price bound (required) |
| `--connector` | Connector name (default: meteora/clmm) |
| `--base-amount` | Base token amount (default: 0) |
| `--quote-amount` | Quote token amount |
| `--side` | 0=BOTH, 1=BUY, 2=SELL (default: 1) |
| `--auto-close-above` | Auto-close seconds when price above range |
| `--auto-close-below` | Auto-close seconds when price below range |
| `--strategy-type` | Meteora: 0=Spot, 1=Curve, 2=Bid-Ask |

---

## manage_controller.py

Deploy and manage LP Rebalancer controllers via hummingbot-api.

### Quick Start

```bash
# 1. Create LP Rebalancer config
python scripts/manage_controller.py create-config my_lp_config \
    --pool <pool_address> \
    --pair SOL-USDC \
    --amount 100 \
    --side 1 \
    --width 0.5 \
    --offset 0.01 \
    --rebalance-seconds 60 \
    --sell-max 100 \
    --sell-min 75 \
    --buy-max 90 \
    --buy-min 70

# 2. Deploy bot with the config
python scripts/manage_controller.py deploy my_lp_bot --configs my_lp_config

# 3. Monitor
python scripts/manage_controller.py status
```

### Usage

```bash
# Get LP Rebalancer config template
python scripts/manage_controller.py template

# Create LP Rebalancer config (see Quick Start for full example)
python scripts/manage_controller.py create-config my_lp_config --pool <address> --pair SOL-USDC

# List all configs
python scripts/manage_controller.py list-configs

# Get config details
python scripts/manage_controller.py describe-config my_lp_config

# Deploy bot with controller config(s)
python scripts/manage_controller.py deploy my_bot --configs my_lp_config
python scripts/manage_controller.py deploy my_bot --configs config1 config2  # Multiple controllers

# Get active bots status
python scripts/manage_controller.py status

# Get specific bot status
python scripts/manage_controller.py bot-status my_bot

# Stop a bot
python scripts/manage_controller.py stop my_bot

# Stop and archive a bot
python scripts/manage_controller.py stop-and-archive my_bot

# Delete a config
python scripts/manage_controller.py delete-config my_lp_config
```

### Create-Config Options

| Argument | Description |
|---|---|
| `--pool` | Pool address (required) |
| `--pair` | Trading pair e.g., SOL-USDC (required) |
| `--connector` | Connector name (default: meteora/clmm) |
| `--network` | Network (default: solana-mainnet-beta) |
| `--amount` | Total amount in quote currency (default: 50) |
| `--side` | 0=BOTH, 1=BUY, 2=SELL (default: 1) |
| `--width` | Position width % (default: 0.5) |
| `--offset` | Position offset % (default: 0.01) |
| `--rebalance-seconds` | Seconds out-of-range before rebalancing (default: 60) |
| `--rebalance-threshold` | Price % beyond bounds before timer starts (default: 0.1) |
| `--sell-max` | Sell price max (anchor point) |
| `--sell-min` | Sell price min |
| `--buy-max` | Buy price max |
| `--buy-min` | Buy price min (anchor point) |
| `--strategy-type` | Meteora: 0=Spot, 1=Curve, 2=Bid-Ask (default: 0) |

### Deploy Options

| Argument | Description |
|---|---|
| `bot_name` | Bot instance name (required) |
| `--configs` | Controller config name(s) (required) |
| `--account` | Credentials profile (default: master_account) |
| `--image` | Docker image (default: hummingbot/hummingbot:latest) |
| `--max-global-drawdown` | Max global drawdown in quote |
| `--max-controller-drawdown` | Max controller drawdown in quote |
| `--script-config` | Script config name (auto-generated if not provided) |
| `--headless` | Run in headless mode |

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HUMMINGBOT_API_URL` | `http://localhost:8000` | Hummingbot API URL |
| `API_USER` | `admin` | API username |
| `API_PASS` | `admin` | API password |

Scripts check for `.env` in: `./hummingbot-api/.env` → `~/.hummingbot/.env` → `.env`

---

## manage_gateway.py

Start/stop Gateway and configure RPC nodes via hummingbot-api.

### Usage

```bash
# Check Gateway status
python scripts/manage_gateway.py status

# Start Gateway
python scripts/manage_gateway.py start
python scripts/manage_gateway.py start --passphrase mypassword --port 15888

# Stop Gateway
python scripts/manage_gateway.py stop

# Restart Gateway
python scripts/manage_gateway.py restart

# Get Gateway logs
python scripts/manage_gateway.py logs
python scripts/manage_gateway.py logs --limit 200

# List all networks
python scripts/manage_gateway.py networks

# Get network config
python scripts/manage_gateway.py network solana-mainnet-beta

# Set custom RPC node (avoid rate limits)
python scripts/manage_gateway.py network solana-mainnet-beta --node-url https://my-rpc.example.com
```

### Commands

| Command | Description |
|---|---|
| `status` | Check if Gateway is running |
| `start` | Start Gateway container |
| `stop` | Stop Gateway container |
| `restart` | Restart Gateway container |
| `logs` | Get Gateway container logs |
| `networks` | List all available networks |
| `network <id>` | Get network config |
| `network <id> --node-url <url>` | Set custom RPC node URL |

### Custom RPC Nodes

Gateway uses public RPC nodes by default, which can hit rate limits. Set your own RPC endpoint:

```bash
# Solana mainnet
python scripts/manage_gateway.py network solana-mainnet-beta --node-url https://my-helius-endpoint.com

# Check the config
python scripts/manage_gateway.py network solana-mainnet-beta
```

Popular Solana RPC providers:
- [Helius](https://helius.dev/) - Free tier available
- [QuickNode](https://quicknode.com/)
- [Alchemy](https://alchemy.com/)
- [Triton](https://triton.one/)

---

## deploy_hummingbot_api.sh

Install, upgrade, and manage the Hummingbot API trading infrastructure.

### Requirements

- Docker and Docker Compose
- Git

### Usage

```bash
# Check installation status
bash scripts/deploy_hummingbot_api.sh status

# Install (interactive)
bash scripts/deploy_hummingbot_api.sh install

# Install with defaults (non-interactive, admin/admin)
bash scripts/deploy_hummingbot_api.sh install --defaults

# Upgrade
bash scripts/deploy_hummingbot_api.sh upgrade

# View logs
bash scripts/deploy_hummingbot_api.sh logs

# Reset (stop and remove)
bash scripts/deploy_hummingbot_api.sh reset
```

### Commands

| Command | Description |
|---|---|
| `status` | Check if Hummingbot API is installed and running |
| `install` | Clone repo and deploy (use `--defaults` for non-interactive) |
| `upgrade` | Pull latest and redeploy |
| `logs` | Show container logs |
| `reset` | Stop containers and remove installation |

---

## check_api.sh

Shared check script: verifies Hummingbot API is running. Can be sourced by other scripts or run directly.

### Usage

```bash
# Run directly
bash scripts/check_api.sh
bash scripts/check_api.sh --json

# Source in another script
source scripts/check_api.sh
check_api || echo "API not running"
```

---

## check_gateway.sh

Shared check script: verifies Gateway is running (also checks API). Can be sourced or run directly.

### Usage

```bash
# Run directly
bash scripts/check_gateway.sh
bash scripts/check_gateway.sh --json

# Source in another script
source scripts/check_gateway.sh
check_gateway || echo "Gateway not running"
```

---

## setup_gateway.sh

Start Gateway (with optional custom image), check status, and configure RPC endpoints per network. Gateway is required for all LP operations.

### Requirements

- Hummingbot API running (install with `deploy_hummingbot_api.sh`) — checked automatically via `check_api.sh`
- Python 3.10+

### Usage

```bash
# Check Gateway status
bash scripts/setup_gateway.sh --status

# Start Gateway with defaults
bash scripts/setup_gateway.sh

# Start with custom image (e.g., development build)
bash scripts/setup_gateway.sh --image hummingbot/gateway:development

# Start with custom RPC (recommended)
bash scripts/setup_gateway.sh --rpc-url https://your-rpc-endpoint.com

# Configure RPC for a different network
bash scripts/setup_gateway.sh --network ethereum-mainnet --rpc-url https://your-eth-rpc.com

# Custom passphrase and port
bash scripts/setup_gateway.sh --passphrase mypassword --port 15888
```

### Options

| Option | Default | Description |
|---|---|---|
| `--status` | | Check status only, don't start |
| `--image IMAGE` | `hummingbot/gateway:latest` | Docker image to use |
| `--passphrase TEXT` | `hummingbot` | Gateway passphrase |
| `--rpc-url URL` | | Custom RPC endpoint for `--network` |
| `--network ID` | `solana-mainnet-beta` | Network to configure RPC for |
| `--port PORT` | `15888` | Gateway port |

---

## add_wallet.py

Add and manage wallets via hummingbot-api Gateway.

### Requirements

- Python 3.10+
- No pip dependencies — uses only the standard library
- Gateway running (start with `setup_gateway.sh`)

### Usage

```bash
# List connected wallets
python scripts/add_wallet.py list

# Add wallet (prompted for private key — secure)
python scripts/add_wallet.py add

# Add wallet with private key
python scripts/add_wallet.py add --private-key <BASE58_KEY>

# Check balances
python scripts/add_wallet.py balances --address <WALLET_ADDRESS>

# Check specific tokens
python scripts/add_wallet.py balances --address <WALLET_ADDRESS> --tokens SOL USDC
```

### Commands

| Command | Description |
|---|---|
| `list` | List all connected wallets |
| `add` | Add a wallet (prompted or via `--private-key`) |
| `balances` | Get wallet token balances |

### Add Options

| Option | Description |
|---|---|
| `--private-key` | Private key in base58. Omit to be prompted securely. |
| `--chain` | Blockchain (default: solana) |
| `--network` | Network (default: mainnet-beta) |

### Balances Options

| Option | Description |
|---|---|
| `--address` | Wallet address (required) |
| `--tokens` | Specific token symbols to check |
| `--chain` | Blockchain (default: solana) |
| `--network` | Network (default: mainnet-beta) |
| `--all` | Show zero balances too |

---

## Notes

- All Python scripts use only the standard library (no pip install required)
- Shell scripts require Docker, Docker Compose, and Git
- The HTML dashboard is fully self-contained (data inlined as JSON), shareable and archivable
- LP position events are stored immediately on-chain, so analysis works for both running and stopped bots
