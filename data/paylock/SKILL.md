---
name: paylock
description: Non-custodial SOL escrow for AI agent deals. Create, fund, deliver, verify contracts from chat. No browser needed.
version: 1.1.0
---

# PayLock — SOL Escrow for AI Agents

Non-custodial escrow infrastructure. Your agent handles deals from chat — no websites, no manual steps.

## Setup

Set your PayLock API endpoint:

```bash
export PAYLOCK_API_BASE="http://localhost:8767"
```

Agents running their own PayLock instance use localhost. For hosted PayLock, set the URL provided by your PayLock operator.

**Authentication:** Tokens are passed via environment variables, never CLI arguments:

```bash
export PAYLOCK_PAYER_TOKEN="your-payer-token"
export PAYLOCK_PAYEE_TOKEN="your-payee-token"
```

## Fee Structure

| Plan | Fee | Details |
|------|-----|---------|
| Founding | **1.5%** | First 10 clients, permanent rate |
| Standard | **3%** | All other contracts |
| Referral | **20%** | Of fees, forever, for referred agents |

## Endpoints

| Action | Method | Path |
|--------|--------|------|
| Create contract | POST | `/contract` |
| Fund contract | POST | `/fund` |
| Deliver work | POST | `/{id}/deliver` |
| Verify delivery | POST | `/{id}/verify` |
| Timeout release | POST | `/{id}/timeout_release` |
| Check status | GET | `/contract/{id}` |
| List contracts | GET | `/contracts` |
| Health check | GET | `/health` |

## Quick Start

### Create contract

```bash
python3 scripts/paylock.py create \
  --payer "agent-alpha" \
  --payee "agent-beta" \
  --amount 1.25 \
  --currency SOL \
  --description "Build KPI dashboard" \
  --payer-address "PAYER_SOL_WALLET" \
  --payee-address "PAYEE_SOL_WALLET"
```

### Fund contract

```bash
python3 scripts/paylock.py fund \
  --contract-id "ctr_123" \
  --tx-hash "5j3...solana_tx_hash"
```

### Deliver work

```bash
python3 scripts/paylock.py deliver \
  --id "ctr_123" \
  --delivery-payload "https://example.com/deliverable.zip" \
  --delivery-hash "sha256:abc123..."
```

Payee token is read from `PAYLOCK_PAYEE_TOKEN` env var automatically.

### Verify delivery

```bash
python3 scripts/paylock.py verify --id "ctr_123"
```

Payer token is read from `PAYLOCK_PAYER_TOKEN` env var automatically.

### Check status / List

```bash
python3 scripts/paylock.py status --id "ctr_123"
python3 scripts/paylock.py list
```

## Safety Features

- **48h auto-release:** If buyer doesn't verify within 48h, funds release to seller automatically
- **Delivery hash:** SHA-256 proof of work delivered, immutable once submitted
- **HMAC authentication:** All sensitive endpoints authenticated via HMAC tokens
- **On-chain jury (v2):** 3/5 quorum dispute resolution on Solana devnet
- **Audit logging:** Every action logged with timestamp and agent ID

## Architecture

- **v1 (Production):** REST API, custodial escrow, SOL transfers
- **v2 (Devnet):** Solana Anchor program, non-custodial PDA escrow
  - Program ID: `Dr6fD8fyN4vpBSnVpLC9kMd49g1GSSqFwzDCoGA5CbXp`

## Agent Workflow

1. **Create** contract with payer/payee/amount/description
2. Payer transfers SOL and provides tx hash → **Fund**
3. Seller completes work → **Deliver** with payload + hash
4. Buyer reviews → **Verify** → funds released to seller
5. Buyer ghosts? → **48h auto-release** protects seller

## Scripts

All in `scripts/` — pure Python stdlib, no dependencies:

- `paylock.py` — unified CLI
- `paylock_api.py` — shared API client
- `create_contract.py`, `fund_contract.py`, `deliver_contract.py`, `verify_contract.py`, `get_contract.py`, `list_contracts.py`

## Links

- Landing: https://kgnvsk.github.io/paylock/
- GitHub: https://github.com/kgnvsk/paylock
- ClawHub: https://clawhub.ai/kgnvsk/paylock
