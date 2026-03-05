---
name: xian-sdk
description: Build applications on the Xian blockchain using the xian-py Python SDK. Use when developing apps that interact with Xian — wallets, transactions, smart contracts, state queries, token transfers. Covers sync and async patterns.
---

# Xian SDK Skill

Build applications on [Xian](https://xian.org) using the [xian-py](https://github.com/xian-network/xian-py) Python SDK.

## Installation

```bash
pip install xian-py

# With Ethereum wallet support
pip install "xian-py[eth]"
```

## Quick Reference

```python
from xian_py import Xian, Wallet

wallet = Wallet()  # New wallet
xian = Xian('http://node:26657', wallet=wallet)

# Common operations
balance = xian.get_balance(wallet.public_key)
state = xian.get_state('contract', 'variable', 'key')
result = xian.send(amount=100, to_address='recipient')
result = xian.send_tx('contract', 'function', {'arg': 'value'})
result = xian.submit_contract('name', code)
```

## Wallets

### Basic Wallet

```python
from xian_py import Wallet

# Create new wallet (random seed)
wallet = Wallet()

# From existing private key
wallet = Wallet('ed30796abc4ab47a97bfb37359f50a9c362c7b304a4b4ad1b3f5369ecb6f7fd8')

print(wallet.public_key)   # Address
print(wallet.private_key)  # Keep secret!
```

### HD Wallet (BIP39/BIP32)

```python
from xian_py.wallet import HDWallet

# Create with new 24-word mnemonic
hd = HDWallet()
print(hd.mnemonic_str)  # Save this!

# Restore from mnemonic
hd = HDWallet('word1 word2 word3 ... word24')

# Derive Xian wallet
path = [44, 0, 0, 0, 0]  # m/44'/0'/0'/0'/0'
wallet = hd.get_wallet(path)

# Derive Ethereum wallet (requires eth extras)
eth_wallet = hd.get_ethereum_wallet(0)  # First account
eth_wallet2 = hd.get_ethereum_wallet(1)  # Second account
```

### Signing & Verification

```python
wallet = Wallet()

# Sign message
signature = wallet.sign_msg("Hello Xian")

# Verify
is_valid = wallet.verify_msg("Hello Xian", signature)

# Validate key format
Wallet.is_valid_key(wallet.public_key)  # True
```

## Blockchain Queries

```python
from xian_py import Xian

xian = Xian('http://node:26657')

# Balance (default: currency contract)
balance = xian.get_balance('address')

# Custom token balance
balance = xian.get_balance('address', contract='token_contract')

# Contract state
state = xian.get_state('contract_name', 'variable', 'key')

# Get contract source
source = xian.get_contract('contract_name', clean=True)
```

## Transactions

### Simple Token Transfer

```python
from xian_py import Xian, Wallet

wallet = Wallet('your_private_key')
xian = Xian('http://node:26657', wallet=wallet)

# Send tokens (auto stamp calculation)
result = xian.send(amount=100, to_address='recipient')

if result['success']:
    print(f"TX: {result['tx_hash']}")
```

### Contract Interaction

```python
# Call any contract function
result = xian.send_tx(
    contract='currency',
    function='transfer',
    kwargs={'to': 'recipient', 'amount': 1000}
)

# With custom token
result = xian.send_tx(
    contract='my_token',
    function='transfer',
    kwargs={'to': 'recipient', 'amount': 500}
)
```

### Stamp Estimation

```python
from xian_py.transaction import simulate_tx, get_nonce

# Simulate to get stamp cost
payload = {
    "contract": "currency",
    "function": "transfer",
    "kwargs": {"to": "recipient", "amount": 100},
    "sender": wallet.public_key,
}

result = simulate_tx('http://node:26657', payload)
print(f"Stamps needed: {result['stamps_used']}")
```

## Smart Contracts

### Deploy Contract

```python
code = '''
balances = Hash(default_value=0)

@construct
def seed():
    balances[ctx.caller] = 1_000_000

@export
def transfer(to: str, amount: float):
    assert amount > 0, "Amount must be positive"
    assert balances[ctx.caller] >= amount, "Insufficient balance"
    
    balances[ctx.caller] -= amount
    balances[to] += amount

@export
def balance_of(address: str) -> float:
    return balances[address]
'''

result = xian.submit_contract('my_token', code)
print(f"Deployed: {result['success']}")
```

### Contract Patterns

See `references/contract-patterns.md` for common patterns (tokens, access control, pausable, upgrades).

### Contract Validation

Validate against [Xian standards](https://github.com/xian-network/xian-standard-contracts):

```python
from xian_py.validator import validate_contract, XianStandard

is_valid, errors = validate_contract(code)  # XSC001 default

# Specific standard
is_valid, errors = validate_contract(code, standard=XianStandard.XSC001)

if not is_valid:
    print(errors)
```

### Read-Only Execution

Query contract without spending stamps:

```python
from xian_py.transaction import simulate_tx

payload = {
    "contract": "my_token",
    "function": "balance_of",
    "kwargs": {"address": "some_address"},
    "sender": wallet.public_key,
}

result = simulate_tx('http://node:26657', payload)
print(f"Balance: {result['result']}")
```

## Async Operations

For high-performance applications:

```python
import asyncio
from xian_py import XianAsync, Wallet

async def main():
    wallet = Wallet()
    
    async with XianAsync('http://node:26657', wallet=wallet) as xian:
        # Concurrent queries
        balance, state = await asyncio.gather(
            xian.get_balance(wallet.public_key),
            xian.get_state('currency', 'balances', 'address')
        )
        
        # Send transaction
        result = await xian.send(amount=100, to_address='recipient')

asyncio.run(main())
```

### Batch Operations

```python
async def check_balances(addresses: list[str]):
    async with XianAsync('http://node:26657') as xian:
        balances = await asyncio.gather(*[
            xian.get_balance(addr) for addr in addresses
        ])
        return dict(zip(addresses, balances))
```

### Sync Wrapper

Call async from sync code:

```python
from xian_py import XianAsync, run_sync

def get_balance_sync(address: str) -> float:
    async def _get():
        async with XianAsync('http://node:26657') as xian:
            return await xian.get_balance(address)
    return run_sync(_get())

balance = get_balance_sync('address')
```

## Encryption

Two-way encrypted messaging:

```python
from xian_py import Wallet
from xian_py.crypto import encrypt, decrypt_as_sender, decrypt_as_receiver

sender = Wallet()
receiver = Wallet()

# Encrypt
encrypted = encrypt(sender.private_key, receiver.public_key, "Secret message")

# Decrypt as sender
msg = decrypt_as_sender(sender.private_key, receiver.public_key, encrypted)

# Decrypt as receiver  
msg = decrypt_as_receiver(sender.public_key, receiver.private_key, encrypted)
```

## Error Handling

```python
from xian_py import Xian, XianException

try:
    result = xian.send_tx('contract', 'function', {})
except XianException as e:
    print(f"Blockchain error: {e}")
```

## Common Patterns

### Token Transfer Service

```python
class TokenService:
    def __init__(self, node_url: str, private_key: str):
        self.wallet = Wallet(private_key)
        self.xian = Xian(node_url, wallet=self.wallet)
    
    def transfer(self, to: str, amount: float, token: str = 'currency'):
        balance = self.xian.get_balance(self.wallet.public_key, contract=token)
        if balance < amount:
            raise ValueError(f"Insufficient: {balance} < {amount}")
        
        return self.xian.send_tx(token, 'transfer', {'to': to, 'amount': amount})
```

### DEX Swap

```python
async def swap(xian, dex: str, token_in: str, token_out: str, 
               amount: float, min_out: float):
    # Approve DEX
    await xian.send_tx(token_in, 'approve', {'to': dex, 'amount': amount})
    
    # Execute swap
    return await xian.send_tx(dex, 'swap', {
        'token_in': token_in,
        'token_out': token_out,
        'amount_in': amount,
        'min_amount_out': min_out
    })
```

## Resources

- [xian-py GitHub](https://github.com/xian-network/xian-py) — Full SDK docs
- [Xian Standard Contracts](https://github.com/xian-network/xian-standard-contracts) — Token standards
- [xian.org](https://xian.org) — Project site
