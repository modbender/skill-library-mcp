---
name: create-test-pool
description: >-
  Deploy a custom Uniswap pool on the local testnet with configurable parameters.
  Create pools with specific conditions (thin liquidity, wide spreads, exact tick
  ranges) to test agent behavior under controlled scenarios. Requires a running
  local testnet.
model: sonnet
allowed-tools:
  - mcp__uniswap__deploy_mock_pool
  - mcp__uniswap__fund_test_account
  - mcp__uniswap__get_pool_info
  - mcp__uniswap__search_tokens
---

# Create Test Pool

## Overview

Deploys a custom Uniswap pool on the local testnet with exact parameters you specify. This lets you create controlled test environments -- thin liquidity pools, extreme price ranges, specific fee tiers -- to test how agents behave under edge conditions.

**Why this is 10x better than doing it manually:**

1. **No Solidity scripting**: Creating a V3 pool manually requires calling `createAndInitializePoolIfNecessary`, computing `sqrtPriceX96`, calculating tick ranges, approving tokens, and calling `mint`. This does it all with natural language.
2. **Token resolution**: Say "WETH/USDC" and it resolves addresses, decimals, and sorts tokens correctly. No need to look up contract addresses.
3. **Automatic funding**: If the deployer account doesn't have enough tokens, the tool handles whale impersonation to fund the deployment.
4. **Price-to-tick conversion**: Specify a price like "2000" (USDC per WETH) and the tool computes the correct `sqrtPriceX96` and tick range.
5. **Edge case testing**: Create pools with $100 liquidity to test thin-market behavior, or pools at extreme prices to test boundary conditions.
6. **Verification**: After deployment, you can immediately query the pool with `get_pool_info` to confirm state.

## When to Use

Activate when the user says anything like:

- "Create a WETH/USDC pool with thin liquidity"
- "Deploy a test pool with 0.05% fee"
- "Set up a DAI/USDC pool at 1:1"
- "Create a pool with only $1000 liquidity"
- "Deploy a V2 pair for testing"
- "I need a pool with a narrow tick range"
- "Create a WBTC/WETH pool at the current price"
- "Set up a pool to test high slippage scenarios"

**Do NOT use** when no testnet is running (use `setup-local-testnet` first), or when the user wants to interact with existing mainnet pools (use `analyze-pool`).

## Parameters

| Parameter    | Required | Default   | How to Extract                                                           |
| ------------ | -------- | --------- | ------------------------------------------------------------------------ |
| token0       | Yes      | --        | First token: "WETH", "USDC", or a 0x address                            |
| token1       | Yes      | --        | Second token: "USDC", "DAI", or a 0x address                            |
| version      | No       | v3        | "v2" or "v3"                                                             |
| fee          | No       | 3000      | Fee tier: 100 (0.01%), 500 (0.05%), 3000 (0.3%), 10000 (1%)             |
| initialPrice | No       | --        | Price of token0 in token1 terms (e.g. 2000 for ETH at $2000)            |
| liquidityUsd | No       | 1,000,000 | Dollar value of initial liquidity                                        |
| tickLower    | No       | auto      | V3 lower tick (advanced users only)                                      |
| tickUpper    | No       | auto      | V3 upper tick (advanced users only)                                      |

## Workflow

### Step 1: Verify Testnet is Running

If the tool returns `TESTNET_NOT_RUNNING`, tell the user:

```text
No local testnet is running. Let me set one up first.
```

Then suggest using `setup-local-testnet` or offer to do it for them.

### Step 2: Extract Parameters

Parse the user's request carefully:

- **Token pair**: "WETH/USDC", "ETH/DAI", "WBTC/WETH"
  - Map "ETH" to "WETH" (Uniswap uses wrapped ETH)
- **Fee tier**: "0.05% fee" → 500, "0.3%" → 3000, "1%" → 10000, "0.01%" → 100
- **Price**: "at $2000" → initialPrice: 2000 (for WETH/USDC)
- **Liquidity**: "thin liquidity" → liquidityUsd: 1000, "$10M" → liquidityUsd: 10000000
- **Version**: "V2 pair" → version: "v2", default is "v3"

**Common liquidity descriptions:**
- "thin" / "low" / "shallow" → $1,000 - $10,000
- "moderate" / "normal" → $100,000 - $1,000,000
- "deep" / "high" → $10,000,000+

### Step 3: Fund Deployer If Needed

If the pool requires tokens the deployer might not have, call `mcp__uniswap__fund_test_account` first to ensure the deployer (account #1: `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`) has sufficient tokens.

### Step 4: Deploy the Pool

Call `mcp__uniswap__deploy_mock_pool` with the extracted parameters.

### Step 5: Verify and Present

Present the deployed pool with full details:

```text
Test Pool Deployed

  Pool:       WETH/USDC (V3, 0.05% fee)
  Address:    0xNEW...
  Price:      1 WETH = 2,000 USDC
  Liquidity:  ~$1,000,000
  Tick Range: -204714 to -199514 (±50% around current price)

  Token0: USDC  0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48  (6 decimals)
  Token1: WETH  0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2  (18 decimals)

  Test Scenarios This Pool Enables:
  - Swap testing: "Get a quote for 1 WETH → USDC"
  - LP testing: "Add liquidity to the WETH/USDC pool"
  - Price impact: "What's the price impact of swapping 100 WETH?"
  - Time-dependent: "Advance 7 days and check fee accumulation"
```

### Step 6: Suggest Follow-ups

```text
  Next Steps:
  - Query pool state: "Get info on pool 0xNEW..."
  - Test a swap against this pool
  - Create another pool with different parameters
  - Advance time to test fee accumulation: "Time travel 7 days"
```

## Important Notes

- **Tokens are automatically sorted.** Uniswap requires token0 < token1 by address. The tool handles this.
- **V3 pools need initialization.** The tool calls `createAndInitializePoolIfNecessary` which sets the initial price.
- **Default tick range is ±50%.** If no tick range is specified, liquidity is spread across a wide range around the initial price.
- **Deployer is Anvil account #1.** The first Anvil default account is used for deployment.
- **Pool may already exist on fork.** If you fork Ethereum and try to create a WETH/USDC 0.05% pool, it already exists. The tool will add liquidity to the existing pool.
- **V2 pools always have 0.3% fee.** The fee parameter is ignored for V2.

## Error Handling

| Error                          | User-Facing Message                                                    | Suggested Action                                    |
| ------------------------------ | ---------------------------------------------------------------------- | --------------------------------------------------- |
| `TESTNET_NOT_RUNNING`          | "No local testnet is running."                                         | Run setup-local-testnet first                       |
| `TESTNET_TOKEN_NOT_FOUND`      | "Cannot resolve token X."                                              | Use a well-known symbol or provide the 0x address   |
| `TESTNET_CONTRACT_NOT_FOUND`   | "NonfungiblePositionManager not found on this chain."                   | Fork Ethereum mainnet which has all V3 contracts    |
| `TESTNET_DEPLOY_POOL_FAILED`   | "Failed to deploy pool: {reason}"                                      | Check token balances, fund deployer if needed       |
