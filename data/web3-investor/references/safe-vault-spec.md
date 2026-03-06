# Safe Vault Technical Specification

## Overview

Safe Vault is a secure transaction execution framework that enables AI agents to interact with Web3 protocols safely. It follows a phased approach:

- **Phase 1**: Simulation + Manual Confirmation
- **Phase 2**: Limited Auto-Execution (≤ $100 USD by default)
- **Phase 3**: Full Autonomous Execution

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Agent Request                           │
│  "Invest 100 USDC into Aave with max 5% slippage"           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Intent Parser                              │
│  - Parse natural language to structured intent              │
│  - Identify protocol, action, amount, parameters            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Whitelist Check                            │
│  - Is target address in whitelist?                          │
│  - Is action type allowed?                                   │
│  - Is amount within limits?                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Risk Analysis                              │
│  - Protocol risk assessment                                  │
│  - Slippage estimation                                        │
│  - Gas cost estimation                                        │
│  - Simulate transaction                                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Execution Decision                         │
│                                                              │
│  Phase 1: Generate signing request → Human confirms         │
│  Phase 2: Auto-sign if ≤ limit → Human reviews in batch     │
│  Phase 3: Auto-sign within parameters → Log only             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Transaction Execution                      │
│  - Submit to mempool                                         │
│  - Monitor confirmation                                       │
│  - Report result                                              │
└─────────────────────────────────────────────────────────────┘
```

## Phase 1: Simulation Mode (Current)

### Transaction Flow

```
Agent → Intent Parser → Whitelist Check → Risk Analysis
→ Simulation → Signing Request → Human Review → Manual Execution
```

### Signing Request Format

```json
{
  "request_id": "uuid",
  "timestamp": "2024-01-15T10:30:00Z",
  "intent": {
    "action": "deposit",
    "protocol": "aave-v3",
    "amount": "100",
    "asset": "USDC",
    "chain": "ethereum"
  },
  "transaction": {
    "to": "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2",
    "value": "0",
    "data": "0x...",
    "gas_limit": 250000,
    "gas_price": "20000000000"
  },
  "simulation": {
    "success": true,
    "gas_used": 185000,
    "state_changes": [
      {
        "contract": "0x...",
        "change": "USDC balance -100"
      },
      {
        "contract": "0x...",
        "change": "aUSDC balance +100"
      }
    ]
  },
  "risk_assessment": {
    "risk_level": "low",
    "risk_score": 1,
    "warnings": []
  },
  "approval_url": "https://safe-vault.example/approve/uuid"
}
```

### Human Confirmation Methods

1. **CLI Confirmation**: Agent displays signing request, user copies to wallet
2. **QR Code**: Generate QR code for mobile wallet scanning
3. **Safe{Wallet}**: Create pending transaction in Safe UI

## Phase 2: Limited Auto-Execution

### Requirements

1. **Secure Key Storage**
   - Use environment variables or secure vault
   - Never log or expose private keys
   - Consider using AWS KMS / GCP KMS

2. **Transaction Limits**
   - Default: $100 USD equivalent
   - Configurable per asset and protocol
   - Daily cumulative limit

3. **Rate Limiting**
   - Max 10 transactions per hour
   - Max 50 transactions per day
   - Configurable cooldown periods

4. **Monitoring**
   - All transactions logged
   - Alert on suspicious patterns
   - Daily summary to user

### Configuration

```json
{
  "phase_2": {
    "enabled": true,
    "limits": {
      "per_transaction_usd": 100,
      "daily_total_usd": 500,
      "hourly_count": 10,
      "daily_count": 50
    },
    "whitelist": {
      "required": true,
      "addresses": [
        {
          "address": "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2",
          "name": "Aave Pool",
          "max_amount_usd": 500
        }
      ]
    },
    "notifications": {
      "on_execute": true,
      "daily_summary": true,
      "channel": "telegram"
    }
  }
}
```

## Phase 3: Full Autonomous

### Requirements

1. **Comprehensive Audit**
   - Third-party security audit
   - Formal verification of critical paths
   - Bug bounty program

2. **Safety Mechanisms**
   - Circuit breakers
   - Automatic pause on anomaly detection
   - Insurance fund

3. **Governance**
   - Multi-sig for critical changes
   - Timelock for parameter updates
   - User veto power

### Not Recommended For
- Individual users without insurance
- Amounts > $10,000 USD
- Novel protocols (use Phase 1/2)

## Wallet Integration

### MetaMask (EOA)

```python
# Phase 1: Generate request for user to sign
request = generate_signing_request(tx)
print(f"Please sign this transaction in MetaMask:")
print(f"To: {request['to']}")
print(f"Data: {request['data']}")

# Phase 2+: Use web3.py with private key
from web3 import Web3
w3 = Web3(...)
signed_tx = w3.eth.account.sign_transaction(tx, private_key)
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
```

### Safe{Wallet} (Multi-sig)

```python
# Build Safe transaction
safe_tx = safe.build_transaction(
    to=tx['to'],
    value=tx['value'],
    data=tx['data'],
    safe_nonce=safe_nonce
)

# Phase 1: Create pending transaction
# User approves in Safe UI
safe_url = f"https://app.safe.global/transactions/queue?safe={safe_address}"

# Phase 2+: Sign and propose
safe.sign_transaction(safe_tx)
safe.propose_transaction(safe_tx)
```

## Security Checklist

- [ ] Private keys stored securely (env vars, vault)
- [ ] Whitelist enforced before any execution
- [ ] All transactions simulated before signing
- [ ] Rate limits in place
- [ ] Transaction logging enabled
- [ ] Error handling for failed transactions
- [ ] Gas price limits to prevent frontrunning
- [ ] Slippage protection for DEX trades