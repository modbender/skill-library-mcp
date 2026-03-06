---
name: autonomous-agent
description: CornerStone MCP x402 skill for agents. Tools for stock predictions, backtests, bank linking, and agent/borrower scores. Payment-protected MCP tools (run_prediction, run_backtest, link_bank_account, get_agent_reputation_score, get_borrower_score, by-email variants) with x402 flow (Aptos + Base). Skill handles 402 → pay → retry. Wallet attestation for onboarding. For marketplaces where agents download and use skills autonomously.
metadata: {"clawdbot":{"emoji":"📈","homepage":"https://github.com/FinTechTonic/autonomous-agent","requires":{"bins":["node","npm"]}}}
---

# CornerStone MCP x402 Skill (for Agents)

This skill gives you (the agent) a set of tools to: create and manage Aptos and EVM wallets, check balances, and call x402-paid MCP tools (stock prediction, backtest, bank linking, agent/borrower scores). **Payment is automatic** — when a paid tool returns 402, the skill signs, verifies, settles, and retries transparently. You just call the tool; the result comes back.

---

## Quick-start workflow

Follow this sequence on first use, then skip to the tool you need:

1. **Check wallets** → call `get_wallet_addresses` (no args).
2. **If empty** → call `create_aptos_wallet` then `create_evm_wallet`.
3. **Fund** → call `credit_aptos_wallet` (Aptos faucet) and `fund_evm_wallet` (EVM faucet instructions).
4. **Tell the user** to whitelist the returned addresses at `https://arnstein.ch/flow.html`.
5. **Check balance** → call `balance_aptos` (must have USDC for predictions/backtests) and/or `balance_evm` (must have ETH for bank linking).
6. **Use paid tools** → `run_prediction`, `run_backtest`, `link_bank_account`, or score tools.

> **Important:** Paid tools will fail with a wallet/whitelist error if the address has not been funded and whitelisted. Always verify wallets and balances first.

---

## Tool reference

### Wallet management tools (local)

#### `get_wallet_addresses`
- **Args:** none
- **Returns:** `{ aptos: [{ address, network }], evm: [{ address, network }] }` — may be empty arrays.
- **When to use:** Always call first before any wallet or paid tool action. Determines what exists.
- **Decision:** If both arrays are empty → create wallets. If only one is empty → create the missing one. If both have entries → proceed to balance check or paid tools.

#### `create_aptos_wallet`
- **Args:** `{ force?: boolean, network?: "testnet" | "mainnet" }` — defaults: force=false, network=testnet.
- **Returns:** `{ success, address, network, message }` or `{ success: false, message, addresses }` if wallet exists and force=false.
- **When to use:** When `get_wallet_addresses` returns empty `aptos` array, or user requests a new wallet.
- **Error handling:** If `success: false` and wallet already exists, either use the existing wallet or retry with `force: true` to add another.

#### `create_evm_wallet`
- **Args:** `{ force?: boolean, network?: "testnet" | "mainnet" }` — defaults: force=false, network=testnet.
- **Returns:** `{ success, address, network, message }` or `{ success: false, message, addresses }`.
- **Same pattern as** `create_aptos_wallet`.

#### `credit_aptos_wallet`
- **Args:** `{ amount_octas?: number }` — default 100,000,000 (= 1 APT).
- **Returns on devnet:** `{ success: true, address }` (programmatic faucet funded).
- **Returns on testnet:** `{ success: true, address, faucet_url }` (instructions only; no programmatic faucet).
- **Prerequisite:** Aptos wallet must exist (`create_aptos_wallet` first).
- **Note:** Funded APT is for gas; tools pay in USDC (~6¢). The user may need to acquire testnet USDC separately.

#### `fund_evm_wallet`
- **Args:** none
- **Returns:** `{ success: true, address, faucet_url, message }` (manual funding instructions).
- **Prerequisite:** EVM wallet must exist (`create_evm_wallet` first).
- **Note:** Returns a Base Sepolia faucet URL. The user must fund manually; there is no programmatic faucet.

### Balance tools (local)

#### `balance_aptos`
- **Args:** none
- **Returns:** `{ address, balances: { usdc, apt } }` or `{ error }`.
- **When to use:** Before calling `run_prediction`, `run_backtest`, or score tools to confirm sufficient USDC.

#### `balance_evm`
- **Args:** `{ chain?: string }` — default "base". Supported: `base`, `baseSepolia`, `ethereum`, `polygon`, `arbitrum`, `optimism`.
- **Returns:** `{ address, chain, balance, symbol }` or `{ error }`.
- **When to use:** Before calling `link_bank_account` to confirm sufficient ETH on Base Sepolia.
- **Note:** For testnet tools, use `chain: "baseSepolia"`.

### Paid MCP tools (x402 — payment handled automatically)

> All paid tools accept both Aptos and EVM payment. The skill picks the best option or follows `PREFERRED_PAYMENT_ORDER`. You never see 402 errors — just call the tool and get the result or an error message.

#### `run_prediction`
- **Args:** `{ symbol: string, horizon?: number }` — symbol is a stock ticker (e.g. "AAPL"), horizon is days (default 30).
- **Returns:** Prediction result object (forecast data, confidence intervals, etc.) or `{ error }`.
- **Cost:** ~6¢ USDC (Aptos or EVM).
- **Prerequisite:** Funded + whitelisted Aptos or EVM wallet.
- **Example call:** `run_prediction({ symbol: "AAPL", horizon: 30 })`

#### `run_backtest`
- **Args:** `{ symbol: string, startDate?: string, endDate?: string, strategy?: string }` — dates in "YYYY-MM-DD", strategy defaults to "chronos".
- **Returns:** Backtest result (returns, drawdown, sharpe, etc.) or `{ error }`.
- **Cost:** ~6¢ USDC.
- **Example call:** `run_backtest({ symbol: "TSLA", startDate: "2024-01-01", endDate: "2024-12-31", strategy: "chronos" })`

#### `link_bank_account`
- **Args:** none
- **Returns:** `{ link_token }` or account ID for Plaid bank linking, or `{ error }`.
- **Cost:** ~5¢ (EVM/Base).
- **Prerequisite:** Funded + whitelisted EVM wallet (Base Sepolia for testnet).

#### `get_agent_reputation_score`
- **Args:** `{ agent_address?: string, payer_wallet?: string }` — both optional; uses the configured wallet if omitted.
- **Returns:** `{ reputation_score: number }` (e.g. 100) or 403 if not allowlisted, or `{ error }`.
- **Cost:** ~6¢ via x402, or free with lender credits (pass `payer_wallet`).

#### `get_borrower_score`
- **Args:** `{ agent_address?: string, payer_wallet?: string }` — same pattern.
- **Returns:** `{ score: number }` (100 base; higher with bank linked) or `{ error }`.
- **Cost:** ~6¢ via x402, or free with lender credits.

#### `get_agent_reputation_score_by_email`
- **Args:** `{ email: string, payer_wallet?: string }` — resolves email to allowlisted agent.
- **Returns:** `{ reputation_score: number }` or `{ error }`.
- **Prerequisite:** `SCORE_BY_EMAIL_ENABLED` must be set on the server. Higher fee.

#### `get_borrower_score_by_email`
- **Args:** `{ email: string, payer_wallet?: string }` — same pattern.
- **Returns:** `{ score: number }` or `{ error }`.
- **Prerequisite:** `SCORE_BY_EMAIL_ENABLED` must be set on the server. Higher fee.

---

## Decision tree for common tasks

### "Run a prediction for X"
```
get_wallet_addresses
  → aptos empty? → create_aptos_wallet → credit_aptos_wallet → tell user to whitelist
  → aptos exists? → balance_aptos
    → has USDC? → run_prediction({ symbol: "X", horizon: 30 })
    → no USDC? → tell user to fund USDC, provide address
```

### "Link a bank account"
```
get_wallet_addresses
  → evm empty? → create_evm_wallet → fund_evm_wallet → tell user to whitelist
  → evm exists? → balance_evm({ chain: "baseSepolia" })
    → has ETH? → link_bank_account
    → no ETH? → fund_evm_wallet (returns faucet URL)
```

### "Get my scores"
```
get_wallet_addresses
  → has aptos or evm? → get_agent_reputation_score + get_borrower_score
  → neither? → create wallets first, whitelist, then query
```

---

## Error handling

| Error pattern | Meaning | What to do |
|--------------|---------|------------|
| `"No Aptos wallet"` | Wallet file missing | Call `create_aptos_wallet` |
| `"No EVM wallet"` | Wallet file missing | Call `create_evm_wallet` |
| `"already exist. Use force: true"` | Wallet exists, not overwriting | Use existing wallet, or pass `force: true` to add another |
| `"Payment verification failed"` | Insufficient funds or wrong asset | Check balance; tell user to fund the wallet |
| `"No Aptos wallet configured"` / `"No EVM wallet configured"` | Paid tool needs wallet that doesn't exist | Create the missing wallet type |
| `"Unsupported chain"` | Invalid chain name for `balance_evm` | Use one of: base, baseSepolia, ethereum, polygon, arbitrum, optimism |
| `"timed out after 300s"` | MCP call took too long | Retry once; the server may be under load |
| `"403"` or `"not allowlisted"` | Wallet not whitelisted | Tell user to whitelist address at https://arnstein.ch/flow.html |

---

## Setup (for the human installing this skill)

1. **Install:** `npm install` from repo root. Copy `.env.example` to `.env`.
2. **Configure:** Set wallet paths (`APTOS_WALLET_PATH`, `EVM_WALLET_PATH` or `EVM_PRIVATE_KEY`).
3. **Wallets:** Create via tools (`create_aptos_wallet`, `create_evm_wallet`) or CLI (`node src/setup-aptos.js`, `node src/setup.js`). Fund and whitelist all addresses at https://arnstein.ch/flow.html.

---

## CLI commands (from repo root)

| Task | Command |
|------|--------|
| Generate Aptos wallet | `npm run setup:aptos` |
| Generate EVM wallet | `npm run setup` |
| Show addresses for whitelist | `npm run addresses` |
| Credit Aptos (devnet) | `npm run credit:aptos` (set `APTOS_FAUCET_NETWORK=devnet`) |
| EVM balance | `npm run balance -- <chain>` |
| Transfer ETH/tokens | `npm run transfer -- <chain> <to> <amount> [tokenAddress]` |
| Swap tokens (Odos) | `npm run swap -- <chain> <fromToken> <toToken> <amount>` |
| Run skill demo | `npx cornerstone-agent "Run a 30-day prediction for AAPL"` |
| Attest Aptos wallet | `npm run attest:aptos` |
| Attest EVM wallet | `npm run attest:evm` |

---

**Source:** [FinTechTonic/autonomous-agent](https://github.com/FinTechTonic/autonomous-agent)
