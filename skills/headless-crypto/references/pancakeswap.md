# PancakeSwap DEX Reference

PancakeSwap is the leading DEX on BNB Chain, offering AMM trading for BEP20 tokens.

## Smart Contract Addresses

### PancakeSwap V2 (Recommended)

- **Router:** `0x10ED43C718714eb63d5aA57B78B54704E256024E`
- **Factory:** `0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73`
- **WBNB:** `0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c`

### PancakeSwap V3

- **Router:** `0x13f4EA83D0bd40E75C8222255bc855a974568Dd4`
- **Factory:** `0x0BFbCF9fa4f9C56B0F40a671Ad40E0805A091865`

## Common Token Addresses

### Stablecoins

- **BUSD:** `0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56`
- **USDT:** `0x55d398326f99059fF775485246999027B3197955`
- **USDC:** `0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d`

### Major Tokens

- **CAKE:** `0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82`
- **ETH:** `0x2170Ed0880ac9A755fd29B2688956BD959F933F8`
- **BTC:** `0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c`

## Router ABI (Essential Functions)

```json
[
  {
    "name": "swapExactTokensForTokens",
    "inputs": [
      {"name": "amountIn", "type": "uint256"},
      {"name": "amountOutMin", "type": "uint256"},
      {"name": "path", "type": "address[]"},
      {"name": "to", "type": "address"},
      {"name": "deadline", "type": "uint256"}
    ],
    "outputs": [{"name": "amounts", "type": "uint256[]"}]
  },
  {
    "name": "swapExactBNBForTokens",
    "inputs": [
      {"name": "amountOutMin", "type": "uint256"},
      {"name": "path", "type": "address[]"},
      {"name": "to", "type": "address"},
      {"name": "deadline", "type": "uint256"}
    ],
    "outputs": [{"name": "amounts", "type": "uint256[]"}],
    "payable": true
  },
  {
    "name": "getAmountsOut",
    "inputs": [
      {"name": "amountIn", "type": "uint256"},
      {"name": "path", "type": "address[]"}
    ],
    "outputs": [{"name": "amounts", "type": "uint256[]"}]
  }
]
```

## Swap Flow

### 1. Approve Token Spending

Before swapping, approve the router to spend your tokens:

```python
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed1.binance.org"))

# ERC20 approve ABI
approve_abi = [{
    "name": "approve",
    "inputs": [
        {"name": "spender", "type": "address"},
        {"name": "amount", "type": "uint256"}
    ],
    "outputs": [{"name": "", "type": "bool"}]
}]

token_contract = w3.eth.contract(address=TOKEN_ADDRESS, abi=approve_abi)

# Approve max amount
tx = token_contract.functions.approve(
    ROUTER_ADDRESS,
    2**256 - 1  # Max uint256
).build_transaction({
    'from': account.address,
    'gas': 100000,
    'gasPrice': w3.eth.gas_price,
    'nonce': w3.eth.get_transaction_count(account.address)
})

signed = account.sign_transaction(tx)
tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
```

### 2. Get Quote

```python
# Get expected output amount
amounts_out = router.functions.getAmountsOut(
    amount_in,
    [token_in, token_out]
).call()

expected_out = amounts_out[-1]
```

### 3. Execute Swap

```python
import time

deadline = int(time.time()) + 300  # 5 minutes

tx = router.functions.swapExactTokensForTokens(
    amount_in,
    min_amount_out,  # With slippage
    [token_in, token_out],
    recipient_address,
    deadline
).build_transaction({
    'from': account.address,
    'gas': 200000,
    'gasPrice': w3.eth.gas_price,
    'nonce': w3.eth.get_transaction_count(account.address)
})

signed = account.sign_transaction(tx)
tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
```

## Transaction Fees

- **Network fee:** Variable (0.0003-0.001 BNB typically)
- **PancakeSwap fee:** 0.25% of swap amount (V2)
- **Priority:** Gas price affects speed

## Slippage Calculation

```python
# Get quote
expected_output = router.functions.getAmountsOut(
    input_amount,
    [input_token, output_token]
).call()[-1]

# Apply slippage tolerance
slippage_percent = 1.0  # 1%
min_output = int(expected_output * (1 - slippage_percent / 100))
```

## Gas Optimization

### Estimate Gas

```python
gas_estimate = router.functions.swapExactTokensForTokens(
    amount_in,
    min_amount_out,
    path,
    recipient,
    deadline
).estimate_gas({'from': account.address})

# Add 20% buffer
safe_gas_limit = int(gas_estimate * 1.2)
```

### Get Current Gas Price

```python
# Current gas price
current_gas = w3.eth.gas_price

# Fast gas (1.2x current)
fast_gas = int(current_gas * 1.2)

# Use in transaction
tx = {..., 'gasPrice': fast_gas}
```

## Multi-Hop Swaps

For tokens without direct pairs, route through WBNB:

```python
# Swap TOKEN_A -> WBNB -> TOKEN_B
path = [TOKEN_A, WBNB, TOKEN_B]

amounts_out = router.functions.getAmountsOut(
    amount_in,
    path
).call()

# Execute
router.functions.swapExactTokensForTokens(
    amount_in,
    min_amount_out,
    path,  # Multi-hop path
    recipient,
    deadline
).transact()
```

## Error Handling

### Common Errors

**"PancakeRouter: INSUFFICIENT_OUTPUT_AMOUNT"**
- Slippage too low
- Pool liquidity changed
- Increase slippage or retry

**"PancakeRouter: EXPIRED"**
- Deadline passed
- Set longer deadline (e.g., +10 minutes)

**"execution reverted"**
- Token not approved
- Insufficient balance
- Check allowance and balance

### Check Allowance

```python
# Check current allowance
allowance = token_contract.functions.allowance(
    account.address,
    ROUTER_ADDRESS
).call()

if allowance < amount_to_swap:
    # Need to approve first
    approve_tx = token_contract.functions.approve(...)
```

## API Endpoints

### PancakeSwap Info API

**Base URL:** `https://api.pancakeswap.info/api/v2`

- `GET /tokens` - All tokens
- `GET /tokens/{address}` - Token info
- `GET /pairs` - All pairs
- `GET /pairs/{address}` - Pair info

### The Graph (Subgraph)

**Endpoint:** `https://api.thegraph.com/subgraphs/name/pancakeswap/exchange-v2`

Query pairs and pools with GraphQL.

## Testing on Testnet

**BSC Testnet:**
- RPC: `https://data-seed-prebsc-1-s1.binance.org:8545`
- Chain ID: 97
- Faucet: https://testnet.binance.org/faucet-smart

## Resources

- **PancakeSwap Docs:** https://docs.pancakeswap.finance
- **BSC Docs:** https://docs.bnbchain.org
- **Web3.py Docs:** https://web3py.readthedocs.io
