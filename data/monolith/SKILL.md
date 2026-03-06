---
name: monolith
description: Secure crypto wallet for AI agents. Hardware-isolated keys (Apple Secure Enclave), ERC-4337 smart wallet, on-chain spending caps, default-deny policy engine.
homepage: https://github.com/slaviquee/monolith
source: https://github.com/slaviquee/monolith/tree/main/skill
metadata: {"openclaw":{"displayName":"Monolith — Crypto Wallet","source":"https://github.com/slaviquee/monolith/tree/main/skill","homepage":"https://github.com/slaviquee/monolith","os":["darwin"],"requires":{"bins":["MonolithDaemon"]},"install":[{"id":"daemon-pkg","kind":"download","label":"Install Monolith Daemon (macOS pkg)","url":"https://github.com/slaviquee/monolith/releases/download/v0.1.5/MonolithDaemon-v0.1.5.pkg","os":["darwin"]},{"id":"companion-zip","kind":"download","label":"Download Monolith Companion (macOS app zip)","url":"https://github.com/slaviquee/monolith/releases/download/v0.1.3/MonolithCompanion.app.zip","os":["darwin"]}]},"clawdbot":{"displayName":"Monolith — Crypto Wallet","source":"https://github.com/slaviquee/monolith/tree/main/skill","homepage":"https://github.com/slaviquee/monolith","os":["darwin"],"requires":{"bins":["MonolithDaemon"]},"install":[{"id":"daemon-pkg","kind":"download","label":"Install Monolith Daemon (macOS pkg)","url":"https://github.com/slaviquee/monolith/releases/download/v0.1.5/MonolithDaemon-v0.1.5.pkg","os":["darwin"]},{"id":"companion-zip","kind":"download","label":"Download Monolith Companion (macOS app zip)","url":"https://github.com/slaviquee/monolith/releases/download/v0.1.3/MonolithCompanion.app.zip","os":["darwin"]}]}}
---

# Monolith — Crypto Wallet Skill

Secure crypto wallet for OpenClaw agents. Monolith combines hardware-isolated keys (Apple Secure Enclave), on-chain spending controls, and policy-gated approvals so agents can transact safely without exposing private keys.

## Commands

| Command | What it does | Requires daemon? |
|---------|-------------|------------------|
| `send <to> <amount> [token] [chainId]` | Send ETH or USDC | Yes |
| `swap <amountETH> [tokenOut] [chainId]` | Swap ETH for tokens via Uniswap (Routing API with on-chain fallback) | Yes |
| `balance <address> [chainId]` | Check ETH and stablecoin balances | No (read-only) |
| `capabilities` | Show current limits, budgets, gas status | Yes |
| `decode <target> <calldata> <value>` | Decode a tx intent into human-readable summary | Yes |
| `panic` | Emergency freeze — instant, no Touch ID | Yes |
| `status` | Check daemon health and wallet info | Yes |
| `identity [query\|register]` | ERC-8004 identity operations | Partially |
| `setup` | Run setup wizard, show wallet status and config | Yes |
| `policy` | Show current spending policy | Yes |
| `policy update '<json>'` | Update spending policy (Touch ID required) | Yes |
| `allowlist <add\|remove> <address> [label]` | Add or remove address from allowlist (Touch ID required) | Yes |
| `audit-log` | Show the daemon audit log | Yes |

## Security Model

- **The skill is untrusted.** It only builds intents: `{target, calldata, value}`.
- The skill NEVER sets nonce, gas, chainId, fees, or signatures.
- The signing daemon (local macOS process) enforces all policy.
- Transactions within policy limits execute automatically (autopilot).
- Transactions that exceed limits or use unknown calldata require human approval via 8-digit code.
- Token approvals (`approve`, `permit`, etc.) ALWAYS require explicit approval.

## What requires approval?

- Transfers over per-tx or daily spending caps
- Transfers to non-allowlisted addresses
- Token approvals (approve, permit, setApprovalForAll)
- Unknown calldata (default-deny policy)
- Swaps above slippage limits

## What works on autopilot?

- ETH and USDC transfers within limits to allowlisted addresses
- Swaps on allowlisted DEXes (Uniswap) within slippage limits
- DeFi deposits/withdrawals on allowlisted protocols (Aave)
- Balance checks, status queries, decode requests

## Setup

1. Install Monolith from ClawHub: `clawhub install monolith`
2. Start a new OpenClaw session so the skill is loaded.
3. Install local macOS components from the install entries:
   - `MonolithDaemon-v0.1.5.pkg` (admin/root install)
   - `MonolithCompanion.app.zip` (extract app to `/Applications` and open once)
4. Start daemon first, then companion. If companion was opened before daemon, restart companion after daemon is running.
5. Run `monolith setup` to verify daemon/companion connectivity and wallet status.
6. Fund the wallet address with ETH on your chosen chain.
7. Start transacting.

### First-Install Notes (OpenClaw bot/operator)

- Approval flows (Touch ID + notifications) require an active logged-in macOS GUI session.
- Headless-only SSH sessions cannot complete biometric/notification approval steps.
- `monolith setup` is the canonical health check before attempting `send`, `swap`, `policy`, or `allowlist` commands.


## Error Handling

- If the daemon is not running, all signing commands will fail with a clear error
- If gas is low, the daemon will refuse transactions — fund the wallet with more ETH
- If the wallet is frozen, no outbound transactions are possible until unfrozen (requires Touch ID + 10min delay)
- Rate-limited by Pimlico? The daemon uses exponential backoff automatically

## Approval Flow

When a transaction exceeds policy limits or uses unknown calldata, the daemon
returns HTTP 202 with a reason, summary, and expiration. The agent should:

1. Present the approval reason and summary to the user.
2. Ask the user for the 8-digit approval code (displayed by the daemon's native macOS dialog).
3. Re-call `/sign` with the same intent plus the `approvalCode` field to confirm.

No separate approval script is needed -- the same `send` or `swap` command is
re-invoked with the approval code passed through the daemon.

## Swap Routing

Uses Uniswap Routing API when available; falls back to on-chain V3 fee-tier probing
(tries 3000, 500, 10000 bps tiers, picks best quote). The fallback ensures swap
intents can still be built when the API is down or returns unexpected results.

## Chains

- Ethereum Mainnet (chainId 1)
- Base (chainId 8453)
