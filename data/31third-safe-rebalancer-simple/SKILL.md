---
name: 31third-safe-rebalancer-simple
description: One-step Safe rebalancer using on-chain 31Third policies.
homepage: https://31third.com
---

# 31Third Safe Rebalancer Simple

This skill is intentionally minimal for non-technical users.

Best practice: use only one command / one tool:

- `rebalance_now`
- `verify_deployment_config` (post-deploy troubleshooting)

If you are unsure, use the help command first:

- `npm run cli -- help`

## Prerequisites

- Node.js 22+
- npm

## Local Setup

```bash
npm install
npm run build
```

## Setup

1. Deploy your Safe + policies using the 31Third policy wizard:
   <https://app.31third.com/safe-policy-deployer>
2. You need at least two wallets:
   - Safe owner wallet: never share this private key.
   - Executor wallet: configured in the wizard on `ExecutorModule`; this private key is used by this skill.
3. Copy env vars from the final wizard overview.

Required env vars:

```bash
SAFE_ADDRESS=0xYourSafe
EXECUTOR_MODULE_ADDRESS=0xYourExecutorModule
EXECUTOR_WALLET_PRIVATE_KEY=0x...
TOT_API_KEY=your_31third_api_key
RPC_URL=https://mainnet.base.org
CHAIN_ID=8453
```

`TOT_API_KEY` can be requested via <https://31third.com/contact> or by emailing `dev@31third.com`.

## What rebalance_now does

1. Reads `AssetUniverse` and `StaticAllocation` policy state from `ExecutorModule`.
2. Builds `baseEntries` from current Safe balances for AssetUniverse tokens.
3. Builds `targetEntries` from on-chain StaticAllocation targets.
4. Calls SDK `calculateRebalancing(...)`.
5. Executes via SDK `executeRebalancing(...)` using ethers wallet signer.
6. Waits for confirmation and returns tx hash.

Safety checks:

- Fails if `scheduler != registry`.
- Fails if executor wallet is not equal to `registry`.
- Fails if required policies are missing.
- Loads `driftThresholdBps` from StaticAllocation and skips execution when drift is below threshold.
- Loads `maxSlippageBps` from SlippagePolicy and uses:
  - `maxSlippage = policySlippage - 0.1%`
  - `maxPriceImpact = policySlippage - 0.1%`
- Uses default `minTradeValue = 0.1`.

Partial policy deployment behavior:

- If AssetUniverse is not deployed, base entries default to `[]`.
- If SlippagePolicy is not deployed, configured/default slippage values are used.
- If StaticAllocation is not deployed, auto target fetch is not possible.
  This is the only fallback case where you should pass manual `targetEntries`.
  Do this only when StaticAllocation policy is intentionally not deployed.
  CLI fallback example:
  `npm run cli -- rebalance-now --target-entries '[{"tokenAddress":"0x...","allocation":0.5},{"tokenAddress":"0x...","allocation":0.5}]'`

## CLI

```bash
npm run cli -- help
npm run cli -- rebalance-now
npm run cli -- rebalance-now --target-entries '[{"tokenAddress":"0x...","allocation":0.5},{"tokenAddress":"0x...","allocation":0.5}]'
npm run cli -- verify-deployment --troubleshooting-file ./summary.txt
npm run cli -- verify-deployment --troubleshooting-summary "Safe=0x..."
```

## Troubleshooting & Best Practices

If your rebalance fails, check these common issues:

### 1. Verify the deployed contracts vs your environment
Use the `verify-deployment` tool to verify the deployed contracts against your environment.
Copy the troubleshooting info from the Safe Policy Deployer (Step 4 or Step 5). It has the following schema:

```
Safe=0x123...456
ExecutorModule=0x123...456 | Deployed
Scheduler=0x123...456
Registry=0x123...456
BatchTrade=0xD20c024560ccA40288C05BAB650ac087ae9b0f6e
FeedRegistry=0x1d4999242A24C8588c4f5dB7dFF1D74Df6bC746A
CooldownSec=3600

AssetUniversePolicy=0x123...456 | Deployed
AssetUniverseAssets:
- USDC | 0x833589fcd6edb6e08f4c7c32d4f71b54bda02913
- WETH | 0x4200000000000000000000000000000000000006

StaticAllocationPolicy=0x123...456 | Deployed
StaticAllocationDriftThresholdPercent=0.50%
StaticAllocationToleranceThresholdPercent=0.50%
StaticAllocationTargets:
- USDC | 0x833589fcd6edb6e08f4c7c32d4f71b54bda02913 | AllocationPercent=10.00%
- WETH | 0x4200000000000000000000000000000000000006 | AllocationPercent=90.00%

SlippagePolicy=0x123...456 | Deployed
MaxSlippagePercent=0.50%
```

IMPORTANT: The framework is deployed with a Safe batch transaction. It might happen that an internal transaction runs
out of gas and fails. The batch transaction itself still succeeds, but not all policies might be deployed. In this case,
execution of rebalancings might fail.


### 2. "Policy failed: to token not allowed"
Your `AssetUniverse` policy is blocking the trade.
- **Fix:** Just use tokens that are allowed by the policy for rebalancing.

### 3. "Policy failed: minToReceive below..."
The trade slippage is too high.
- **Cause:** Low liquidity for the token pair (common with Aave `aTokens` or wrapped assets on new chains).
- **Fix:** Try setting maxSlippage and maxPriceImpact lower on the rebalancing calculation call.

### 4. "Missing StaticAllocation policy"
The script can't find a target allocation on-chain.
- **Fix:** Run verify-deployment and if policy not deployed on purpose you can rebalance into any allocation within the AssetUniverse.
