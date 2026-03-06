---
name: torch-liquidation-agent
description: Read-only lending market scanner for Torch Market on Solana. No wallet required. Scans lending markets, profiles borrower wallets, and scores loans by risk. Default info mode makes no state changes and requires only an RPC endpoint. Optional bot mode (requires wallet) can execute liquidations on positions that crossed the on-chain threshold.
license: MIT
metadata:
  author: torch-market
  version: "1.0.3"
  clawhub: https://clawhub.ai/mrsirg97-rgb/torchliquidationagent
  npm: https://www.npmjs.com/package/torch-liquidation-agent
  github: https://github.com/mrsirg97-rgb/torch-liquidation-bot
  agentkit: https://github.com/mrsirg97-rgb/solana-agent-kit-torch-market
  audit: https://github.com/mrsirg97-rgb/torch-liquidation-bot/blob/main/audits/audit_agent.md
compatibility: Requires solana-agent-kit ^2.0.0 and solana-agent-kit-torch-market ^3.0.8. Solana RPC endpoint required. Default info mode is fully read-only -- no wallet loaded, no signing, no state changes. Wallet keypair only needed for optional bot or watch mode.
---

# Torch Liquidation Agent

Read-only lending market scanner for [Torch Market](https://torch.market) on Solana. No wallet required. Only an RPC endpoint is needed to run the default mode.

Built on [solana-agent-kit-torch-market](https://www.npmjs.com/package/solana-agent-kit-torch-market) -- all Solana RPC calls, lending reads, SAID lookups, and (optional) transactions go through the agent kit plugin. This skill makes **no direct network calls** of any kind.

## What This Skill Does

This skill scans lending markets on Torch Market, a fair-launch DAO launchpad on Solana. Every migrated token on Torch has a built-in lending market where holders can borrow SOL against their tokens. When a borrower's collateral drops in value and their loan-to-value ratio exceeds 65%, the position becomes liquidatable on-chain per the protocol's rules.

The skill's core value is **risk analysis** -- it profiles borrowers, tracks price trends, and scores every loan by how likely it is to fail. In the default info mode, it's a read-only dashboard that requires no wallet and makes no state changes. An optional bot mode (wallet required, off by default) can act on positions that cross the protocol threshold.

### How It Works

```
scan all tokens with active lending
         |
    for each token:
         |
    find all borrowers with active loans
         |
    profile each borrower (SAID reputation + trade history)
         |
    score each loan (4-factor risk model)
         |
    if liquidatable + profitable → execute liquidation
    if high risk → keep watching closely
```

### Three Modes

| Mode | Purpose | Wallet | State Changes |
|------|---------|--------|---------------|
| `info` (default) | Display lending parameters for a token or all tokens | not required | none (read-only) |
| `bot` | Scan and score positions; execute liquidations when threshold is met | required | yes (transactions) |
| `watch` | Monitor your own loan health in real-time | required | optional (auto-repay) |

### Risk Scoring

Every loan is scored 0-100 on four weighted factors:

| Factor | Weight | What It Measures |
|--------|--------|------------------|
| LTV proximity | 40% | How close the position is to the 65% liquidation threshold |
| Price momentum | 30% | Is the collateral token's price trending down? (linear regression on recent snapshots) |
| Wallet risk | 20% | SAID trust tier + trade win/loss ratio. Low-reputation wallets with losing histories score higher |
| Interest burden | 10% | How much accrued interest is eating into the collateral margin |

Positions scoring above the configurable risk threshold (default: 60) are flagged as high-risk and monitored more closely.

## Architecture

```
packages/agent/src/
├── types.ts            — all interfaces and contracts
├── config.ts           — env vars → typed config
├── logger.ts           — structured logging with levels
├── utils.ts            — shared helpers
├── scanner.ts          — discovers tokens with active lending
├── wallet-profiler.ts  — SAID reputation + trade history analysis
├── risk-scorer.ts      — 4-factor weighted risk scoring
├── liquidator.ts       — executes liquidation transactions
├── monitor.ts          — main orchestration (scan + score loops)
└── index.ts            — entry point with mode routing
```

Each file handles a single responsibility. The bot runs two concurrent loops:

- **Scan loop** (default: every 60s) -- discovers tokens with active lending, snapshots prices
- **Score loop** (default: every 15s) -- profiles borrowers, scores loans, executes liquidations

## Network & Permissions

- **Default mode (`info`) is read-only** -- no wallet is loaded, no keypair is decoded, no signing occurs, no state changes. Only `RPC_URL` is required.
- **No direct network calls from this skill** -- zero `fetch()`, zero HTTP clients, zero outbound URLs in the source code. All outbound connections go through dependencies: Solana RPC (via `solana-agent-kit`) and SAID Protocol API (via `solana-agent-kit-torch-market`). No telemetry or third-party services. Confirmed by audit (`audits/audit_agent.md`, finding I-1).
- **Private keys never leave the process** -- when a wallet is provided (bot/watch mode only), it is decoded once, wrapped in `KeypairWallet`, and used only for signing via `SolanaAgentKit`. The raw key bytes are never logged, serialized, stored, or transmitted. Confirmed by audit (finding I-2).
- **Distributed via npm** -- all code runs from `node_modules/`. No post-install hooks, no remote code fetching.
- **Transactions are constructed by the agent kit plugin** (`solana-agent-kit-torch-market`) and signed client-side via `SolanaAgentKit`. The on-chain program validates all parameters.

## Available Actions

All actions are provided by the `solana-agent-kit-torch-market` plugin. This skill contains no direct network calls -- every outbound connection is routed through the plugin.

### Read-only actions (no wallet, no signing, no state changes)

These are the only actions used in the default `info` mode:

| Action | Description |
|--------|-------------|
| `TORCH_LIST_TOKENS` | Discover migrated tokens with active lending markets |
| `TORCH_GET_TOKEN` | Get token price and metadata for collateral valuation |
| `TORCH_GET_LENDING_INFO` | Get lending parameters -- rates, thresholds, treasury balance |
| `TORCH_GET_LOAN_POSITION` | Get a borrower's loan health, LTV, collateral, and debt |
| `TORCH_GET_MESSAGES` | Read trade history for borrower wallet profiling |
| `TORCH_VERIFY_SAID` | Check SAID Protocol verification status and trust tier for a wallet |

### Write actions (wallet required, off by default)

Only used when `MODE=bot` or `MODE=watch` is explicitly set:

| Action | Description |
|--------|-------------|
| `TORCH_LIQUIDATE_LOAN` | Execute a liquidation on an underwater position |
| `TORCH_REPAY_LOAN` | Repay borrowed SOL (used in watch mode auto-repay) |
| `TORCH_CONFIRM` | Report transaction to SAID Protocol for reputation |

## Methods

### Read Operations (no wallet required)

```typescript
import {
  torchListTokens,
  torchGetToken,
  torchGetLendingInfo,
  torchGetLoanPosition,
  torchGetMessages,
} from "solana-agent-kit-torch-market"

// Discover tokens with active lending
const tokens = await torchListTokens(agent, "migrated", "volume", 50)

// Get token price for collateral valuation
const token = await torchGetToken(agent, "MINT_ADDRESS")

// Get lending parameters
const lending = await torchGetLendingInfo(agent, "MINT_ADDRESS")
// lending.interest_rate_bps      -- 200 (2%)
// lending.liquidation_threshold_bps -- 6500 (65%)
// lending.liquidation_bonus_bps  -- 1000 (10%)
// lending.treasury_sol_available  -- SOL available for borrowing

// Get a borrower's loan health
const position = await torchGetLoanPosition(agent, "MINT_ADDRESS", "BORROWER_ADDRESS")
// position.health          -- "healthy" | "at_risk" | "liquidatable" | "none"
// position.current_ltv_bps -- current loan-to-value in basis points
// position.collateral_amount -- tokens locked as collateral
// position.total_owed      -- principal + accrued interest

// Get trade messages for wallet profiling
const messages = await torchGetMessages(agent, "MINT_ADDRESS", 50)
```

### Write Operations (wallet required)

```typescript
import {
  torchLiquidateLoan,
  torchRepayLoan,
  torchConfirm,
} from "solana-agent-kit-torch-market"

// Liquidate an underwater position (permissionless)
// Liquidator receives collateral + 10% bonus
const sig = await torchLiquidateLoan(agent, "MINT_ADDRESS", "BORROWER_ADDRESS")

// Repay borrowed SOL (interest first, then principal)
const sig = await torchRepayLoan(agent, "MINT_ADDRESS", 600_000_000) // lamports

// Confirm transaction for SAID reputation
const result = await torchConfirm(agent, "TX_SIGNATURE")
// result.confirmed: boolean
// result.event_type: "trade_complete" (+5 reputation)
```

## Installation

```bash
npm install torch-liquidation-agent solana-agent-kit solana-agent-kit-torch-market
```

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `RPC_URL` | yes | -- | Solana RPC endpoint |
| `WALLET` | bot/watch only | -- | Solana wallet keypair (base58) |
| `MODE` | no | `info` | `info`, `bot`, or `watch` |
| `MINT` | no (info/watch) | -- | Token mint address for single-token modes |
| `SCAN_INTERVAL_MS` | no | `60000` | How often to discover new lending markets |
| `SCORE_INTERVAL_MS` | no | `15000` | How often to re-score positions |
| `MIN_PROFIT_SOL` | no | `0.01` | Minimum profit in SOL to execute a liquidation |
| `RISK_THRESHOLD` | no | `60` | Minimum risk score (0-100) to flag as high-risk |
| `PRICE_HISTORY` | no | `20` | Price snapshots to keep for momentum calculation |
| `LOG_LEVEL` | no | `info` | `debug`, `info`, `warn`, or `error` |
| `AUTO_REPAY` | no | `false` | Auto-repay your position if liquidatable (watch mode) |

## Run

```bash
# show lending info for all migrated tokens (default, no wallet needed)
RPC_URL=<rpc> npx torch-liquidation-agent

# show lending info for a specific token
MODE=info MINT=<mint> RPC_URL=<rpc> npx torch-liquidation-agent

# run the liquidation bot (requires wallet)
MODE=bot WALLET=<key> RPC_URL=<rpc> npx torch-liquidation-agent

# watch your own loan health (requires wallet)
MODE=watch MINT=<mint> WALLET=<key> RPC_URL=<rpc> npx torch-liquidation-agent
```

## Programmatic Usage

```typescript
import { SolanaAgentKit, KeypairWallet } from "solana-agent-kit"
import { Monitor, loadConfig } from "torch-liquidation-agent"

const config = loadConfig()
const monitor = new Monitor(config)

process.on("SIGINT", () => monitor.stop())
await monitor.start()
```

### Individual modules

```typescript
import { SolanaAgentKit, KeypairWallet } from "solana-agent-kit"
import { scanForLendingMarkets } from "torch-liquidation-agent/scanner"
import { WalletProfiler } from "torch-liquidation-agent/wallet-profiler"
import { scoreLoan } from "torch-liquidation-agent/risk-scorer"
import { Liquidator } from "torch-liquidation-agent/liquidator"
import { Logger } from "torch-liquidation-agent/logger"

const wallet = new KeypairWallet(keypair, rpcUrl)
const agent = new SolanaAgentKit(wallet, rpcUrl, {})
const log = new Logger("my-bot", "info")

// Discover lending markets
const tokens = await scanForLendingMarkets(agent, new Map(), 20, log)

// Profile a borrower
const profiler = new WalletProfiler(log)
const profile = await profiler.profile(agent, "BORROWER_ADDRESS", "MINT_ADDRESS")

// Score a loan
const scored = scoreLoan(token, "BORROWER_ADDRESS", position, profile)
// scored.riskScore: 0-100
// scored.estimatedProfitLamports: expected profit after fees
```

## Key Types

```typescript
interface ScoredLoan {
  mint: string
  tokenName: string
  borrower: string
  position: TorchLoanPosition  // health, LTV, collateral, debt
  walletProfile: WalletProfile // SAID tier, trade stats, risk score
  riskScore: number            // 0-100 composite
  factors: RiskFactors         // breakdown of all 4 scoring factors
  estimatedProfitLamports: number
}

interface WalletProfile {
  address: string
  saidVerified: boolean
  trustTier: "high" | "medium" | "low" | null
  tradeStats: TradeStats       // wins, losses, win rate, net PnL
  riskScore: number            // 0-100
}

interface MonitoredToken {
  mint: string
  name: string
  symbol: string
  lendingInfo: TorchLendingInfo  // rates, thresholds, treasury balance
  priceSol: number
  priceHistory: number[]         // for momentum calculation
  activeBorrowers: string[]
}
```

## SAID Protocol Integration

Borrower wallets are profiled using [SAID Protocol](https://saidprotocol.com) (Solana Agent Identity):

- **Read**: Wallet trust tier (`high` / `medium` / `low`) feeds into the 20% wallet risk factor
- **Write**: Call `torchConfirm()` after liquidations to build your agent's portable reputation (+5 per trade)

Low-reputation borrowers with losing trade histories score higher risk, meaning the bot watches their positions more closely.

## Lending Protocol Constants

| Parameter | Value |
|-----------|-------|
| Max LTV | 50% |
| Liquidation threshold | 65% LTV |
| Interest rate | 2% per epoch (~7 days) |
| Liquidation bonus | 10% of collateral value |
| Treasury utilization cap | 50% |
| Min borrow | 0.1 SOL |
| Token-2022 transfer fee | 1% on all transfers |

## Links

- npm: [npmjs.com/package/torch-liquidation-agent](https://www.npmjs.com/package/torch-liquidation-agent)
- Agent Kit Plugin: [npmjs.com/package/solana-agent-kit-torch-market](https://www.npmjs.com/package/solana-agent-kit-torch-market)
- Source Code: [github.com/mrsirg97-rgb/torch-liquidation-bot](https://github.com/mrsirg97-rgb/torch-liquidation-bot)
- ClawHub: [clawhub.ai/mrsirg97-rgb/torchliquidationagent](https://clawhub.ai/mrsirg97-rgb/torchliquidationagent)
- Torch Market: [torch.market](https://torch.market)
- SAID Protocol: [saidprotocol.com](https://saidprotocol.com)
- Program ID: `8hbUkonssSEEtkqzwM7ZcZrD9evacM92TcWSooVF4BeT`

## License

MIT
