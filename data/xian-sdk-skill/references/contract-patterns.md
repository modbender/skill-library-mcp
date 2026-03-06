# Xian Contract Patterns

Common patterns for Xian smart contracts written in Python.

## Table of Contents

- [Basic Token (XSC001)](#basic-token-xsc001)
- [Access Control](#access-control)
- [Pausable Contract](#pausable-contract)
- [Upgradeable Pattern](#upgradeable-pattern)

## Basic Token (XSC001)

Minimal fungible token following XSC001 standard:

```python
balances = Hash(default_value=0)
metadata = Hash()

@construct
def seed():
    metadata['token_name'] = 'My Token'
    metadata['token_symbol'] = 'MTK'
    metadata['token_logo_url'] = 'https://example.com/logo.png'
    metadata['token_website'] = 'https://example.com'
    metadata['operator'] = ctx.caller
    
    # Initial supply to deployer
    balances[ctx.caller] = 1_000_000

@export
def transfer(amount: float, to: str):
    assert amount > 0, 'Amount must be positive'
    assert balances[ctx.caller] >= amount, 'Insufficient balance'
    
    balances[ctx.caller] -= amount
    balances[to] += amount

@export
def approve(amount: float, to: str):
    balances[ctx.caller, to] = amount

@export
def transfer_from(amount: float, to: str, main_account: str):
    assert amount > 0, 'Amount must be positive'
    assert balances[main_account, ctx.caller] >= amount, 'Not approved'
    assert balances[main_account] >= amount, 'Insufficient balance'
    
    balances[main_account, ctx.caller] -= amount
    balances[main_account] -= amount
    balances[to] += amount

@export
def balance_of(address: str) -> float:
    return balances[address]
```

## Access Control

Owner-only functions:

```python
owner = Variable()

@construct
def seed():
    owner.set(ctx.caller)

def only_owner():
    assert ctx.caller == owner.get(), 'Only owner'

@export
def admin_function():
    only_owner()
    # ... privileged logic

@export
def transfer_ownership(new_owner: str):
    only_owner()
    owner.set(new_owner)
```

Multi-role access:

```python
roles = Hash(default_value=False)

@construct
def seed():
    roles['admin', ctx.caller] = True

@export
def grant_role(role: str, account: str):
    assert roles['admin', ctx.caller], 'Only admin'
    roles[role, account] = True

@export
def revoke_role(role: str, account: str):
    assert roles['admin', ctx.caller], 'Only admin'
    roles[role, account] = False

@export
def minter_function():
    assert roles['minter', ctx.caller], 'Only minter'
    # ... minting logic
```

## Pausable Contract

Emergency stop pattern:

```python
paused = Variable()
owner = Variable()

@construct
def seed():
    owner.set(ctx.caller)
    paused.set(False)

def when_not_paused():
    assert not paused.get(), 'Contract is paused'

def only_owner():
    assert ctx.caller == owner.get(), 'Only owner'

@export
def pause():
    only_owner()
    paused.set(True)

@export
def unpause():
    only_owner()
    paused.set(False)

@export
def transfer(to: str, amount: float):
    when_not_paused()
    # ... transfer logic
```

## Upgradeable Pattern

Proxy pattern for upgrades:

```python
# Proxy contract
implementation = Variable()
owner = Variable()

@construct
def seed(impl_contract: str):
    implementation.set(impl_contract)
    owner.set(ctx.caller)

@export
def upgrade(new_impl: str):
    assert ctx.caller == owner.get(), 'Only owner'
    implementation.set(new_impl)

@export
def execute(function: str, kwargs: dict):
    impl = importlib.import_module(implementation.get())
    fn = getattr(impl, function)
    return fn(**kwargs)
```

## State Patterns

### Mapping with Default

```python
balances = Hash(default_value=0)

# No need to initialize - returns 0 for unknown keys
balance = balances['new_address']  # Returns 0
```

### Nested Mapping

```python
# Allowances: owner -> spender -> amount
allowances = Hash(default_value=0)

allowances[owner, spender] = 100
allowed = allowances[owner, spender]
```

### List-like Storage

```python
items = Hash()
item_count = Variable()

@construct
def seed():
    item_count.set(0)

@export
def add_item(data: str):
    idx = item_count.get()
    items[idx] = data
    item_count.set(idx + 1)

@export
def get_item(idx: int) -> str:
    assert idx < item_count.get(), 'Index out of bounds'
    return items[idx]
```

## Event Logging

Emit events for off-chain indexing:

```python
@export
def transfer(to: str, amount: float):
    # ... transfer logic
    
    # Log event (captured by BDS)
    return {
        'event': 'Transfer',
        'from': ctx.caller,
        'to': to,
        'amount': amount
    }
```

## Time-based Logic

```python
import datetime

lock_until = Hash()

@export
def lock_tokens(amount: float, days: int):
    unlock_time = datetime.datetime.now() + datetime.timedelta(days=days)
    lock_until[ctx.caller] = unlock_time
    # ... lock logic

@export
def unlock():
    assert datetime.datetime.now() >= lock_until[ctx.caller], 'Still locked'
    # ... unlock logic
```
