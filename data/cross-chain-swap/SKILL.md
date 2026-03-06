---
name: cross-chain-swap
description: Execute a cross-chain token swap via Uniswap's bridge infrastructure. Handles quoting, safety validation, bridge monitoring, and destination confirmation. Use when the user wants to swap tokens across different chains.
model: opus
allowed-tools: [Task(subagent_type:cross-chain-executor), mcp__uniswap__getSupportedChains, mcp__uniswap__getTokenInfo]
---

# Cross-Chain Swap

## Overview

Executes a cross-chain token swap — swapping a token on one chain for a different (or same) token on another chain. Delegates the full workflow to the `cross-chain-executor` agent, which handles quoting, route evaluation, safety checks, bridge monitoring, and destination confirmation.

## When to Use

Activate when the user asks:

- "Swap ETH on Arbitrum for USDC on Base"
- "Cross-chain swap"
- "Buy USDC on Optimism using ETH from mainnet"
- "Move my ETH from Ethereum to Arbitrum and convert to USDC"
- "Swap tokens across chains"
- "Exchange X on chain A for Y on chain B"

## Parameters

| Parameter        | Required | Default    | Description                                          |
| ---------------- | -------- | ---------- | ---------------------------------------------------- |
| tokenIn          | Yes      | —          | Input token symbol or address on source chain        |
| tokenOut         | Yes      | —          | Output token symbol or address on destination chain  |
| amount           | Yes      | —          | Amount to swap (human-readable, e.g., "1.5" or "1000") |
| sourceChain      | Yes      | —          | Source chain name (e.g., "ethereum", "arbitrum")     |
| destChain        | Yes      | —          | Destination chain name (e.g., "base", "optimism")    |
| slippage         | No       | auto       | Slippage tolerance (e.g., "0.5" for 0.5%)           |
| recipient        | No       | Same wallet| Recipient address on destination chain               |

## Workflow

1. **Extract parameters** from the user's request. Identify:
   - Which token they want to send and on which chain.
   - Which token they want to receive and on which chain.
   - The amount to swap.
   - Resolve ambiguous chain references (e.g., "mainnet" = "ethereum").

2. **Validate inputs**:
   - Verify both chains are supported via `mcp__uniswap__getSupportedChains`.
   - Verify tokens exist on their respective chains via `mcp__uniswap__getTokenInfo`.
   - If source and destination chain are the same: redirect to `execute-swap` skill instead.

3. **Delegate to cross-chain-executor**: Invoke `Task(subagent_type:cross-chain-executor)` with:
   - tokenIn, tokenOut, amount, sourceChain, destChain, slippage, recipient.
   - The agent handles the full 7-step workflow: quote, risk assessment, safety check, execution, bridge monitoring, confirmation, and reporting.

4. **Present results**: Format the execution report for the user, highlighting:
   - Amounts sent and received.
   - Total fees (gas + bridge).
   - Settlement time.
   - Any warnings from safety or risk checks.

## Output Format

```text
Cross-Chain Swap Complete

  Source:      1.5 ETH on Ethereum
  Destination: 2,850.25 USDC on Base
  Fees:        $3.50 (gas: $2.50, bridge: $1.00)
  Settlement:  2 min 35 sec

  Source Tx:   0xabc...123
  Bridge ID:   0x789...abc
  Dest Tx:     0xdef...456

  Risk: LOW | Safety: APPROVED
```

## Important Notes

- Cross-chain swaps involve bridge operations that take time to settle (typically 1-10 minutes).
- The skill will monitor the bridge and report status updates during settlement.
- Bridge fees and slippage apply in addition to normal swap fees.
- If the bridge gets stuck, the executor will escalate with recovery instructions.

## Error Handling

| Error                        | User-Facing Message                                              | Suggested Action                     |
| ---------------------------- | ---------------------------------------------------------------- | ------------------------------------ |
| Unsupported chain            | "Chain [name] is not supported for cross-chain swaps."           | Check supported chains               |
| Same chain                   | "Source and destination are the same chain. Use a regular swap." | Use execute-swap skill               |
| Safety veto                  | "This swap was blocked by safety checks: [reason]."             | Reduce amount or check token         |
| Risk veto                    | "Risk assessment vetoed: [reason]."                              | Choose a different route or amount   |
| Bridge stuck                 | "Bridge settlement is taking longer than expected."              | Wait or check order ID manually      |
| Bridge failed                | "Bridge operation failed. Funds should remain on source chain."  | Check source wallet balance          |
| Insufficient balance         | "Not enough [token] on [chain] to execute this swap."            | Check balance and reduce amount      |
