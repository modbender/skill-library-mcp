---
name: bridge-tokens
description: Bridge tokens from one chain to another without swapping. Simplified cross-chain transfer where the output token is the same as the input token. Use when the user wants to move tokens between chains.
model: opus
allowed-tools: [Task(subagent_type:cross-chain-executor), mcp__uniswap__getSupportedChains, mcp__uniswap__getTokenInfo]
---

# Bridge Tokens

## Overview

Bridges tokens from one chain to another — a simplified cross-chain operation where the token stays the same (e.g., USDC on Ethereum to USDC on Base). Delegates to the `cross-chain-executor` agent with `tokenOut = tokenIn` to streamline the workflow.

This is the simpler sibling of `cross-chain-swap`. Use this when the user just wants to move tokens, not swap them.

## When to Use

Activate when the user asks:

- "Bridge 1000 USDC from Ethereum to Base"
- "Move my ETH to Arbitrum"
- "Transfer USDC to Optimism"
- "Send tokens to another chain"
- "Bridge tokens"
- "Move all my USDC from Polygon to Base"

## Parameters

| Parameter        | Required | Default    | Description                                           |
| ---------------- | -------- | ---------- | ----------------------------------------------------- |
| token            | Yes      | —          | Token symbol or address to bridge                     |
| amount           | Yes      | —          | Amount to bridge (human-readable)                     |
| sourceChain      | Yes      | —          | Source chain name (e.g., "ethereum")                  |
| destChain        | Yes      | —          | Destination chain name (e.g., "base")                 |
| recipient        | No       | Same wallet| Recipient address on destination chain                |

## Workflow

1. **Extract parameters** from the user's request. Identify:
   - Which token to bridge.
   - The amount.
   - Source and destination chains.
   - Resolve the same token's address on both chains via `mcp__uniswap__getTokenInfo`.

2. **Validate inputs**:
   - Verify both chains are supported via `mcp__uniswap__getSupportedChains`.
   - Verify the token exists on both chains.
   - If source and destination chain are the same: inform the user no bridge is needed.

3. **Delegate to cross-chain-executor**: Invoke `Task(subagent_type:cross-chain-executor)` with:
   - tokenIn = token (on source chain).
   - tokenOut = same token (on destination chain).
   - amount, sourceChain, destChain, recipient.
   - The agent handles quoting, safety, execution, monitoring, and confirmation.

4. **Present results**: Format the bridge report for the user, highlighting:
   - Amount sent and received (should be very close, minus bridge fee).
   - Bridge fee.
   - Settlement time.

## Output Format

```text
Bridge Complete

  Token:       USDC
  Sent:        1,000.00 USDC on Ethereum
  Received:    999.50 USDC on Base
  Bridge Fee:  0.50 USDC ($0.50)
  Settlement:  1 min 48 sec

  Source Tx:   0xabc...123
  Bridge ID:   0x789...abc
  Dest Tx:     0xdef...456

  Risk: LOW | Safety: APPROVED
```

## Important Notes

- Bridge operations transfer the same token between chains. The received amount will be slightly less due to bridge fees.
- Settlement times vary by chain pair (typically 1-10 minutes).
- Not all tokens are bridgeable between all chains. The executor will check availability.
- For moving tokens AND swapping to a different token, use `cross-chain-swap` instead.

## Error Handling

| Error                        | User-Facing Message                                              | Suggested Action                       |
| ---------------------------- | ---------------------------------------------------------------- | -------------------------------------- |
| Token not available on dest  | "[Token] is not available on [destChain]."                       | Use cross-chain-swap to swap to a native token |
| Same chain                   | "Source and destination are the same chain. No bridge needed."   | No action needed                       |
| Unsupported chain            | "Chain [name] is not supported."                                 | Check supported chains                 |
| Safety veto                  | "This bridge was blocked by safety checks: [reason]."           | Reduce amount or check configuration   |
| Bridge stuck                 | "Bridge settlement is delayed. Monitoring continues."            | Wait — recovery instructions provided  |
| Insufficient balance         | "Not enough [token] on [chain]."                                 | Check balance and reduce amount        |
