---
name: autonomous-agent
description: CornerStone MCP x402 skill for agents. Tools for stock predictions, backtests, bank linking, and agent/borrower scores. Payment-protected MCP tools with x402 flow (Aptos + Base). Skill handles 402 → pay → retry. Wallet attestation for onboarding. For marketplaces where agents download and use skills autonomously.
metadata: {"openclaw":{"emoji":"📈","homepage":"https://github.com/FinTechTonic/autonomous-agent","requires":{"bins":["node","npm"]},"primaryEnv":"MCP_SERVER_URL","skillKey":"autonomous-agent"},"clawdbot":{"emoji":"📈","homepage":"https://github.com/FinTechTonic/autonomous-agent","requires":{"bins":["node","npm"]}}}
---

# CornerStone MCP x402 Skill (for Agents)

Skill that gives **agents** tools to call x402-protected MCP endpoints: stock prediction, backtest, bank linking, and agent/borrower scores. **Payment is automatic** — the skill handles 402 → sign → verify → settle → retry transparently. Supports **wallet attestation** (signing) for onboarding (POST /attest/aptos, /attest/evm).

## Installation

When this skill is loaded from the **autonomous-agent** repo, the repo root is the parent of the skill folder `{baseDir}`. Clone and install from the repo root:

```bash
git clone https://github.com/FinTechTonic/autonomous-agent.git && cd autonomous-agent
npm install
```

Copy `.env.example` to `.env` and set:

- set `X402_FACILITATOR_URL` too
- `LLM_BASE_URL`, `HUGGINGFACE_API_KEY` or `HF_TOKEN`, `LLM_MODEL` – for inference
- `APTOS_WALLET_PATH`, `EVM_WALLET_PATH` (or `EVM_PRIVATE_KEY`) – for payments

## Quick-start workflow

1. `get_wallet_addresses()` – check what wallets exist.
2. If empty: `create_aptos_wallet()` + `create_evm_wallet()`.
3. Fund: `credit_aptos_wallet()` + `fund_evm_wallet()`.
4. Whitelist addresses at https://arnstein.ch/sse/flow.html.
5. Check balances: `balance_aptos()`, `balance_evm({ chain: "baseSepolia" })`.
6. Call paid tools: `run_prediction`, `run_backtest`, `link_bank_account`, or score tools.

## Run the skill (demo)

```bash
npx cornerstone-agent "Run a 30-day prediction for AAPL"
npx cornerstone-agent
npm run agent -- "..."
node src/run-agent.js "..."
```

## Wallet attestation (signing)

- Aptos: `npm run attest:aptos` or `npx cornerstone-agent-attest-aptos` — output to POST /attest/aptos
- EVM: `npm run attest:evm` or `npx cornerstone-agent-attest-evm` — output to POST /attest/evm

## Tool reference

### Wallet tools (local)
| Tool | Args | Returns |
|------|------|---------|
| `get_wallet_addresses` | none | `{ aptos: [{ address, network }], evm: [...] }` |
| `create_aptos_wallet` | `{ force?, network? }` | `{ success, address, network }` |
| `create_evm_wallet` | `{ force?, network? }` | `{ success, address, network }` |
| `credit_aptos_wallet` | `{ amount_octas? }` | devnet: funds directly; testnet: `{ faucet_url, address }` |
| `fund_evm_wallet` | none | `{ faucet_url, address, message }` |
| `balance_aptos` | none | `{ address, balances: { usdc, apt } }` |
| `balance_evm` | `{ chain? }` | `{ address, chain, balance, symbol }` |

### Paid MCP tools (x402 — payment automatic)
| Tool | Args | Returns | Cost |
|------|------|---------|------|
| `run_prediction` | `{ symbol, horizon? }` | Forecast data | ~6¢ |
| `run_backtest` | `{ symbol, startDate?, endDate?, strategy? }` | Performance metrics | ~6¢ |
| `link_bank_account` | none | `{ link_token }` | ~5¢ |
| `get_agent_reputation_score` | `{ agent_address?, payer_wallet? }` | `{ reputation_score }` | ~6¢ or credits |
| `get_borrower_score` | `{ agent_address?, payer_wallet? }` | `{ score }` | ~6¢ or credits |
| `get_agent_reputation_score_by_email` | `{ email, payer_wallet? }` | `{ reputation_score }` | higher |
| `get_borrower_score_by_email` | `{ email, payer_wallet? }` | `{ score }` | higher |

Whitelist the addresses the agent uses at https://arnstein.ch/sse/flow.html so the server allows those wallets.
