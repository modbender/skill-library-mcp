---
name: x402-wach
description: DeFi risk analysis toolkit powered by WACH.AI via x402 payments using AWAL wallet custody. Use when the user asks to check if a token is safe, assess DeFi risk, detect honeypots, analyze liquidity, holder distribution, or smart contract vulnerabilities for tokens on Ethereum, Polygon, Base, BSC, or Solana. Costs 0.01 USDC per query on Base.
license: MIT
compatibility: Requires Node.js 18+, npm, network access, AWAL installed and authenticated, and a funded AWAL wallet with USDC on Base.
metadata:
  author: quillai-network
  version: "3.0"
  endpoint: https://x402.wach.ai/verify-token
  payment: 0.01 USDC on Base (automatic via x402)
---

# x402-wach — DeFi Risk Analysis

A DeFi risk analysis toolkit powered by WACH.AI, using x402 with AWAL-managed key custody.

## OpenClaw Hard Rules (Non-Negotiable)

When this skill is active, OpenClaw must follow all rules below:

1. **Never request or expose secrets**
   - Never ask for private keys, seed phrases, mnemonics, wallet export files, or raw signing material.
   - Never suggest using `wallet.json` or any local key file flow.

2. **AWAL-only custody path**
   - Always use AWAL-backed commands for setup and payments.
   - Treat legacy local-wallet instructions as invalid for this skill version.

3. **Run readiness checks before paid calls**
   - Before `verify-risk`, ensure AWAL is ready via `wallet setup` or `wallet doctor`.
   - If not ready, stop and guide user to login/fund flow.

4. **Respect payment guardrails**
   - Default max payment cap is `10000` atomic USDC (`$0.01`) per request.
   - Do not raise cap unless the user explicitly asks.

5. **Do not hide payment failure details**
   - If payment fails, surface clear reason and next action (auth, balance, network, command mismatch).
   - Do not claim success unless report payload is actually present.

6. **No blind retries that may duplicate spend**
   - For network/transient errors, retry once at most.
   - Keep the same request context and tell the user a retry was attempted.

7. **Always present source link in final report**
   - Prefer TokenSense URL pattern:
     - `https://tokensense.wach.ai/<chain>/<tokenAddress>`
   - Use API source only as fallback.

## When to Use This Skill

Use this skill when user asks to:

- assess DeFi risk for a token
- detect scam/honeypot patterns
- inspect holder concentration/liquidity quality
- review contract risk signals
- get risk/market/code score breakdown
- evaluate tokens across `eth`, `pol`, `base`, `bsc`, or `sol`

## Supported Chains

| Short Name | Chain               | Token Standard |
| ---------- | ------------------- | -------------- |
| `eth`      | Ethereum            | ERC-20         |
| `pol`      | Polygon             | ERC-20         |
| `base`     | Base                | ERC-20         |
| `bsc`      | Binance Smart Chain | BEP-20         |
| `sol`      | Solana              | SPL            |

Payment is always in USDC on Base, regardless of analysis chain.

## Command Playbook for OpenClaw

### 1) Readiness / Setup

Run:

```bash
x402-wach wallet setup
```

If setup says not ready, run:

```bash
x402-wach wallet doctor
x402-wach wallet login <EMAIL>
x402-wach wallet verify <FLOW_ID> <OTP>
x402-wach wallet balance
```

Interpretation:

- `✓ Ready to make x402 payments with AWAL` -> proceed to analysis.
- `AWAL wallet is not authenticated` -> run login + verify flow.
- `Insufficient USDC on Base` -> ask user to fund AWAL address.
- `Could not read AWAL balance/status` -> run doctor and show raw failure.

### 2) Risk Analysis

Run:

```bash
x402-wach verify-risk <TOKEN_ADDRESS> <CHAIN_SHORT_NAME>
```

Preferred cap-safe form:

```bash
x402-wach verify-risk <TOKEN_ADDRESS> <CHAIN_SHORT_NAME> --max-amount-atomic 10000
```

### 3) Optional Helpers

```bash
x402-wach wallet status
x402-wach wallet address
x402-wach chains
x402-wach guide
```

## Tool Result Interpretation Rules

### Readiness/Doctor Output

- **Contains `✓ Ready`** -> safe to proceed with paid analysis.
- **Contains `not authenticated`** -> require OTP login/verify.
- **Contains `Insufficient USDC`** -> request wallet funding on Base.
- **Contains command-help text from AWAL** -> command mismatch/version issue; run `x402-wach wallet doctor` and use supported subcommands shown.
- **Contains JSON parse errors** -> treat as AWAL output format mismatch; surface raw error and do not continue paid flow.

### verify-risk Output

- **`Token analysis complete!` + populated sections** -> success.
- **Header only with empty body** -> payload unwrap issue; report as tool parsing bug.
- **`No token found` / empty report** -> valid call, no token at address/chain.
- **402/payment error** -> wallet balance/cap/auth issue; user action required.

## Safety-Focused User Guidance

When blocked, provide this exact short path:

```bash
x402-wach wallet doctor
x402-wach wallet login <email>
x402-wach wallet verify <flowId> <otp>
x402-wach wallet balance
```

Then retry:

```bash
x402-wach verify-risk <TOKEN_ADDRESS> <CHAIN_SHORT_NAME> --max-amount-atomic 10000
```

## Programmatic Usage Pattern (Agent-Friendly)

```typescript
import {
  getAwalReadiness,
  validateTokenAddress,
  verifyTokenRisk,
} from "@quillai-network/x402-wach";

const token = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48";
const chain = "eth";

const validation = validateTokenAddress(token, chain);
if (!validation.valid) throw new Error(validation.error);

const readiness = await getAwalReadiness(10_000);
if (!readiness.ready) throw new Error(readiness.reasons.join("; "));

const report = await verifyTokenRisk(token, chain, { maxAmountAtomic: 10_000 });
console.log(report);
```

## Expected Report Sections

On successful analysis, formatted output can include:

- Market Data
- Risk Scores
- Honeypot Analysis
- Holders
- Liquidity
- Code Analysis
- Social & Community
- Source (TokenSense link) + report timestamp

## Absolute Prohibitions for OpenClaw

- Do not use or suggest `wallet create`, `wallet import`, or `wallet.json`.
- Do not ask user for private key or seed phrase.
- Do not increase spend cap silently.
- Do not claim analysis success when output parsing failed.
- Do not suppress AWAL raw errors when diagnosis is needed.
