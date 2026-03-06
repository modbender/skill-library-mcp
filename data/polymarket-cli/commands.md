# Command Reference — Polymarket CLI

## Installation

```bash
# Homebrew (macOS/Linux) — recommended
brew tap Polymarket/polymarket-cli https://github.com/Polymarket/polymarket-cli
brew install polymarket

# Cargo (Rust)
cargo install polymarket-cli

# From source
git clone https://github.com/Polymarket/polymarket-cli
cd polymarket-cli && cargo install --path .
```

## Output Modes

```bash
polymarket -o table ...  # Human-readable (default)
polymarket -o json ...   # Machine-readable
```

Errors: table prints to stderr, JSON prints `{"error": "..."}` to stdout.

---

## Markets (No Wallet Needed)

```bash
# List markets
polymarket markets list --limit 10
polymarket markets list --active true --order volume_num

# Get specific market
polymarket markets get SLUG_OR_ID
polymarket markets get will-trump-win-the-2024-election

# Search
polymarket markets search "bitcoin" --limit 5

# Tags
polymarket markets tags MARKET_ID
```

Flags: `--limit`, `--offset`, `--order`, `--ascending`, `--active`, `--closed`

## Events (No Wallet Needed)

```bash
polymarket events list --limit 10
polymarket events list --tag politics --active true
polymarket events get EVENT_ID
polymarket events tags EVENT_ID
```

## Other Read-Only

```bash
# Tags
polymarket tags list
polymarket tags get politics
polymarket tags related politics

# Series
polymarket series list --limit 10
polymarket series get SERIES_ID

# Comments
polymarket comments list --entity-type event --entity-id 500
polymarket comments by-user 0xADDRESS

# Profiles
polymarket profiles get 0xADDRESS

# Sports
polymarket sports list
polymarket sports teams --league NFL --limit 32
```

---

## CLOB Queries (No Wallet Needed)

```bash
# Health
polymarket clob ok

# Prices
polymarket clob price TOKEN_ID --side buy
polymarket clob midpoint TOKEN_ID
polymarket clob spread TOKEN_ID

# Batch queries
polymarket clob batch-prices "TOKEN1,TOKEN2" --side buy
polymarket clob midpoints "TOKEN1,TOKEN2"
polymarket clob spreads "TOKEN1,TOKEN2"

# Order book
polymarket clob book TOKEN_ID
polymarket clob books "TOKEN1,TOKEN2"

# Last trade
polymarket clob last-trade TOKEN_ID

# Market info
polymarket clob market CONDITION_ID
polymarket clob markets

# Price history
polymarket clob price-history TOKEN_ID --interval 1d --fidelity 30
# Intervals: 1m, 1h, 6h, 1d, 1w, max

# Metadata
polymarket clob tick-size TOKEN_ID
polymarket clob fee-rate TOKEN_ID
polymarket clob neg-risk TOKEN_ID
polymarket clob time
polymarket clob geoblock
```

---

## Trading (Wallet Required)

### Orders

```bash
# Limit order
polymarket clob create-order \
  --token TOKEN_ID \
  --side buy --price 0.50 --size 10

# Market order
polymarket clob market-order \
  --token TOKEN_ID \
  --side buy --amount 5

# Batch orders
polymarket clob post-orders \
  --tokens "TOKEN1,TOKEN2" \
  --side buy \
  --prices "0.40,0.60" \
  --sizes "10,10"

# Cancel
polymarket clob cancel ORDER_ID
polymarket clob cancel-orders "ORDER1,ORDER2"
polymarket clob cancel-market --market CONDITION_ID
polymarket clob cancel-all
```

Order types: GTC (default), FOK, GTD, FAK. Add `--post-only` for limit orders.

### View Orders and Trades

```bash
polymarket clob orders
polymarket clob orders --market CONDITION_ID
polymarket clob order ORDER_ID
polymarket clob trades
```

### Balances

```bash
polymarket clob balance --asset-type collateral
polymarket clob balance --asset-type conditional --token TOKEN_ID
polymarket clob update-balance --asset-type collateral
```

---

## Rewards and API Keys (Wallet Required)

```bash
polymarket clob rewards --date 2024-06-15
polymarket clob earnings --date 2024-06-15
polymarket clob earnings-markets --date 2024-06-15
polymarket clob reward-percentages
polymarket clob current-rewards
polymarket clob market-reward CONDITION_ID

# Order scoring
polymarket clob order-scoring ORDER_ID
polymarket clob orders-scoring "ORDER1,ORDER2"

# API keys
polymarket clob api-keys
polymarket clob create-api-key
polymarket clob delete-api-key

# Account
polymarket clob account-status
polymarket clob notifications
polymarket clob delete-notifications "NOTIF1,NOTIF2"
```

---

## Public Data (No Wallet Needed)

```bash
# Portfolio
polymarket data positions 0xWALLET
polymarket data closed-positions 0xWALLET
polymarket data value 0xWALLET
polymarket data traded 0xWALLET

# Trade history
polymarket data trades 0xWALLET --limit 50

# Activity
polymarket data activity 0xWALLET

# Market data
polymarket data holders CONDITION_ID
polymarket data open-interest CONDITION_ID
polymarket data volume EVENT_ID

# Leaderboards
polymarket data leaderboard --period month --order-by pnl --limit 10
polymarket data builder-leaderboard --period week
polymarket data builder-volume --period month
```

---

## Approvals (Wallet Required, On-Chain)

```bash
# Check approvals
polymarket approve check
polymarket approve check 0xADDRESS

# Approve all (6 transactions, needs MATIC)
polymarket approve set
```

## Conditional Tokens (Wallet Required, On-Chain)

```bash
# Split USDC into YES/NO tokens
polymarket ctf split --condition CONDITION_ID --amount 10

# Merge tokens back to USDC
polymarket ctf merge --condition CONDITION_ID --amount 10

# Redeem after resolution
polymarket ctf redeem --condition CONDITION_ID
polymarket ctf redeem-neg-risk --condition CONDITION_ID --amounts "10,5"

# Calculate IDs (read-only)
polymarket ctf condition-id --oracle 0x... --question 0x... --outcomes 2
polymarket ctf collection-id --condition 0x... --index-set 1
polymarket ctf position-id --collection 0x...
```

`--amount` is in USDC (e.g., 10 = $10). Needs MATIC for gas.

## Bridge

```bash
# Deposit addresses
polymarket bridge deposit 0xWALLET

# Supported assets
polymarket bridge supported-assets

# Check status
polymarket bridge status 0xDEPOSIT_ADDRESS
```

---

## Wallet Management (USER-ONLY — agent must not run these)

These commands handle private keys. The user must run them directly:

```bash
polymarket wallet create          # Generate new
polymarket wallet create --force  # Overwrite existing
polymarket wallet import 0xKEY    # Import existing
polymarket wallet address         # Print address
polymarket wallet show            # Full info (may reveal sensitive data)
polymarket wallet reset           # Delete config (prompts)
polymarket wallet reset --force   # Delete without prompt
```

The agent should refuse to execute any wallet command and instruct the user to run it themselves.

## Interactive Shell

```bash
polymarket shell
# polymarket> markets list --limit 3
# polymarket> clob book TOKEN_ID
# polymarket> exit
```

## Utility

```bash
polymarket status     # API health
polymarket setup      # First-time wizard
polymarket upgrade    # Update CLI
polymarket --version
polymarket --help
```
