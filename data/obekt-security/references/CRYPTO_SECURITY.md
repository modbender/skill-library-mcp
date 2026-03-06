# Cryptocurrency and Blockchain Security Guide

Security recommendations and patterns specific to cryptocurrency and blockchain operations in agent skills.

## Critical Warning

🚨 **Blockchain transactions are irreversible.** Once a transaction is signed and broadcast, it cannot be reversed.

**Never:**
- Never hardcode private keys or mnemonics
- Never sign transactions without explicit approval
- Never expose wallet credentials in any form
- Never broadcast transactions without verification

---

## 1. Wallet Key Security

### 1.1 Key Generation

**Best Practices:**
```python
from eth_account import Account
import secrets

# GOOD: Use library functions with secure randomness
account = Account.create()
private_key = account.key.hex()
address = account.address

# The private_key must NEVER be committed to version control
print(f"Private Key: {private_key}")  # ⚠️ WARNING: Only output once, then delete
```

**Never Do:**
```python
# NEVER hardcode keys
PRIVATE_KEY = "0xabc123456789def..."

# NEVER predict keys (they will be drained instantly)
for i in range(1000):
    private_key = format(i, '064x')  # DO NOT!
```

---

### 1.2 Key Storage

**Best Practices:**

1. **Environment Variables (Basic):**
```python
import os
from eth_account import Account

# Load from environment
private_key = os.getenv('WALLET_PRIVATE_KEY')
if not private_key:
    raise ValueError("WALLET_PRIVATE_KEY not set in environment")

account = Account.from_key(private_key)
```

2. **Environment File (Development Only - Never Commit):**
```bash
# .env (ADD TO .gitignore!)
WALLET_PRIVATE_KEY=0xabc123456789def...
WALLET_MNEMONIC="word1 word2 word3 ... word12"
```

```python
from dotenv import load_dotenv

load_dotenv()  # Load .env file
private_key = os.getenv('WALLET_PRIVATE_KEY')
```

3. **Secrets Manager (Production):**
```python
import boto3

def get_wallet_secret(secret_name):
    """Retrieve wallet secret from AWS Secrets Manager"""
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']
```

**Security Rules:**
- [ ] Never commit private keys to git
- [ ] Never log private keys
- [ ] Never print private keys in output
- [ ] Store keys encrypted at rest
- [ ] Use proper secret management

---

## 2. Transaction Safety

### 2.1 Transaction Validation

Before signing any transaction, validate:

```python
from web3 import Web3
from eth_account import Account

def safe_transaction_sign(account, tx_data):
    """Sign transaction with safety checks"""

    # 1. Validate recipient address
    if not Web3.is_address(tx_data['to']):
        raise ValueError("Invalid recipient address")

    # 2. Validate amount
    amount_wei = int(tx_data['value'])
    amount_eth = Web3.from_wei(amount_wei, 'ether')

    if amount_wei <= 0:
        raise ValueError("Transaction amount must be positive")

    # 3. Check against limits
    MAX_TX_AMOUNT_ETH = 10.0
    if float(amount_eth) > MAX_TX_AMOUNT_ETH:
        raise ValueError(f"Transaction amount ({amount_eth}) exceeds limit ({MAX_TX_AMOUNT_ETH})")

    # 4. Validate gas settings
    if 'gas' not in tx_data:
        tx_data['gas'] = Web3.eth.estimate_gas(tx_data)

    if 'gasPrice' not in tx_data:
        tx_data['gasPrice'] = Web3.eth.gas_price

    # 5. Log transaction details for review
    print(f"Transaction to sign:")
    print(f"  To: {tx_data['to']}")
    print(f"  Amount: {amount_eth} ETH")
    print(f"  Gas: {tx_data['gas']}")
    print(f"  Gas Price: {Web3.from_wei(tx_data['gasPrice'], 'gwei')} gwei")
    print(f"  Estimated Fee: {Web3.from_wei(tx_data['gas'] * tx_data['gasPrice'], 'ether')} ETH")

    # 6. Get explicit confirmation
    confirm = input("Sign this transaction? (yes/no): ")
    if confirm.lower() != 'yes':
        raise ValueError("Transaction cancelled by user")

    # 7. Sign transaction
    signed_tx = account.sign_transaction(tx_data)
    return signed_tx
```

---

### 2.2 Approval Safety

For ERC20 token approvals:

```python
def safe_approve_token(web3, account, token_address, spender_address, amount):
    """Safe token approval with checks"""

    # 1. Validate addresses
    if not Web3.is_address(token_address):
        raise ValueError("Invalid token address")

    if not Web3.is_address(spender_address):
        raise ValueError("Invalid spender address")

    # 2. Check spender is not blacklisted (maintain a list)
    BLACKLISTED_SPENDERS = {
        '0x...',
        '0x...',
    }

    if spender_address.lower() in [addr.lower() for addr in BLACKLISTED_SPENDERS]:
        raise ValueError("Spender address is blacklisted")

    # 3. Load token contract to check decimals
    token_abi = [
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "type": "function"
        },
        {
            "constant": False,
            "inputs": [
                {"name": "_spender", "type": "address"},
                {"name": "_value", "type": "uint256"}
            ],
            "name": "approve",
            "outputs": [{"name": "", "type": "bool"}],
            "type": "function"
        }
    ]

    token = web3.eth.contract(address=token_address, abi=token_abi)
    decimals = token.functions.decimals().call()

    # 4. Validate amount limits
    MAX_APPROVAL_ETH = 1000.0
    amount_eth =amount / (10 ** decimals)

    if float(amount_eth) > MAX_APPROVAL_ETH:
        raise ValueError(f"Approval amount ({amount_eth}) exceeds limit ({MAX_APPROVAL_ETH})")

    # 5. Explicit confirmation for large approvals
    print(f"Approving {spender_address} to spend {amount_eth} tokens")
    print(f"Token: {token_address}")
    confirm = input("Approve this transaction? (yes/no): ")

    if confirm.lower() != 'yes':
        raise ValueError("Approval cancelled")

    # 6. Build and sign transaction
    tx = token.functions.approve(spender_address, amount).build_transaction({
        'from': account.address,
        'nonce': web3.eth.get_transaction_count(account.address),
        'gas': 100000,
        'gasPrice': web3.eth.gas_price
    })

    signed_tx = account.sign_transaction(tx)
    return signed_tx
```

---

## 3. Smart Contract Interactions

### 3.1 Contract Verification

Before interacting with smart contracts:

```python
def verify_contract(web3, contract_address):
    """Basic contract verification checks"""

    # 1. Check if address is a contract (has code)
    code = web3.eth.get_code(contract_address)
    if code == b'' or code == b'0x':
        raise ValueError("Address is not a contract")

    # 2. Check contract has been deployed for some time
    # Prevent interacting with brand new contracts until verified
    contract_info = web3.eth.get_block(web3.eth.get_transaction_receipt(web3.eth.get_transaction_by_block(0, 0).hash)['blockHash'])
    # Add actual deployment check logic

    # 3. Known good contracts (whitelist)
    KNOWN_GOOD = {
        # Uniswap V2 Router
        '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
        # USDC
        '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    }

    if contract_address.lower() in [addr.lower() for addr in KNOWN_GOOD]:
        print("✅ Contract is in known-good list")
        return True

    print("⚠️  Contract is not in known-good list")
    print("⚠️  Proceed with caution")

    return False
```

---

### 3.2 Reentrancy Protection

If building contracts, use reentrancy guards:

```python
# ReentrancyGuard (example for Solidity)
contract ReentrancyGuard {
    bool private locked;

    modifier noReentrancy() {
        require(!locked, "Reentrant call");
        locked = true;
        _;
        locked = false;
    }

    function safeWithdraw() external noReentrancy {
        // Withdraw logic here
    }
}
```

When interacting with contracts, be aware of reentrancy risks.

---

### 3.3 Unlimited Approval Risk

Never use unlimited approvals (`uint256` or very large amounts) unless necessary:

```python
import math

# BAD: Unlimited approval
MAX_UINT256 = 2**256 - 1
token.functions.approve(spender, MAX_UINT256)

# GOOD: Limited approval
amount = int(amount_needed * 1.1 * (10 ** decimals))  # 10% buffer
token.functions.approve(spender, amount)

# ALWAYS: Revoke approval when done
token.functions.approve(spender, 0)
```

---

## 4. Wallet Drains and Scams

### 4.1 Common Attack Patterns

**Signature Requests:**
- Be wary of requests to `signTypedData` without clear purpose
- Check permit signatures carefully
- Verify message structure

**Permit/EIP-2612:**
```python
# Check permit parameters carefully
def validate_permit(permit):
    """
    Permit structure:
    owner, spender, value, nonce, deadline
    """
    if permit['value'] > MAX_AMOUNT:
        raise ValueError("Permit amount too large")

    if permit['deadline'] > MAX_DEADLINE:
        raise ValueError("Permit deadline too far in future")

    # Check spender is not blacklisted
    if permit['spender'] in BLACKLISTED_SPENDERS:
        raise ValueError("Permit to blacklisted spender")
```

---

### 4.2 Drained Wallet Recovery

If wallet is drained:

1. **Do NOT use the same keys again**
   - Generate new wallet
   - Move remaining assets to new wallet

2. **Do NOT send funds to stolen addresses**
   - Some scams claim "send X ETH to recover"
   - These are ALWAYS scams

3. **Report the theft**
   - Contact exchanges if funds went through them
   - Report to law enforcement
   - Notify affected parties

4. **Audit where the key was exposed**
   - Check git history
   - Check logs
   - Check environment variables
   - Check shared credentials

---

## 5. Network Security

### 5.1 RPC Endpoints

**Best Practices:**
```python
# GOOD: Use reputable RPC providers
RPC_ENDPOINTS = {
    'ethereum': 'https://eth.llamarpc.com',
    'polygon': 'https://polygon.llamarpc.com',
    'base': 'https://base.llamarpc.com',
}

web3 = Web3(Web3.HTTPProvider(RPC_ENDPOINTS['ethereum']))

# Fallback RPCs
for endpoint in RPC_ENDPOINTS['ethereum']:
    try:
        web3 = Web3(Web3.HTTPProvider(endpoint))
        if web3.is_connected():
            break
    except Exception:
        continue
```

**Never:**
- Use unverified RPC endpoints
- Use HTTP for production (use HTTPS)
- Use endpoints that require authentication in client code

---

### 5.2 Chain ID Verification

Always verify chain ID before transactions:

```python
def verify_chain(web3, expected_chain_id):
    """Verify connected to correct chain"""
    chain_id = web3.eth.chain_id

    if chain_id != expected_chain_id:
        raise ValueError(
            f"Wrong chain! Expected {expected_chain_id}, got {chain_id}"
        )

    return True

# Usage for Base chain
EXPECTED_CHAIN_IDS = {
    'mainnet': 8453,
    'goerli': 84531,
}

verify_chain(web3, EXPECTED_CHAIN_IDS['mainnet'])
```

---

## 6. Testing and Development

### 6.1 Testnet Safety

**Always work on testnets first:**

```python
# Use testnet for development
TESTNET_CHAIN_IDS = {
    'ethereum': 5,   # Goerli
    'polygon': 80001, # Mumbai
    'base': 84531,   # Base Goerli
}

# Verify testnet before real operations
assert web3.eth.chain_id in TESTNET_CHAIN_IDS.values(), "Not on testnet!"
```

**Faucet for test tokens:**
- Get test ETH from faucets
- Never mix mainnet and testnet keys
- Clearly label testnet funds

---

### 6.2 Dry Run Transactions

Before executing on mainnet:

```python
def dry_run_transaction(web3, tx_data):
    """Simulate transaction without executing"""

    try:
        gas_estimate = web3.eth.estimate_gas(tx_data)
        gas_price = web3.eth.gas_price
        cost_eth = Web3.from_wei(gas_estimate * gas_price, 'ether')

        print(f"Dry run successful")
        print(f"Gas estimate: {gas_estimate}")
        print(f"Estimated cost: {cost_eth} ETH")

        return True
    except Exception as e:
        print(f"Dry run failed: {e}")
        return False

# Always dry run before real transaction
if dry_run_transaction(web3, tx_data):
    # Proceed with real transaction
    pass
```

---

## 7. Emergency Procedures

### 7.1 Compromised Keys

**Immediate Actions:**
1. Stop using compromised keys
2. Move all assets to new secure wallet
3. Review all transactions from compromised wallet
4. Rotate all related credentials
5. Investigate how keys were exposed

### 7.2 Stuck Transactions

If transaction is pending:
- Do NOT send another with same nonce and higher gas unless intentional
- Wait for transaction to confirm or timeout
- Consider using transaction replacement (EIP-1559)

### 7.3 Reverted Transactions

Check why transaction reverted:
- Inspect transaction receipt
- Use contract event logs
- debug_traceTransaction on RPC nodes
- Review contract logic on block explorers

---

## 8. Tools and Resources

**Security Tools:**
- [Etherscan](https://etherscan.io) - Transaction explorer
- [Revoke.cash](https://revoke.cash) - Revoke approvals
- [De.Fi](https://de.fi) - Wallet approvals management
- [OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts) - Audited contract library

**Block Explorers:**
- Ethereum: https://etherscan.io
- Polygon: https://polygonscan.com
- Base: https://basescan.org
- Arbitrum: https://arbiscan.io

**Documentation:**
- [EIP-2612: Permit](https://eips.ethereum.org/EIPS/eip-2612)
- [OpenZeppelin Security](https://docs.openzeppelin.com/contracts/security)
- [Solidity Best Practices](https://consensys.github.io/solidity-style-guide/)

---

## Security Checklist

Before deploying blockchain operations:

- [ ] Private keys never committed to git
- [ ] Private keys stored securely (env vars/secrets manager)
- [ ] All amounts validated before signing
- [ ] All addresses validated (checksum format)
- [ ] Transaction limits enforced
- [ ] Gas estimates calculated
- [ ] Chain ID verified
- [ ] Testnet-first deployment verified
- [ ] Test transactions dry-run
- [ ] Emergency procedures documented
- [ ] Contact information for support

---

**Remember:** In blockchain, security mistakes are irreversible. Validate twice, sign once. 🛡️
