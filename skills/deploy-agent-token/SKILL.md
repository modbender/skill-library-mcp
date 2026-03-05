---
name: deploy-agent-token
description: Deploy an agent token with a Uniswap V4 pool — handles pool creation with configurable hooks (anti-snipe, dynamic fees, revenue share), initial liquidity bootstrapping, LP locking, and post-deployment monitoring. Use when the user wants to launch a token on Uniswap.
model: opus
allowed-tools: [Task(subagent_type:token-deployer)]
---

# Deploy Agent Token

## Overview

Automates the full lifecycle of launching a token on Uniswap V4: pool creation with configurable hooks, initial liquidity bootstrapping, LP token locking, and post-deployment monitoring. Delegates to the `token-deployer` agent which handles the critical first hours of a token's life — ensuring proper anti-snipe protections, correct initial pricing, sufficient liquidity depth, and locked LP tokens.

This skill exists because agent platforms like Clanker (585K+ tokens, $5B+ volume) and BankrBot need automated, safe pool creation. Misconfigured pools, missing anti-snipe hooks, or inadequate liquidity can destroy a launch.

## When to Use

Activate when the user asks:

- "Deploy a token for my agent"
- "Create a Uniswap V4 pool for my token"
- "Launch a token with anti-snipe protection"
- "Set up a pool with dynamic fees"
- "Deploy token on Base with locked liquidity"
- "Launch my agent token like Clanker"
- "Create a pool with revenue share hooks"
- "Bootstrap liquidity for my new token"

## Parameters

| Parameter          | Required | Default    | Description                                                                        |
| ------------------ | -------- | ---------- | ---------------------------------------------------------------------------------- |
| tokenAddress       | Yes      | --         | ERC-20 token contract address to create a pool for                                 |
| pairedToken        | No       | WETH       | Quote token to pair with (WETH, USDC, or address)                                  |
| chain              | No       | base       | Target chain for deployment (must support V4)                                      |
| initialPrice       | No       | --         | Desired price per token in the paired token (or derive from `targetMarketCap`)     |
| targetMarketCap    | No       | --         | Target market cap in USD — used to calculate initial price from total supply       |
| initialLiquidity   | Yes      | --         | Amount of each token to seed the pool (e.g., "1M AGENT + 10 WETH")                |
| hooks              | No       | anti-snipe | Hook configuration: "anti-snipe", "dynamic-fees", "revenue-share", or comma-separated combination |
| antiSnipeDelay     | No       | 2 blocks   | Anti-snipe delay period in blocks (ClankerHook model)                              |
| revenueSharePct    | No       | --         | Percentage of swap fees directed to token creator (if revenue-share hook enabled)   |
| lpLockDuration     | No       | 10 years   | How long to lock LP tokens (e.g., "10 years", "1 year", "6 months")               |
| vestingSchedule    | No       | --         | Optional vesting schedule for token allocations                                    |

### Hook Configuration Guide

- **Anti-snipe** (default, recommended): Prevents bot sniping at launch using a 2-block delay (ClankerHook model). Without this, bots can drain initial liquidity within seconds.
- **Dynamic fees**: Adjusts pool fees based on volatility or volume. Good for tokens with unpredictable early trading patterns.
- **Revenue share**: Directs a portion of swap fees to the token creator. Creates an ongoing revenue stream from trading activity.
- **TWAMM**: Time-weighted average market making for gradual price discovery during launch.

## Workflow

1. **Extract parameters** from the user's request. Determine the token address, paired token, chain, initial price or market cap, liquidity amounts, hook configuration, and LP lock duration. Validate that required parameters (token address, initial liquidity) are provided. If initial price is not specified but target market cap is, note that the agent will calculate the price from total supply.

2. **Delegate to `token-deployer` agent**: Invoke `Task(subagent_type:token-deployer)` with the extracted parameters. The agent executes a 7-step pipeline:
   - **Verify token**: Check token contract via metadata (name, symbol, decimals, supply, risk flags). Refuse if honeypot indicators detected.
   - **Configure hooks**: Select and validate V4 hooks, verify they are deployed on the target chain, calculate hook address requirements.
   - **Create pool**: Calculate sqrtPriceX96, construct pool key, simulate via safety-guardian, execute initialization.
   - **Bootstrap liquidity**: Delegate to lp-strategist for optimal range, add liquidity via position manager.
   - **Lock LP**: Transfer position NFT to time-locked vault, configure lock duration.
   - **Monitor**: Track price, volume, TVL, and anomalies during the critical first hours.
   - **Report**: Produce comprehensive deployment report.

   The agent internally delegates to `safety-guardian` (transaction validation) and `lp-strategist` (liquidity strategy).

3. **Present results**: Format the deployment report for the user, including pool address, hook configuration, liquidity details, LP lock status, and early monitoring data.

## Agent Delegation

```
Task(subagent_type:token-deployer)
  tokenAddress: <0x...>
  pairedToken: <WETH|USDC|address>
  chain: <base|ethereum|...>
  initialPrice: <price in paired token>
  targetMarketCap: <USD value>
  initialLiquidity: <amounts>
  hooks: <anti-snipe,dynamic-fees,revenue-share>
  antiSnipeDelay: <2 blocks>
  revenueSharePct: <percentage>
  lpLockDuration: <10 years>
  vestingSchedule: <schedule>
```

## Output Format

```text
Token Deployment Complete

  Pool:
    Address:    0x1234...abcd
    Chain:      Base (8453)
    Version:    V4
    Pair:       AGENT / WETH
    Fee:        0.30% (tick spacing: 60)
    Hooks:      Anti-snipe (2-block delay) + Dynamic fees
    Init Price: 0.001 WETH per AGENT

  Liquidity:
    Position:   #12345
    Amount:     1,000,000 AGENT + 10 WETH
    Range:      Full range
    Status:     Active

  LP Lock:
    Vault:      0x5555...6666
    Duration:   10 years (unlocks 2036-02-10)
    Position:   #12345

  Early Monitoring (1h):
    Price:      0.00105 WETH (+5.0%)
    Volume:     $45,000
    TVL:        $20,000
    Anomalies:  None detected

  Next Steps:
    - Monitor pool health over the first 24 hours
    - Consider adding more liquidity if TVL grows
    - Share pool address for community trading
```

## Important Notes

- Pool creation is irreversible. Every pool creation transaction is simulated via `safety-guardian` before broadcast.
- Anti-snipe hooks are enabled by default and strongly recommended. Without them, bots can front-run the launch and drain initial liquidity within seconds.
- All hook contracts must be deployed and verified on the target chain before they can be attached to a pool. Unverified hooks can steal funds.
- If an existing pool with significant liquidity already exists for the token pair, the agent will warn you and suggest adding to the existing pool instead.
- LP locking builds market confidence. The default 10-year lock follows the Clanker model. Shorter locks are possible but may reduce trader confidence.
- Initial price calculation is critical. The agent cross-checks the price against token supply and target market cap to prevent misconfiguration.
- Post-deployment monitoring runs during the first hours to detect anomalies (sandwich attacks, unusual trades, liquidity removal).

## Error Handling

| Error                        | User-Facing Message                                                                          | Suggested Action                                  |
| ---------------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| Token verification failed    | "Could not verify token at [address]: [reason]."                                             | Check the token contract address and chain        |
| Honeypot detected            | "Token has honeypot indicators. Refusing to create pool."                                    | Review the token contract for malicious code      |
| Pool already exists          | "A pool with $[X] TVL already exists for this pair. Consider adding liquidity instead."      | Use manage-liquidity to add to existing pool      |
| Hook not deployed            | "Hook contract [type] is not deployed on [chain]."                                           | Deploy the hook first or choose a different hook  |
| V4 not supported             | "Uniswap V4 is not deployed on [chain]."                                                     | Choose a chain with V4 support                    |
| Insufficient liquidity tokens| "Not enough [token] to seed the pool: have [X], need [Y]."                                   | Acquire more tokens or reduce initial liquidity   |
| Safety guardian vetoed        | "Transaction vetoed by safety-guardian: [reason]."                                            | Review the veto reason and adjust parameters      |
| LP lock failed               | "Could not lock LP tokens: [reason]."                                                        | Check vault contract availability on the chain    |
| Gas estimation failed        | "Could not estimate gas for pool creation on [chain]."                                       | Try again or check chain status                   |
