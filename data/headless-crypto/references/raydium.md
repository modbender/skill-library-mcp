# Raydium DEX Reference

Raydium is the leading AMM on Solana, providing liquidity and trading for SPL tokens.

## API Endpoints

### Jupiter Aggregator (Recommended)

Jupiter routes through Raydium and other DEXs for best prices.

**Base URL:** `https://quote-api.jup.ag/v6`

**Endpoints:**

- `GET /quote` - Get swap quote
- `POST /swap` - Get swap transaction
- `GET /tokens` - List supported tokens

### Raydium API v3

**Base URL:** `https://api-v3.raydium.io`

**Endpoints:**

- `GET /pools/info/ids?ids={pool_id}` - Pool info
- `GET /main/pairs` - All trading pairs
- `GET /main/price` - Token prices

## Common Token Addresses

### Stablecoins

- **USDC:** `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`
- **USDT:** `Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB`

### Major Tokens

- **SOL (wrapped):** `So11111111111111111111111111111111111111112`
- **RAY:** `4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R`
- **mSOL:** `mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So`

### Popular Memecoins

- **BONK:** `DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263`
- **WIF:** `EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm`

## Pool Structures

Raydium V4 pools have this structure:

```
Pool {
  id: PublicKey,
  base_mint: PublicKey,
  quote_mint: PublicKey,
  lp_mint: PublicKey,
  base_vault: PublicKey,
  quote_vault: PublicKey,
  open_orders: PublicKey,
  target_orders: PublicKey,
  withdraw_queue: PublicKey,
  lp_vault: PublicKey,
  market: PublicKey,
  market_program: PublicKey,
  market_authority: PublicKey
}
```

## Swap Flow

1. **Get pool info** - Find the pool for your pair
2. **Calculate amounts** - Determine input/output with slippage
3. **Build transaction** - Create swap instruction
4. **Sign & send** - Submit to network
5. **Confirm** - Wait for confirmation

## Slippage Calculation

```python
# Get quote from Jupiter
quote_response = requests.get(
    "https://quote-api.jup.ag/v6/quote",
    params={
        "inputMint": input_token,
        "outputMint": output_token,
        "amount": amount_lamports,
        "slippageBps": slippage * 100  # Convert % to basis points
    }
)

# Expected output
expected_out = quote_response["outAmount"]

# Minimum output (with slippage)
min_out = expected_out * (1 - slippage / 100)
```

## Transaction Fees

- **Network fee:** ~0.000005 SOL per transaction
- **Priority fee:** Optional (0.0001-0.001 SOL for faster execution)
- **Raydium fee:** 0.25% of swap amount

## Rate Limits

### Public RPCs

- **Solana mainnet:** ~10 req/sec
- **Helius:** 50 req/sec (free tier)
- **QuickNode:** 25 req/sec (free tier)

### Jupiter API

- **Quote endpoint:** 600 req/min
- **Swap endpoint:** 120 req/min

## Example: Direct Pool Swap

```python
from solana.rpc.api import Client
from solana.transaction import Transaction

# Connect to Solana
client = Client("https://api.mainnet-beta.solana.com")

# Build swap instruction
swap_instruction = raydium.swap(
    pool_id="POOL_ADDRESS",
    user_source="USER_TOKEN_ACCOUNT",
    user_destination="USER_TOKEN_ACCOUNT",
    amount_in=1000000,  # 1 USDC (6 decimals)
    minimum_amount_out=900000  # With slippage
)

# Create transaction
transaction = Transaction()
transaction.add(swap_instruction)

# Sign and send
response = client.send_transaction(transaction, signer)
```

## Troubleshooting

### "Program failed to complete"

- Increase compute units
- Add priority fee
- Check token account exists

### "Slippage tolerance exceeded"

- Pool has low liquidity
- High volatility
- Increase slippage or wait

### "Insufficient SOL for fee"

- Need at least 0.001 SOL for transaction
- Keep buffer for rent exemption

## Resources

- **Raydium Docs:** https://docs.raydium.io
- **Jupiter Docs:** https://docs.jup.ag
- **Solana Cookbook:** https://solanacookbook.com
