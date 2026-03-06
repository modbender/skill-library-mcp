---
name: clawpay
description: Send and receive escrow payments on Solana using ClawPay. Pay other AI agents, lock funds in escrow, confirm delivery, release payments, check receipts, and verify agent reputation. Use when asked to pay an agent, create an escrow, buy a service from another agent, sell a service, check payment status, or view transaction history.
version: 1.0.0
author: clawpay
metadata:
  openclaw:
    emoji: "💰"
    requires:
      bins:
        - python3
        - pip3
    primaryEnv: SOLANA_KEYPAIR_PATH
---

# ClawPay — Escrow Payments for AI Agents

You can send and receive trustless escrow payments on Solana using ClawPay. This skill handles the full payment lifecycle: locking funds, confirming delivery, releasing payments, and checking receipts.

## Setup

First, check if clawpay is installed:

```bash
pip3 show clawpay
```

If not installed:

```bash
pip3 install clawpay
```

The user's Solana wallet keypair is required. Check for it at the path in the `SOLANA_KEYPAIR_PATH` environment variable, or look for common locations:
- `~/wallet.json`
- `~/.config/solana/id.json`
- `~/projects/clawpay/program-keypair.json`

If no keypair is found, ask the user to provide one or generate one with `solana-keygen new --outfile ~/wallet.json`.

## How ClawPay Works

ClawPay is a time-locked escrow protocol on Solana. Every payment follows this flow:

1. **T0 — Lock**: Buyer locks SOL into an escrow account
2. **T1 — Deliver**: Seller must deliver before the deadline, or funds auto-refund to buyer
3. **T2 — Verify**: Buyer confirms delivery, or funds auto-release to seller after the window
4. **Settle**: 98% goes to seller, 1% to ClawPay, 1% to referrer (if any)
5. **Receipt**: Cryptographic receipt minted on-chain for both parties

No trust required between agents. The timeline enforces everything.

## Core Operations

### Pay Another Agent (Create Escrow)

When asked to pay an agent or buy a service:

```python
from clawpay import Client
from solders.keypair import Keypair
from solders.pubkey import Pubkey

keypair = Keypair.from_json(open("KEYPAIR_PATH").read())
client = Client(keypair)

escrow = client.create_escrow(
    seller=Pubkey.from_string("SELLER_PUBKEY"),
    amount_sol=AMOUNT,
    delivery_secs=DELIVERY_TIME,       # seconds until delivery deadline
    verification_secs=VERIFICATION_TIME # seconds for dispute window (min 10)
)
print(f"Escrow created: {escrow.address}")
print(f"Amount: {escrow.amount_sol} SOL")
print(f"Delivery deadline: {escrow.t1}")
print(f"Verification ends: {escrow.t2}")
```

Default values if not specified:
- `delivery_secs`: 600 (10 minutes)
- `verification_secs`: 30 (30 seconds)
- `amount_sol`: Ask the user — never assume an amount

### Confirm Delivery (As Seller)

When you've completed a service and need to confirm delivery:

```python
from clawpay import Client
from solders.keypair import Keypair
from solders.pubkey import Pubkey

keypair = Keypair.from_json(open("KEYPAIR_PATH").read())
client = Client(keypair)

escrow_address = Pubkey.from_string("ESCROW_ADDRESS")
client.confirm_delivery(escrow_address, keypair)
print("Delivery confirmed. Waiting for verification window.")
```

### Release Funds (After Verification)

After the verification window passes, anyone can trigger release:

```python
client.auto_release(Pubkey.from_string("ESCROW_ADDRESS"))
print("Funds released to seller.")
```

### Refund (Missed Delivery Deadline)

If the seller missed the delivery deadline:

```python
client.auto_refund(Pubkey.from_string("ESCROW_ADDRESS"))
print("Funds refunded to buyer.")
```

### Check Escrow Status

```python
escrow = client.get_escrow(Pubkey.from_string("ESCROW_ADDRESS"))
print(f"Status: {escrow.status}")
print(f"Amount: {escrow.amount_sol} SOL")
print(f"Delivered: {escrow.delivered}")
print(f"Released: {escrow.released}")
```

### Check Agent Reputation (Receipts)

```python
receipts = client.get_receipts(Pubkey.from_string("AGENT_PUBKEY"))
print(f"Total transactions: {len(receipts)}")
for r in receipts:
    outcome = ["released", "refunded", "disputed"][r.outcome]
    print(f"  #{r.receipt_index}: {r.amount_sol} SOL — {outcome}")
```

## Important Constraints

- **Minimum escrow**: 0.05 SOL
- **Maximum escrow**: 10.0 SOL
- **Minimum verification window**: 10 seconds
- **Maximum delivery time**: 30 days
- **Fee**: 2% on settlement (1% ClawPay + 1% referrer)
- **Network**: Solana Mainnet (default) or Devnet

## Guardrails

- NEVER create an escrow without confirming the amount with the user first
- NEVER send funds without verifying the seller's public key
- Always display the escrow address after creation — the user needs it
- Always check escrow status before attempting release or refund
- If a keypair file is not found, ask the user — do not guess
- Report all errors clearly, especially insufficient balance errors
- When checking reputation, mention both successful and failed transactions for honesty

## Verification

After any transaction, you can verify on Solana Explorer:
- Program: https://explorer.solana.com/address/F2nwkN9i2kUDgjfLwHwz2zPBXDxLDFjzmmV4TXT6BWeD
- Transaction: https://explorer.solana.com/tx/TRANSACTION_SIGNATURE

## Links

- Website: https://claw-pay.com
- SDK: https://pypi.org/project/clawpay/
- GitHub: https://github.com/jakemeyer125-design/ClawPay-SDK
