---
name: easyclaw-skill
description: Run user-facing EasyClaw DEX actions from a self-contained skill folder. Use when an agent needs to submit user orders or check wallet/margin/order balances on EasyClaw without depending on external project directories.
version: 0.1.0
metadata:
  openclaw:
    homepage: https://github.com/ice-coldbell/easyclaw/tree/main/easyclaw-skill
    requires:
      env:
        - SOLANA_RPC_URL
        - ANCHOR_PROVIDER_URL
        - KEYPAIR_PATH
        - ANCHOR_WALLET
        - EASYCLAW_API_BASE_URL
        - EASYCLAW_WS_URL
        - EASYCLAW_API_TOKEN
        - ORDER_ENGINE_PROGRAM_ID
        - MARKET_REGISTRY_PROGRAM_ID
        - API_BASE_URL
        - BACKEND_WS_URL
        - WS_URL
        - API_AUTH_TOKEN
        - API_TOKEN
      bins:
        - node
        - npm
      config:
        - ~/.config/solana/id.json
    primaryEnv: KEYPAIR_PATH
---

# EasyClaw User DEX Skill

Run only user workflows:

- balance and open-order checks
- order submission (place order)
- backend position/order/fill/history/orderbook/chart queries
- authenticated agent/strategy controls and safety kill-switch
- realtime websocket monitoring and signal-driven auto order execution

Do not run admin/bootstrap/keeper workflows in this skill.

## Runtime & Credential Requirements

- Wallet signer source: `KEYPAIR_PATH` or `ANCHOR_WALLET` (fallback `~/.config/solana/id.json`).
- Solana RPC source: `SOLANA_RPC_URL` or `ANCHOR_PROVIDER_URL` (fallback `http://127.0.0.1:8899`).
- Backend endpoint source: `EASYCLAW_API_BASE_URL` / `EASYCLAW_WS_URL` (or alias vars in `backend-common.js`).
- Optional API credential: `EASYCLAW_API_TOKEN` (required for protected backend controls).
- Local process usage: onboarding probes `solana config get` and can spawn child Node.js processes for autotrade execution.
- Local file writes:
  - onboarding persists selected wallet envs into `easyclaw-skill/.env`
  - strategy onboarding writes files into `easyclaw-skill/state/strategies/`

## Command Interface

Use `{baseDir}/scripts/dex-agent.sh`:

```bash
# toolchain + environment diagnostics
{baseDir}/scripts/dex-agent.sh doctor

# install local skill dependencies
{baseDir}/scripts/dex-agent.sh install

# wallet, USDC, margin, and open orders
{baseDir}/scripts/dex-agent.sh balance
{baseDir}/scripts/dex-agent.sh balance --json

# submit order tx
{baseDir}/scripts/dex-agent.sh order --market-id 1 --side buy --type market --margin 1000000
{baseDir}/scripts/dex-agent.sh order --market-id 2 --side sell --type limit --margin 2000000 --price 3000000000

# backend REST queries
{baseDir}/scripts/dex-agent.sh backend positions --mine --limit 20
{baseDir}/scripts/dex-agent.sh backend position-history --mine --limit 20
{baseDir}/scripts/dex-agent.sh backend chart-candles --market BTCUSDT --timeframe 1m --limit 120
{baseDir}/scripts/dex-agent.sh backend orderbook-heatmap --exchange binance --symbol BTCUSDT --limit 30
{baseDir}/scripts/dex-agent.sh backend portfolio --period 7d
{baseDir}/scripts/dex-agent.sh backend strategy-templates
{baseDir}/scripts/dex-agent.sh backend agent-risk --agent-id agent-001

# realtime WS monitor
{baseDir}/scripts/dex-agent.sh watch --channels "agent.signals,portfolio.updates,market.price.BTCUSDT"

# realtime signal -> auto order execution
{baseDir}/scripts/dex-agent.sh autotrade --market-id 1 --margin 1000000 --min-confidence 0.75

# guided onboarding + strategy capture + autotrade start
{baseDir}/scripts/dex-agent.sh onboard --market-id 1 --margin 1000000
```

## Files

- `scripts/balance.js`: user balance and order summary
- `scripts/order-execute.js`: user order submission helper
- `scripts/backend.js`: backend REST API query helper
- `scripts/ws-watch.js`: backend websocket channel subscriber
- `scripts/realtime-agent.js`: signal-driven auto-order loop
- `scripts/onboard.js`: interactive onboarding flow (wallet selection, registration wait, strategy capture, autotrade kickoff)
- `scripts/backend-common.js`: backend endpoint/auth helpers
- `scripts/common.js`: PDA, signer, tx, and decode utilities
- `package.json`: local runtime dependencies
- `.env.example`: required environment keys

## Setup

1. Copy `.env.example` to `.env`.
2. Fill signer and RPC values.
3. Run `dex-agent.sh install`.
4. Run `dex-agent.sh balance` first to validate access.
5. Run `dex-agent.sh backend doctor` and `dex-agent.sh watch --channel system.status`.
6. Run `dex-agent.sh onboard --market-id <id> --margin <u64>` for guided onboarding.

For env definitions and option details, read [references/dex-env.md](references/dex-env.md).

## Safety

- Keep `KEYPAIR_PATH` and private keys local.
- Use devnet/localnet unless explicitly instructed otherwise.
- Confirm `ORDER_ENGINE_PROGRAM_ID` and `MARKET_REGISTRY_PROGRAM_ID` before placing orders.
