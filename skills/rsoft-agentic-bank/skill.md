---
name: rsoft-agentic-bank
description: AI-native lending service for autonomous agents. Request loans, repay with USDC on Base, and check credit scores — all autonomously.
version: 1.7.0
requires:
  bins:
    - curl
  skills:
    - payment
metadata:
  openclaw:
    homepage: https://rsoft-agentic-bank.com/
---

# RSoft Agentic Bank

Official skill for **RSoft Agentic Bank** — an AI-native lending service for autonomous agents on Base (Coinbase L2).

Agents can request USDC loans, receive funds on-chain, and repay autonomously using the payment skill.

## Prerequisites

- **Payment skill** must be installed and configured for `base-sepolia` with a funded wallet (USDC + small ETH for gas).
- If the payment skill is not installed, run:
```bash
npx clawhub install payment
```
- Configure for Base Sepolia:
```bash
~/.openclaw/skills/payment/scripts/payment-config set network.name "base-sepolia" network.chain_id 84532 network.rpc_url "https://sepolia.base.org" payment.default_token "0x036CbD53842c5426634e7929541eC2318f3dCF7e" payment.default_token_symbol "USDC" payment.default_token_decimals 6
```
- If you don't have a wallet yet:
```bash
~/.openclaw/skills/payment/scripts/create-wallet
```
- Fund your wallet with USDC and a small amount of ETH for gas on Base Sepolia.

## Setup: Know Your Wallet Address

Before using the bank, get your wallet address:
```bash
~/.openclaw/skills/payment/scripts/get-address
```
Use the `address` field as your `agent_id` in all bank commands.

## Base URL

```
https://7mavs5vu7ggbhtxvbavdgs26qa0cbawg.lambda-url.us-east-1.on.aws
```

## Available Commands

### 1. Check Interest Rates

Query current lending rates:
```bash
curl -s https://7mavs5vu7ggbhtxvbavdgs26qa0cbawg.lambda-url.us-east-1.on.aws/api/interest-rates
```

### 2. Check Credit Score

Check your creditworthiness (replace `{agent_id}` with your wallet address):
```bash
curl -s https://7mavs5vu7ggbhtxvbavdgs26qa0cbawg.lambda-url.us-east-1.on.aws/api/creditworthiness/{agent_id}
```

### 3. Request a Loan

Request USDC financing (minimum 5 USDC). Replace `{agent_id}` with your wallet address:
```bash
curl -s -X POST -H "Content-Type: application/json" -d '{"agent_id": "{agent_id}", "amount": 5}' https://7mavs5vu7ggbhtxvbavdgs26qa0cbawg.lambda-url.us-east-1.on.aws/api/loans
```
The bank evaluates risk with AI and, if approved, sends USDC directly to your wallet on Base Sepolia.

### 4. Check Wallet Balance

Verify that the loan was received:
```bash
~/.openclaw/skills/payment/scripts/get-address
```

### 5. Repay a Loan (3 steps — do all 3 in order)

**Step 1: Check how much you owe**
```bash
curl -s https://7mavs5vu7ggbhtxvbavdgs26qa0cbawg.lambda-url.us-east-1.on.aws/api/repay-info/{agent_id}
```
Save the `request_id`, `repayment_amount`, and `pay_to` from the response.

**Step 2: Send USDC payment on-chain**
```bash
~/.openclaw/skills/payment/scripts/pay --to <pay_to> --amount <repayment_amount>
```
Use the `pay_to` and `repayment_amount` values from Step 1. Save the transaction hash from the output.

**Step 3: Confirm repayment with the bank**

WARNING: The URL is `/api/repay` — do NOT change it to `/api/loans/repay` or any other URL.
```bash
curl -s -X POST -H "Content-Type: application/json" -d '{"request_id": "<request_id>", "tx_hash": "<tx_hash>"}' https://7mavs5vu7ggbhtxvbavdgs26qa0cbawg.lambda-url.us-east-1.on.aws/api/repay
```
Use the `request_id` from Step 1 and the `tx_hash` from Step 2.

## Full Workflow Example

```
1. Get your wallet address         → get-address
2. Check interest rates            → curl /api/interest-rates
3. Check your credit score         → curl /api/creditworthiness/{wallet}
4. Request a loan                  → curl POST /api/loans
5. Verify loan received            → get-address (check balance)
6. Check repayment info            → curl /api/repay-info/{wallet}
7. Send USDC to bank               → pay --to {pay_to} --amount {amount}
8. Confirm repayment               → curl POST /api/repay
```

## Important Notes

- **Network:** Base Sepolia (testnet) — all transactions use test USDC.
- **Minimum loan:** 5 USDC.
- **Currency:** USDC (6 decimals) on Base Sepolia.
- **Gas:** Your wallet needs a small amount of ETH on Base Sepolia for transaction fees.
- **One active loan at a time.** Repay before requesting a new loan.
- All transactions are verifiable on [BaseScan Sepolia](https://sepolia.basescan.org/).

## Verification

- **Official Website:** [rsoft-agentic-bank.com](https://rsoft-agentic-bank.com/)
- **Publisher:** RSoft Latam
- **Protocol:** REST API via curl + payment skill for on-chain transfers
- **Network:** Base Sepolia (Coinbase L2)

---
*Developed by RSoft Latam — Empowering the Agentic Economy.*
