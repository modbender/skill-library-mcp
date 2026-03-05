---
description: >-
  Execute a Uniswap token swap. Use when user wants to swap, trade, buy, or sell
  tokens. Handles quotes, safety checks, simulation, and execution autonomously.
  Supports V2, V3, V4, UniswapX, and cross-chain routing on all supported chains.
allowed-tools: >-
  Read, Glob, Grep,
  Task(subagent_type:trade-executor),
  mcp__uniswap__get_supported_chains,
  mcp__uniswap__search_tokens,
  mcp__uniswap__check_safety_status
model: opus
---

# Execute Swap

Execute a token swap on Uniswap with full safety validation.

## Activation

Use this skill when the user says any of:
- "Swap X for Y"
- "Buy X with Y"
- "Sell X for Y"
- "Trade X for Y"
- "Exchange X to Y"
- "Convert X to Y"

## Input Extraction

Extract these parameters from the user's message:

| Parameter | Required | Default | Source |
|-----------|----------|---------|--------|
| `tokenIn` | Yes | — | Token name/symbol/address |
| `tokenOut` | Yes | — | Token name/symbol/address |
| `amount` | Yes | — | Numeric value |
| `chain` | No | ethereum | Chain name or context |
| `slippage` | No | 0.5% | Explicit percentage |
| `routing` | No | auto | "via V3", "use UniswapX", etc. |

## Workflow

1. **Validate inputs**: Resolve token symbols using `search_tokens`. Confirm chain is supported.

2. **Pre-flight safety check**: Call `check_safety_status` to verify:
   - Spending limits have room for this trade
   - Rate limits are not exhausted
   - Circuit breaker is not tripped

3. **Delegate to trade-executor**: Launch `Task(subagent_type:trade-executor)` with:
   - tokenIn, tokenOut, amount, chain
   - slippageTolerance (in bps)
   - routingPreference (auto/v2/v3/v4/uniswapx)

4. **Report result** to the user in a clear format:

```
Swap Executed Successfully

  Input:  500.00 USDC
  Output: 0.1538 WETH ($499.55)
  Price:  1 WETH = $3,248.04
  Impact: 0.01%
  Gas:    $0.42

  Tx: https://basescan.org/tx/0xABC...

  Safety: All 7 checks passed
```

## Error Handling

| Error | User Message | Suggested Action |
|-------|-------------|-----------------|
| `SAFETY_SPENDING_LIMIT_EXCEEDED` | "This swap would exceed your $X daily limit." | Reduce amount or wait |
| `SAFETY_TOKEN_NOT_ALLOWED` | "TOKEN is not on your allowlist." | Add to config |
| `SAFETY_SIMULATION_FAILED` | "Swap simulation failed: [reason]." | Check addresses, try smaller |
| `INSUFFICIENT_LIQUIDITY` | "Not enough liquidity at acceptable slippage." | Try smaller amount |

## MCP server dependency

This skill relies on Uniswap MCP tools for chain support lookup, token search, safety checks, and swap execution.
When used in isolation (for example, from a skills catalog), ensure the Agentic Uniswap MCP server is running:

- Repo: [`Agentic-Uniswap` MCP server](https://github.com/wpank/Agentic-Uniswap/tree/main/packages/mcp-server)
- Package: `@agentic-uniswap/mcp-server`
