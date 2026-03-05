---
name: 31third-safe-rebalancer
description: Policy-aware Safe portfolio rebalancing assistant for 31Third ExecutorModule.
homepage: https://31third.com
---

# 31Third Safe Rebalancer

This skill helps you monitor portfolio drift and prepare/execute policy-compliant rebalances on a Gnosis Safe through the 31Third `ExecutorModule`.

Best-practice usage:
- Use one-step execution by default: `npm run cli -- rebalance-now`.
- Only use separated tools (`check_drift`, `plan_rebalance`, `execute_rebalance`, etc.) if you explicitly understand each step and want manual control.
- If unsure, run `help` first (`npm run cli -- help`) and follow that guidance.

## Prerequisites

- Node.js 22+
- npm

## Local Setup

```bash
npm install
npm run build
```

## Getting Started

If you have not deployed your policy stack yet, deploy it first:
<https://app.31third.com/safe-policy-deployer>

Set required environment variables:

```bash
SAFE_ADDRESS=0xYourSafe
CHAIN_ID=8453
TOT_API_KEY=your_api_key
RPC_URL=https://mainnet.base.org
EXECUTOR_MODULE_ADDRESS=0xYourExecutorModule
EXECUTOR_WALLET_PRIVATE_KEY=0x...
ORACLE_MAX_AGE_SECONDS=3600
HEARTBEAT_INTERVAL_SECONDS=21600
```

`TOT_API_KEY` (31Third API key) can be requested via <https://31third.com/contact> or by emailing `dev@31third.com`.

Wallet model and key handling:

- Safe owner wallet: controls Safe ownership/governance operations. Never share this private key with the skill.
- Executor wallet: configured as executor on `ExecutorModule` in the wizard. This private key is required by the skill for `execute_rebalance`.
- The final step of the 31Third wizard provides an overview of all required environment variables. Use that as source of truth when configuring this skill.

## What This Skill Does

- Reads active on-chain policies from `ExecutorModule`.
- Computes current-vs-target drift (`check_drift`).
- Validates trades against Asset Universe + Slippage boundaries (`validate_trade`).
- Runs a configurable heartbeat monitor (`automation`) and returns an alert payload when drift exceeds threshold.
- Simulates and executes approved rebalance batches (`execute_rebalance`) with pre-execution `checkPoliciesVerbose` validation and one retry on unknown execution failures.
- Accepts SDK `plan_rebalance` output directly for execution (`txData` + `requiredAllowances`) and decodes batch trade calldata internally.
- Fast-fails execution if `scheduler != registry` on the `ExecutorModule`, printing both addresses.
- Generates SDK-based policy-aware trade plans (`plan_rebalance`) using current Safe balances (bounded by Asset Universe when present) as `baseEntries`.
- Provides one-command execution (`rebalance_now`) for non-technical users: drift check -> SDK plan -> execution.
- Returns setup and capability guidance (`help`).

## Execution Safety

Before execution, the agent provides a clear reason, for example:

- `BTC is at 54.00%, target is 50.00% (drift 400 bps). Rebalance required.`

The skill uses:

- Viem `publicClient` for all reads.
- Viem `walletClient` for execution.

## Execution Contract (Important)

When using SDK/trading-api rebalancing output, execution must follow this exact pattern:

1. Build approvals from `requiredAllowances` as `(tokenAddress, neededAllowance)`.
2. Decode `txData` as `batchTrade(trades, config)`.
3. Re-encode `encodedTradeData` as ABI tuple:
   - `tuple(string,address,uint256,address,uint256,bytes,bytes)[]`
   - `tuple(bool,bool)`
4. Run `checkPoliciesVerbose(tradesInput, configInput)` before submitting.
5. Read `scheduler` and `registry` from ExecutorModule.
6. Ensure the signing executor wallet address equals `registry` (required by `onlyRegistry`).
7. Only execute immediate path (`executeTradeNow(approvals, encodedTradeData)`) when `scheduler == registry`.
8. If `scheduler != registry`, fail fast and show both addresses.

This is the required execution semantics for this skill and should not be changed to raw passthrough calldata execution.

## CLI

Run the bundled CLI:

```bash
npm run cli -- help
npm run cli -- check-drift
npm run cli -- automation --last-heartbeat-ms 0
npm run cli -- plan-rebalance --signer 0xYourSigner --min-trade-value 100
npm run cli -- rebalance-now
npm run cli -- validate-trade --trade '{"from":"0x...","to":"0x...","fromAmount":"1000000000000000000","minToReceiveBeforeFees":"990000000000000000"}'
npm run cli -- execute-rebalance --trades '[{"exchangeName":"0x","from":"0x...","fromAmount":"1000000000000000000","to":"0x...","minToReceiveBeforeFees":"990000000000000000","data":"0x...","signature":"0x..."}]' --approvals '[{"token":"0x...","amount":"1000000000000000000"}]'
npm run cli -- execute-rebalance --rebalancing '{"txData":"0x...","requiredAllowances":[{"token":{"address":"0x..."},"neededAllowance":"1000000000000000000"}]}'
```

Read-only smoke preflight:

```bash
npm run smoke -- --signer 0xYourSigner
npm run smoke -- --trades '[...]' --approvals '[...]'
```

## Notes

- This skill is automation infrastructure, not investment advice.
- Validate behavior in test/staging before running in production.
