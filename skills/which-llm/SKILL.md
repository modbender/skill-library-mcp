---
name: Decision Economic Optimizer
description: Deterministic decision-ranking API with HTTP 402 USDC payments and outcome credits (discounts).
version: 0.1.0
homepage: https://which-llm.com
credentials_required: true
primary_credential: WALLET_CREDENTIALS
---

# Which‑LLM: Outcome‑Driven Decision Optimizer

## Overview

Use this skill when you need to pick a recommended **LLM model** under clear constraints like **budget** and **minimum quality**, based on a natural-language goal.

You’ll get a single recommended model plus an ordered fallback plan you can follow if the first choice fails.

## How it works

- **Ask for a decision**: send `goal` + constraints to `POST /decision/optimize`.
- **Get an answer**: receive `recommended_model` and (when available) a `fallback_plan`.
- **Earn discounts**: after you execute the choice, report the outcome to `POST /decision/outcome` to receive a credit token you can apply to future paid calls.

## Quick Reference

**API Base URL:** `https://api.which-llm.com`  
**Homepage:** `https://which-llm.com`  
**Skill Files:** `skills/decision-economic-optimizer/SKILL.md`, `skills/decision-economic-optimizer/skill.json`

**Supported Chains:** Base (8453), Ethereum (1), Arbitrum (42161), Optimism (10), Avalanche (43114)

**Single-line Use Cases:**

- Pick the cheapest LLM that meets quality requirements
- Get a fallback plan when your first choice fails
- Optimize model selection for specific tasks (summarize, extract, classify, coding)
- Earn discounts by reporting actual execution outcomes

### Prerequisites

Before using this skill, you must provide the agent with:

- **Dedicated EVM-compatible wallet** for autonomous payments (separate from your main wallet)
- **Limited USDC balance** on at least one supported chain (Base recommended for lower fees) - recommended $2-10 USDC
- **Native gas token** for transaction fees (ETH on Base/Ethereum/Arbitrum/Optimism, AVAX on Avalanche) - recommended $3-5
- **Payment address verification** - you must verify payment addresses from multiple independent sources before giving the agent wallet access
- **Important:** Both USDC and gas tokens must be in the same dedicated wallet

The agent requires these credentials to autonomously:

- Sign USDC transfer transactions
- Query wallet balance
- Send transactions to blockchain

### Credential Type Options & Risk Assessment

This skill supports multiple credential formats for wallet access. **Choose the option that matches your security requirements:**

#### Option 1: Raw Private Key

**Format:** 64-character hex string with `0x` prefix

```bash
export WALLET_PRIVATE_KEY="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
```

**Risk Profile:**

- ✅ **Simplest implementation** - Direct signing capability
- ⚠️ **High risk if main wallet** - Full control of wallet
- ✅ **Acceptable risk with dedicated wallet** - Limited funds isolation
- ⚠️ **Requires secure storage** - Environment variable or secrets manager

**Use when:** You create a dedicated wallet with limited USDC + gas token specifically for this skill

**Security mitigation:**

- MUST be a dedicated wallet (not your main wallet)
- MUST contain limited funds only ($2-10 USDC + $3-5 gas token)
- Gas tokens needed: ETH on Base/Ethereum/Arbitrum/Optimism, or AVAX on Avalanche
- SHOULD rotate periodically (create new wallet, transfer remaining balance)
- MUST NOT be committed to git or shared

#### Option 2: Mnemonic Phrase

**Format:** 12 or 24-word BIP-39 seed phrase

```bash
export WALLET_MNEMONIC="word1 word2 word3 ... word12"
```

**Risk Profile:**

- ⚠️ **Same risk as private key** - Derives private key from phrase
- ⚠️ **Potentially higher risk** - Can derive multiple accounts
- ✅ **User-friendly backup** - Easier to write down securely

**Use when:** You prefer mnemonic-based wallet management

**Security mitigation:** Same as private key + ensure only first derived account (m/44'/60'/0'/0/0) is used

#### Option 3: Keystore File + Password

**Format:** Encrypted JSON keystore file (Ethereum standard) + password

```bash
export WALLET_KEYSTORE_PATH="/path/to/keystore.json"
export WALLET_KEYSTORE_PASSWORD="your-secure-password"
```

**Risk Profile:**

- ✅ **Encrypted at rest** - Private key stored encrypted
- ✅ **Two-factor security** - Requires file AND password
- ⚠️ **Still grants full signing** - Once decrypted, same as private key
- ⚠️ **File management overhead** - Must securely store keystore file

**Use when:** You want encrypted private key storage with password protection

**Security mitigation:** Strong password + secure keystore file permissions (chmod 600)

### Credential Setup

1. Generate a new wallet specifically for this skill (never reuse existing wallets)
2. Fund with limited USDC + gas token ($2-10 USDC + $3-5 gas recommended for normal usage)
   - **USDC amounts:**
     - $1 = 100 requests at $0.01 each (or ~199 with 50% credits)
     - $2 = 200 requests (or ~399 with 50% credits)
     - $5 = 500 requests (or ~999 with 50% credits)
     - $10 = 1,000 requests (or ~1,999 with 50% credits)
   - **Gas token amounts:** $3-5 in ETH (Base/Ethereum/Arbitrum/Optimism) or AVAX (Avalanche) for transaction fees
   - **Credit optimization:** If you report outcomes after each decision and use the credit tokens, you get ~50% refund on all requests except the first, effectively doubling your request count
3. Store private key in secure environment variable or secrets manager
4. Monitor transactions regularly via block explorer
5. Rotate wallet periodically (monthly recommended)
6. Never commit private key to version control or share publicly

**Autonomous Operation Note:** The agent will use this wallet to autonomously pay for API requests ($0.01 each) without asking for approval each time. This design avoids approval fatigue while keeping costs predictable and bounded by the wallet balance you choose to fund.

**Important:** Remember to fund both USDC (for payments) AND native gas token ETH/AVAX (for transaction network fees) in your dedicated wallet.

**Example secure setup:**

```bash
# Generate new dedicated wallet (using cast from Foundry)
cast wallet new

# Output:
# Address: 0xYourNewDedicatedAddress
# Private key: 0xYourNewPrivateKey

# Securely set environment variable (doesn't save to shell history)
read -s WALLET_PRIVATE_KEY
# Paste the private key, press Enter

export WALLET_PRIVATE_KEY

# Verify (shows only address, not private key)
cast wallet address --private-key $WALLET_PRIVATE_KEY

# Fund the wallet with limited USDC + gas token
# Example for Base network:
# 1. Send USDC to 0xYourNewDedicatedAddress (e.g., $5 USDC)
# 2. Send ETH to 0xYourNewDedicatedAddress (e.g., $3 ETH for gas fees)
```

**Credential Configuration Example:**

```bash
# Set required wallet credentials (environment variables)
export WALLET_PRIVATE_KEY="0x123...EXAMPLE_WALLET_PRIVATE_KEY_EXAMPLE"

# Optional: Use custom RPC endpoint (defaults to public RPC if not set)
export WALLET_RPC_URL="https://mainnet.base.org"

# Optional: Set preferred chain (defaults to Base/8453 if not set)
export PREFERRED_CHAIN_ID="8453"
```

**Security Note:** These credentials grant autonomous payment capability up to the wallet balance. See "Security Model & Trust Assumptions" below for risk mitigation.

### Security Model & Trust Assumptions

**What you should NOT blindly trust:**

- This skill file (could be tampered during distribution)
- Any single verification source for payment addresses

**Threat model:**

- ✅ Protected against: API returning wrong address (verify independently)
- ✅ Protected against: Skill file modification (no hardcoded addresses trusted)
- ✅ Protected against: Excessive spending (limited by dedicated wallet balance)
- ⚠️ Risk: Agent can autonomously spend up to wallet balance
- ⚠️ Mitigation: Use dedicated wallet with limited funds, monitor transactions regularly

### Wallet Setup Best Practices

**Before providing wallet access:**

1. **Create a dedicated wallet** - Never use your main wallet
2. **Set required credentials** - Provide `WALLET_PRIVATE_KEY` and optionally `WALLET_RPC_URL`, `PREFERRED_CHAIN_ID` (see skill.json metadata for details)
3. **Verify payment addresses** - Check from at least 2 independent sources (see Multi-Source Verification below)
4. **Fund with limited amount** - Only deposit what you're comfortable the agent spending autonomously
5. **Test with small amount first** - Start with minimal funding ($1-2 USDC + $1-2 gas) to verify operation
6. **Monitor regularly** - Check transactions on block explorer (Basescan, Etherscan)
7. **Refill as needed** - Add more funds only after reviewing transaction history

**Recommended initial funding:**

- **USDC:** $2-10 (allows 200-1000 optimization requests at $0.01 each)
- **Gas token:** $3-5 in ETH (Base/Ethereum/Arbitrum/Optimism) or AVAX (Avalanche)
- **Note:** Gas fees on Base are typically very low (~$0.01-0.05 per transaction), so $3-5 ETH can cover hundreds of transactions

## What this skill does

- Sends HTTPS requests to Which‑LLM API
- Uses `POST /decision/optimize` to get a recommendation and `POST /decision/outcome` to report results
- May call `GET /capabilities`, `GET /pricing`, and `GET /status` to discover features and costs
- For paid endpoints, handles the standard flow: **402 → pay autonomously → retry**, and can apply `X-Credit-Token` for discounts
- **Autonomously sends USDC payments** using the provided wallet credentials (`WALLET_PRIVATE_KEY`) when the API requires payment (402 response)
- Connects to blockchain via `WALLET_RPC_URL` (or defaults to public RPC) to sign and broadcast transactions

## What this skill does NOT do

- Does not call an LLM or execute code from your inputs

## Security rules

- Agent operates within the balance limits of the dedicated wallet you provide
- Monitor wallet transactions regularly through block explorers
- Only send payment proof headers to API: transaction hash & wallet address

### Authentication

There is no API key. Paid requests use **payment proof headers** (after an initial 402) and optional `X-Credit-Token` for discounts.

## Endpoints

- Free endpoints (`/capabilities`, `/pricing`, `/status`) require no authentication
- Paid endpoints (`/decision/optimize`) return 402 initially, then accept payment proof headers
- Credits earned from outcome reports can be redeemed via `X-Credit-Token` header

### Autonomous Operation Model

This skill operates autonomously using a dedicated wallet you provide:

- ⚙️ **Autonomous payment authorization**: Agent can send USDC payments up to the wallet balance without per-transaction approval
- ⚙️ **Autonomous API calls**: Can call both free and paid endpoints (`POST /decision/optimize`, `POST /decision/outcome`) without confirmation
- ⚙️ **Risk control**: You control maximum spending by limiting the dedicated wallet balance
- ℹ️ **One-time setup**: Verify payment addresses from multiple sources before providing wallet access (see Payment Security Verification)

**Why No Per-Request Approval?**

This skill is designed for **autonomous operation without per-request approval** because:

1. **Very low per-request cost**: Each decision costs only $0.01 USDC (or ~$0.005 with 50% credit refunds)
2. **Approval fatigue**: Requiring approval for every $0.01 payment would be disruptive and impractical
3. **User-controlled limits**: You set the maximum spending by limiting the dedicated wallet USDC balance (+ gas token for fees)
4. **Example**: A $5 USDC balance + $3 gas token allows 500 optimization requests (or ~999 if using credits from outcome reports)

**Trade-off:** You grant autonomous spending capability in exchange for convenience. This is acceptable because:

- ✅ Cost per request is minimal ($0.01)
- ✅ Total spending is bounded by wallet USDC balance you control (+ minimal gas fees)
- ✅ Wallet is dedicated (separate from your main funds)
- ✅ Transactions are auditable on-chain via block explorer
- ℹ️ Remember to maintain both USDC and gas token (ETH/AVAX) in the dedicated wallet

## Payment Security Verification

### ⚠️ Security Model

This skill **cannot** provide a trustworthy hardcoded payment address because:

- The skill file itself could be tampered with during distribution
- A compromised registry or MITM attack could modify the "verified" address
- No single source should be trusted for financial transactions

### Multi-Source Verification Required (One-Time Setup)

Before sending ANY payment, verify the payment address from **at least 2 of these independent sources**:

#### Option 1: Well-known endpoint (plain text)

```bash
curl -s https://api.which-llm.com/.well-known/payment-address.txt
```

This returns the receiver address as plain text (42 characters starting with `0x`).

#### Option 2: Official documentation (structured JSON)

```bash
curl -s https://api.which-llm.com/docs/payment-addresses | jq -r '.receiver'
```

#### Option 3: ENS record

Check the ENS domain `which-llm.eth` using any of these methods:

- Method A: Using app.ens.domains

1. Visit [app.ens.domains/which-llm.eth](https://app.ens.domains/which-llm.eth)
2. Look for the "Address" field in the ENS record (under "Records" tab)
3. Verify it matches the address from other sources

- Method B: Using command line (requires `cast` from Foundry)

If you don't have Foundry installed:

```bash
# Install Foundry
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

Then resolve the ENS name:

```bash
# Resolve ENS name to address
cast resolve-name which-llm.eth --rpc-url https://eth.llamarpc.com
```

**Verification Rule:** All sources must return the **same address**. If any source shows a different address, **DO NOT provide payment** and report the discrepancy to [report]("https://api.which-llm.com/report/wrong_address").

**Note:** This verification is required only once. After verification, the agent can autonomously send payments to the verified address up to the wallet USDC balance (ensure wallet also has gas tokens for transaction fees).

### Reporting Address Validation Issues

If you encounter address validation problems, report them using the free `/report/wrong_address` endpoint:

```bash
# Report discrepancy from .well-known and ENS
curl -X POST "https://api.which-llm.com/report/wrong_address" \
  -H "Content-Type: application/json" \
  -d '{
    "well known": ".well-known returned 0xAAA... but ENS returned 0xBBB...",
    "ENS": "which-llm.eth resolved to different address than other sources"
  }'
```

**Request Body Fields (all optional, at least one required):**

- `"well known"` (string) - Issues with `.well-known/payment-address.txt` validation
- `"api"` (string) - Issues with API-based address validation
- `"ENS"` (string) - Issues with ENS name resolution

**Example Response:**

```json
{
  "status": "recorded",
  "report_id": "123e4567-e89b-12d3-a456-426614174000",
  "reported_at_epoch": 1707686400
}
```

## Getting Started

### Example: Fetch payment addresses via API

```bash
curl -s "https://api.which-llm.com/docs/payment-addresses"
```

**Example Output:**

```json
{
  "service": "decision-economic-optimizer",
  "payment_asset": "USDC",
  "payment_scheme": "exact",
  "chain_namespace": "eip155",
  "chains": {
    "8453": {
      "name": "Base",
      "asset": "USDC",
      "pay_to": "0x..."
    },
    "1": {
      "name": "Ethereum",
      "asset": "USDC",
      "pay_to": "0x..."
    }
  },
  "receiver": "0x..."
}
```

### Check capabilities (recommended)

```bash
curl -s "https://api.which-llm.com/capabilities"
```

**Example Output:**

```json
{
  "service": "decision-economic-optimizer",
  "deterministic": true,
  "decision_version": "v1",
  "supported_constraints": ["cost", "quality"],
  "supported_decision_types": ["llm_model_selection"],
  "endpoints": ["/decision/optimize", "/decision/outcome", "/status"],
  "payment_model": "http_402",
  "payment_asset": "USDC",
  "payment_scheme": "exact",
  "networks": [
    "eip155:8453",
    "eip155:1",
    "eip155:42161",
    "eip155:10",
    "eip155:43114"
  ]
}
```

### Check pricing

```bash
curl -s "https://api.which-llm.com/pricing"
```

**Example Output:**

```json
{
  "currency": "USDC",
  "payment_asset": "USDC",
  "payment_scheme": "exact",
  "chain_namespace": "eip155",
  "chains": {
    "8453": "Base",
    "1": "Ethereum",
    "42161": "Arbitrum",
    "10": "Optimism",
    "43114": "Avalanche"
  },
  "pricing": {
    "/decision/optimize": {
      "price": 0.01,
      "unit": "per_request"
    }
  }
}
```

### Optimize a decision (paid)

The optimize endpoint uses HTTP 402 payment gating. Here's the detailed flow:

#### Step 1: Initial Request (Expects 402)

```bash
IDEMPOTENCY_KEY="request_$(date +%s)_001"

curl -sS -i -X POST "https://api.which-llm.com/decision/optimize" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $IDEMPOTENCY_KEY" \
  -d '{
    "goal": "Summarize customer feedback emails into a 5-bullet executive summary",
    "constraints": {
      "min_quality_score": 0.8,
      "max_cost_usd": 0.01
    },
    "workload": {
      "input_tokens": 1200,
      "output_tokens": 300,
      "requests": 1
    },
    "task_type": "summarize"
  }'
```

**Request Fields:**

- `goal` (required): Natural language description of what you want to accomplish
- `constraints` (required):
  - `min_quality_score`: Minimum quality threshold (0-1)
  - `max_cost_usd`: Maximum cost in USD
- `workload` (optional): Token/pricing dimensions for accurate cost estimation
  - `input_tokens`, `output_tokens` (required if workload provided)
  - `requests`, `images`, `web_searches`, `internal_reasoning_tokens`, `input_cache_read_tokens`, `input_cache_write_tokens` (optional)
- `task_type` (optional): `"summarize" | "extract" | "classify" | "coding" | "general"` - helps route to task-appropriate models

**Example Response (402 Payment Required):**

```http
HTTP/2 402 Payment Required
Content-Type: application/json

{
  "error_code": "PAYMENT_REQUIRED",
  "required_amount": "0.01",
  "currency": "USDC",
  "accepts": [
    {
      "chain": "eip155:8453",
      "asset": "USDC",
      "pay_to": "0x...PAY_TO_ADDRESS...123xyz",
      "scheme": "exact"
    },
    {
      "chain": "eip155:1",
      "asset": "USDC",
      "pay_to": "0x...PAY_TO_ADDRESS...123xyz",
      "scheme": "exact"
    }
  ],
  "payment_reference": "decision_optimize_abc123",
  "idempotency_key": "request_1770809000_001"
}
```

##### Step 2: Pay USDC On-Chain

**⚠️ SECURITY: Payment address must be verified during initial setup** (see "Payment Security Verification" section)

The agent will autonomously send an exact USDC transfer to `accepts[].pay_to` on the chosen chain:

- Amount: exactly `required_amount` (e.g., `0.01` USDC)
- Chain: choose from `accepts[].chain` (e.g., `eip155:8453` for Base)
- Asset: USDC
- The agent uses the provided wallet to sign and send the transaction
- After confirmation, the transaction hash (`tx_hash`) is obtained

**Note:** The agent autonomously signs and sends the transaction using the dedicated wallet you provided. Only the transaction hash and wallet address are sent to the API as public proof of payment.

##### Step 3: Retry with Payment Proof

The agent automatically retries the request with payment proof headers:

```bash
# Example of the retry request (automated by agent)
TX_HASH="0x...TRANSACTION_HASH_FROM_STEP_2"
PAYER_ADDRESS="0x...WALLET_ADDRESS_PROVIDED"
PAYMENT_CHAIN="eip155:8453"
PAYMENT_AMOUNT="0.01"

curl -sS -i -X POST "https://api.which-llm.com/decision/optimize" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $IDEMPOTENCY_KEY" \
  -H "X-Payment-Chain: $PAYMENT_CHAIN" \
  -H "X-Payment-Tx: $TX_HASH" \
  -H "X-Payer: $PAYER_ADDRESS" \
  -H "X-Payment-Amount: $PAYMENT_AMOUNT" \
  -H "X-Payment-Asset: USDC" \
  -d '{
    "goal": "Summarize customer feedback emails into a 5-bullet executive summary",
    "constraints": {
      "min_quality_score": 0.8,
      "max_cost_usd": 0.01
    }
  }'
```

**Payment Headers:**

- `X-Payment-Chain`: CAIP-2 chain ID (e.g., `eip155:8453` for Base)
- `X-Payment-Tx`: Transaction hash (32 bytes, hex with `0x` prefix)
- `X-Payer`: Your wallet address (hex with `0x` prefix) - **public address only**
- `X-Payment-Amount`: Exact decimal amount matching `required_amount`
- `X-Payment-Asset`: `USDC`

**Security Note:** These headers contain only public information (transaction hash and wallet address). The API verifies the payment by checking the on-chain transaction.

**Example Response (200 Success):**

```http
HTTP/2 200 OK
Content-Type: application/json
X-Decision-Version: v1
X-Decision-Hash: 0xdef456...

{
  "decision_id": "d4e5f6a7-b8c9-0d1e-2f3a-4b5c6d7e8f90",
  "decision_version": "v1",
  "deterministic": true,
  "scoring_version": "v1.0",
  "recommended_model": "openai/gpt-4o-mini",
  "expected_cost": 0.008,
  "expected_quality": 0.85,
  "safe_to_execute": true,
  "human_review_required": false,
  "task_type": "summarize",
  "model_metadata": {
    "provider": "openai",
    "model_id": "openai/gpt-4o-mini",
    "name": "GPT-4o Mini",
    "context_length": 128000,
    "pricing": {
      "prompt": 0.15,
      "completion": 0.6
    },
    "signals": {
      "is_small": true,
      "is_coder": false,
      "is_reasoning": false
    }
  },
  "fallback_plan": [
    {
      "option_id": "anthropic/claude-3-haiku",
      "reason": "NEXT_BEST"
    }
  ],
  "explainability": {
    "score": 0.92,
    "components": {
      "cost_penalty": 0.15,
      "quality_penalty": 0.05,
      "goal_penalty": 0.02,
      "pricing_dimensions_used": ["prompt", "completion"]
    },
    "discarded": false
  },
  "payment": {
    "status": "verified",
    "chain": "eip155:8453",
    "tx_hash": "0x...EXAMPLE_TX_HASH",
    "payer": "0x...EXAMPLE_PAYER_ADDRESS",
    "amount_usdc": "0.01",
    "asset": "USDC",
    "receiver": "0x...PAY_TO_ADDRESS...123xyz"
  },
  "job_receipt": {
    "receipt_version": "v1",
    "receipt_id": "0xabc123...",
    "eip712": {
      "types": {},
      "domain": {},
      "message": {},
      "signature": "0x..."
    }
  }
}
```

**Using Credit Token (Discount):**

If you have a credit token from a previous outcome, include it to reduce the required payment:

```bash
# Example token structure (base64 JWT): {"credit_id":"...","decision_id":"...","payer":"0x...","amount_usdc":"..."}
CREDIT_TOKEN="eyJ...EXAMPLE_CREDIT_TOKEN_FROM_OUTCOME_RESPONSE...xyz"

curl -sS -i -X POST "https://api.which-llm.com/decision/optimize" \
  -H "Content-Type: application/json" \
  -H "X-Credit-Token: $CREDIT_TOKEN" \
  -d '{
    "goal": "Classify customer inquiries by priority",
    "constraints": {
      "min_quality_score": 0.7,
      "max_cost_usd": 0.015
    }
  }'
```

**Possible Responses:**

- If credit fully covers cost → 200 response (no payment needed)
- If credit partially covers → 402 with reduced `required_amount`

**Example Response (402 with Partial Credit):**

```http
HTTP/2 402 Payment Required
Content-Type: application/json

{
  "error_code": "PAYMENT_REQUIRED",
  "required_amount": "0.005",
  "currency": "USDC",
  "accepts": [...],
  "diagnostic": {
    "price_usdc": "0.01",
    "credit_applied_usdc": "0.005",
    "remaining_usdc": "0.005"
  }
}
```

#### 4. Report outcome (earn a discount)

After executing the recommended model, report what actually happened to earn a credit token (discount) for future calls.

**Request:**

```bash
DECISION_ID="d4e5f6a7-b8c9-0d1e-2f3a-4b5c6d7e8f90"
OUTCOME_KEY="outcome_$(date +%s)_001"

curl -sS -i -X POST "https://api.which-llm.com/decision/outcome" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $OUTCOME_KEY" \
  -d '{
    "decision_id": "'"$DECISION_ID"'",
    "option_used": "openai/gpt-4o-mini",
    "actual_cost": 0.008,
    "actual_latency": 650,
    "quality_score": 0.86,
    "success": true
  }'
```

**Request Fields:**

- `decision_id` (required): The `decision_id` from the optimize response
- `option_used` (required): The model ID that was actually used (should match `recommended_model` or a fallback)
- `actual_cost` (required): Actual cost in USD (≥ 0)
- `actual_latency` (required): Actual latency in milliseconds (≥ 0)
- `quality_score` (required): Quality score 0-1
- `success` (required): Boolean indicating if the task succeeded

**Example Response (200 Success):**

```http
HTTP/2 200 OK
Content-Type: application/json

{
  "status": "recorded",
  "decision_id": "d4e5f6a7-b8c9-0d1e-2f3a-4b5c6d7e8f90",
  "outcome_hash": "0xdef456789abcdef456789abcdef456789abcdef456789abcdef456789abcdef",
  "refund_credit": {
    "status": "issued",
    "credit_id": "credit_abc123def456",
    "credit_amount_usdc": 0.005,
    "credit_token": "eyJ...SIGNED_JWT_TOKEN_USE_THIS_IN_X_CREDIT_TOKEN_HEADER...xyz"
  }
}
```

**Credit Token Details:**

- `credit_token`: A signed token you can use on future paid calls
- `credit_amount_usdc`: The discount amount (typically 50% of original payment, with decay over time)
- `credit_id`: Unique identifier for this credit

**Using the Credit Token:**

Save the `credit_token` and include it in future optimize requests:

```bash
# Use the credit_token value from your /decision/outcome response
CREDIT_TOKEN="eyJ...YOUR_CREDIT_TOKEN_FROM_OUTCOME_RESPONSE...xyz"

curl -sS -i -X POST "https://api.which-llm.com/decision/optimize" \
  -H "Content-Type: application/json" \
  -H "X-Credit-Token: $CREDIT_TOKEN" \
  -d '{
    "goal": "Extract key entities from support tickets",
    "constraints": {
      "min_quality_score": 0.75,
      "max_cost_usd": 0.02
    }
  }'
```

**Example Response (200 Success with Credit):**

```http
HTTP/2 200 OK
Content-Type: application/json

{
  "decision_id": "f7g8h9i0-j1k2-l3m4-n5o6-p7q8r9s0t1u2",
  "decision_version": "v1",
  "deterministic": true,
  "recommended_model": "anthropic/claude-3-haiku",
  "expected_cost": 0.012,
  "expected_quality": 0.78,
  "safe_to_execute": true,
  "human_review_required": false
}
```

**Note:** No payment was required because the credit token covered the full cost.

**Credit Behavior:**

- Credits reduce the `required_amount` on the next paid call
- If credit fully covers cost → 200 response (no payment needed)
- If credit partially covers → 402 with reduced `required_amount`
- Credits decay over time (50% decay after 30 days, expires after 90 days)
- Credits are single-use (redeemed after successful payment)
- Credits are bound to the payer address from the original decision

**Important Notes:**

- Credits are only issued for paid/verified decisions
- Each decision can only issue one credit per payer

## Troubleshooting

### Common Error Codes

#### `PAYMENT_REQUIRED` (402)

**Cause:** Endpoint requires payment but no valid payment proof was provided.  
**Resolution:**

1. Check the `required_amount` and `accepts` array in the response
2. Send exact USDC amount to the `pay_to` address on your chosen chain
3. Wait for transaction confirmation (1-3 blocks)
4. Retry request with payment proof headers

**Example Error Response:**

```json
{
  "error_code": "PAYMENT_REQUIRED",
  "required_amount": "0.01",
  "currency": "USDC",
  "accepts": [
    {
      "chain": "eip155:8453",
      "asset": "USDC",
      "pay_to": "0x...PAY_TO_ADDRESS...123xyz",
      "scheme": "exact"
    }
  ],
  "payment_reference": "decision_optimize_abc123"
}
```

#### `PAYMENT_INVALID` (402)

**Cause:** Payment amount doesn't match required amount, or payment verification failed.  
**Resolution:**

1. Verify you sent exactly `required_amount` (not more, not less)
2. Check transaction was confirmed on-chain
3. Ensure you're using the correct chain (CAIP-2 format in `X-Payment-Chain`)
4. Verify payment headers match actual transaction details

#### `PAYMENT_ALREADY_USED` (402)

**Cause:** This transaction hash was already used for a different request.  
**Resolution:**

- Each payment transaction can only be used once
- Send a new payment transaction for this request
- Use `Idempotency-Key` header to retry the same request with same payment

#### `NO_FEASIBLE_OPTIONS` (400)

**Cause:** No models satisfy both cost and quality constraints.  
**Resolution:**

1. Check `constraint_analysis` in error response for which constraint was violated more
2. Relax constraints: increase `max_cost_usd` or decrease `min_quality_score`
3. Review `discarded_models` to see which models were close to meeting requirements

**Example Error Response:**

```json
{
  "error_code": "NO_FEASIBLE_OPTIONS",
  "constraint_analysis": {
    "cost_violations": 12,
    "quality_violations": 3,
    "total_models_evaluated": 15
  },
  "discarded_models": [
    {
      "option_id": "openai/gpt-4",
      "discard_reason": "MAX_COST"
    }
  ],
  "suggestions": {
    "relax_cost": true,
    "relax_quality": false
  }
}
```

#### `DECISION_NOT_FOUND` (400)

**Cause:** The `decision_id` doesn't exist in the system.  
**Resolution:**

- Verify the `decision_id` from your optimize response
- Only paid/verified decisions can have outcomes reported
- Check for typos in the decision ID

### Payment Verification Failures

#### Transaction not found on-chain

**Symptoms:** `PAYMENT_INVALID` error even though transaction was sent.  
**Resolution:**

1. Wait longer - blockchain confirmation can take 30-60 seconds
2. Verify transaction was sent to correct network (Base = 8453, not Ethereum = 1)
3. Check transaction status on block explorer (Basescan, Etherscan)
4. Ensure RPC nodes are synced (occasional issue during high network congestion)

#### Wrong payment amount

**Symptoms:** `PAYMENT_INVALID` with diagnostic showing amount mismatch.  
**Resolution:**

- Must send **exactly** the `required_amount` in USDC (6 decimals)
- Do not round or approximate - use exact value from 402 response
- Check USDC balance and allowances in your wallet
- Ensure wallet has sufficient gas token (ETH/AVAX) for transaction fees

#### Wrong recipient address

**Symptoms:** Transaction confirmed but API returns `PAYMENT_INVALID`.  
**Resolution:**

1. **CRITICAL:** Verify you sent to the correct address from multiple sources
2. Check `pay_to` field in 402 response `accepts` array
3. Verify address matches what's shown at `/docs/payment-addresses`
4. If addresses don't match, **DO NOT PROCEED** - contact support

### Credit Token Issues

#### `CREDIT_INVALID` (402)

**Cause:** Credit token is malformed, expired, or verification failed.  
**Resolution:**

1. Check token wasn't truncated when copying
2. Verify token matches exactly what was returned from `/decision/outcome`
3. Credits expire after 90 days - check `issued_at_epoch` in original response
4. Ensure you're using the token on the same payer address

#### `CREDIT_ALREADY_USED` (402)

**Cause:** This credit was already redeemed in a previous request.  
**Resolution:**

- Credits are single-use only
- Check `redeemed_at_epoch` in error response
- Request new credit by reporting another outcome

#### Credit doesn't reduce payment amount

**Symptoms:** 402 response shows same `required_amount` even with valid credit.  
**Resolution:**

1. Verify credit token is included in `X-Credit-Token` header
2. Check credit `amount_usdc` - may be smaller than expected due to time decay
3. Credits only apply to the next paid call after issuance
4. Ensure payer address matches the address that received the credit

### Rate Limiting

#### `RATE_LIMIT_EXCEEDED` (429)

**Symptoms:** `429 Too Many Requests` response with `X-RateLimit-*` headers.  
**Resolution:**

1. Check `X-RateLimit-Reset` header for when limit resets (epoch timestamp)
2. Implement exponential backoff: wait 1s, 2s, 4s, 8s between retries
3. Use `Idempotency-Key` to safely retry the same request
4. Consider using paid endpoints which have higher rate limits

**Rate Limits (per minute):**

- `/decision/optimize` unpaid: 5 requests
- `/decision/optimize` paid: 20 requests
- `/decision/outcome`: 60 requests
- Public GET endpoints: 600 requests

**Example Error Response:**

```json
{
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after_seconds": 45
}
```

**Response Headers:**

```txt
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1770809760
```
