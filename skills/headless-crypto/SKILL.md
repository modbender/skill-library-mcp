---
name: headless-trading
description: "Autonomous trading for AI agents on Solana and BNB Chain. Use when: (1) executing token swaps on DEXs (Raydium, PancakeSwap), (2) checking token prices and balances, (3) monitoring liquidity pools, (4) implementing trading strategies, (5) managing portfolio positions. Supports headless execution without browser interaction."
---

# Headless Trading

Autonomous trading toolkit for AI agents on Solana (Raydium) and BNB Chain (PancakeSwap).

## Core Capabilities

### 1. Token Swaps
Execute swaps on decentralized exchanges without browser interaction:
- Raydium (Solana): SOL ↔ SPL tokens
- PancakeSwap (BNB Chain): BNB ↔ BEP20 tokens

### 2. Price Monitoring
Fetch real-time token prices:
- DEX liquidity pool prices
- Multiple pair support
- Slippage calculation

### 3. Portfolio Management
Check balances and positions:
- Native token balances (SOL, BNB)
- Token holdings across wallets
- Transaction history

### 4. Strategy Execution
Implement automated trading strategies:
- Limit orders (via monitoring + execution)
- DCA (Dollar Cost Averaging)
- Stop-loss / Take-profit
- Arbitrage opportunities

## Quick Start

### Prerequisites

1. **Private key** (environment variable or secure storage)
2. **RPC endpoint** (public or private node)
3. **Python 3.8+** with dependencies

### Installation

```bash
pip install solana web3 anchorpy raydium-py base58
pip install web3 pancakeswap-sdk
```

### Basic Swap Example

```python
from scripts.raydium_swap import swap_on_raydium

# Swap 0.1 SOL for USDC
tx_hash = swap_on_raydium(
    input_token="SOL",
    output_token="USDC",
    amount=0.1,
    slippage=1.0  # 1% slippage tolerance
)
```

## Workflow Decision Tree

**1. What chain are you trading on?**
- Solana → Use `raydium_*` scripts + See [references/raydium.md](references/raydium.md)
- BNB Chain → Use `pancakeswap_*` scripts + See [references/pancakeswap.md](references/pancakeswap.md)

**2. What operation do you need?**
- Get token price → `get_price.py`
- Check wallet balance → `get_balance.py`
- Execute swap → `swap.py`
- Monitor liquidity → `monitor_pool.py`

**3. What strategy are you implementing?**
- One-time trade → Direct swap
- Automated strategy → See [references/strategies.md](references/strategies.md)

## Trading Operations

### Get Token Price

```python
from scripts.get_price import get_token_price

# Get current price of a token
price = get_token_price(
    chain="solana",
    token_address="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    quote_token="SOL"
)
print(f"Price: {price} SOL")
```

### Check Wallet Balance

```python
from scripts.get_balance import get_balance

# Check SOL balance
balance = get_balance(
    chain="solana",
    wallet_address="YOUR_WALLET_ADDRESS"
)
print(f"Balance: {balance} SOL")
```

### Execute Swap

```python
from scripts.swap import execute_swap

# Swap tokens with slippage protection
result = execute_swap(
    chain="solana",
    input_token="SOL",
    output_token="USDC",
    amount=0.5,
    slippage=1.0,
    private_key="YOUR_PRIVATE_KEY"  # Use env var in production
)
```

### Monitor Liquidity Pool

```python
from scripts.monitor_pool import get_pool_info

# Get liquidity pool stats
pool_info = get_pool_info(
    chain="solana",
    token_a="SOL",
    token_b="USDC"
)
print(f"Liquidity: ${pool_info['liquidity']}")
print(f"24h Volume: ${pool_info['volume_24h']}")
```

## Security Best Practices

### 1. Private Key Management

**NEVER hardcode private keys.** Use environment variables or secure vaults:

```python
import os

PRIVATE_KEY = os.getenv("TRADING_PRIVATE_KEY")
if not PRIVATE_KEY:
    raise ValueError("TRADING_PRIVATE_KEY not set")
```

### 2. Slippage Protection

Always set reasonable slippage limits:
- Stablecoins: 0.1-0.5%
- Blue chips: 0.5-1%
- Low liquidity: 1-3% (risky)

### 3. Transaction Simulation

Test swaps on devnet/testnet first:

```python
result = execute_swap(
    chain="solana",
    input_token="SOL",
    output_token="USDC",
    amount=0.01,  # Small test amount
    slippage=1.0,
    simulate=True  # Dry run
)
```

### 4. Rate Limiting

Respect RPC rate limits:
- Public RPCs: ~5 req/sec
- Private RPCs: Check provider limits

### 5. Error Handling

Always handle transaction failures:

```python
try:
    tx_hash = execute_swap(...)
    print(f"Success: {tx_hash}")
except InsufficientFundsError:
    print("Not enough balance")
except SlippageExceededError:
    print("Price moved too much")
except RPCError as e:
    print(f"RPC failed: {e}")
```

## Common Patterns

### Pattern 1: Price Monitoring Bot

Monitor token prices and execute when conditions are met:

```python
from scripts.get_price import get_token_price
from scripts.swap import execute_swap
import time

TARGET_PRICE = 100  # USDC per token
CHECK_INTERVAL = 60  # seconds

while True:
    price = get_token_price(chain="solana", token_address="...", quote_token="USDC")
    
    if price <= TARGET_PRICE:
        execute_swap(
            chain="solana",
            input_token="USDC",
            output_token="TARGET_TOKEN",
            amount=100,
            slippage=1.0
        )
        break
    
    time.sleep(CHECK_INTERVAL)
```

### Pattern 2: DCA (Dollar Cost Averaging)

Buy fixed amounts at regular intervals:

```python
import schedule

def dca_buy():
    execute_swap(
        chain="solana",
        input_token="SOL",
        output_token="BTC",
        amount=0.1,  # 0.1 SOL every day
        slippage=1.0
    )

# Run daily at 9 AM
schedule.every().day.at("09:00").do(dca_buy)
```

### Pattern 3: Stop-Loss

Sell when price drops below threshold:

```python
ENTRY_PRICE = 100
STOP_LOSS_PERCENT = 10  # 10% loss

while True:
    current_price = get_token_price(...)
    loss_percent = ((ENTRY_PRICE - current_price) / ENTRY_PRICE) * 100
    
    if loss_percent >= STOP_LOSS_PERCENT:
        execute_swap(...)  # Sell position
        break
    
    time.sleep(60)
```

## Resources

### scripts/

Executable Python scripts for trading operations:

- `get_price.py` - Fetch token prices from DEXs
- `get_balance.py` - Check wallet balances
- `swap.py` - Execute token swaps
- `monitor_pool.py` - Get liquidity pool info
- `raydium_swap.py` - Raydium-specific swap implementation
- `pancakeswap_swap.py` - PancakeSwap-specific swap implementation

### references/

- `raydium.md` - Raydium DEX API reference and pool addresses
- `pancakeswap.md` - PancakeSwap DEX API reference
- `strategies.md` - Detailed trading strategy implementations
- `rpc_endpoints.md` - List of public/private RPC providers

## Limitations

- **Gas fees**: Transactions require native tokens (SOL, BNB)
- **Slippage**: High volatility can cause failed transactions
- **RPC reliability**: Public RPCs may be slow/unstable
- **MEV**: Transactions may be frontrun on popular pairs

## Troubleshooting

### "Insufficient funds"
- Check wallet balance with `get_balance.py`
- Ensure enough native token for gas fees

### "Slippage exceeded"
- Increase slippage tolerance (carefully)
- Wait for lower volatility
- Split large orders into smaller ones

### "Transaction failed"
- Check RPC endpoint is responsive
- Verify token addresses are correct
- Ensure wallet has approval for token spend

### "Rate limited"
- Switch to private RPC
- Add delays between requests
- Use multiple RPC endpoints
