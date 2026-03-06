---
name: batch-swap
description: Execute multiple token swaps in sequence. Use when user wants to
  rebalance, swap into multiple tokens, or execute a multi-step trading plan.
  Each swap goes through full safety validation independently.
---


# Batch Swap

Execute multiple token swaps in sequence with independent safety validation per swap.

## Activation

Use this skill when the user says any of:
- "Swap X for Y and Z"
- "Rebalance to 50% ETH 50% USDC"
- "Buy 3 different tokens"
- "Execute these swaps: ..."

## Input Extraction

| Parameter | Required | Default | Source |
|-----------|----------|---------|--------|
| `swaps` | Yes | — | List of {tokenIn, tokenOut, amount} |
| `chain` | No | ethereum | Default chain for all swaps |
| `stopOnFailure` | No | true | Whether to halt on first failure |

## Workflow

1. **Parse all swaps** from the user's message. Confirm token symbols resolve.

2. **Pre-flight check**: Verify total spending within daily limits and sufficient balance for all swaps using `check_safety_status` and `get_agent_balance`.

3. **Sequential execution**: For each swap:
   - Launch `Task(subagent_type:trade-executor)` with swap parameters
   - Wait for confirmation before starting next swap
   - Update running balance between swaps
   - If `stopOnFailure=true` and swap fails, halt remaining swaps

4. **Report summary**:

```
Batch Swap Complete (3/3 succeeded)

  #  Swap              Amount In    Amount Out   Tx
  1  USDC → WETH      1,000 USDC   0.307 WETH   0xABC...
  2  USDC → WBTC      1,000 USDC   0.015 WBTC   0xDEF...
  3  USDC → UNI       1,000 USDC   142.3 UNI    0xGHI...

  Total gas: $1.26
```

## Error Handling

| Error | User Message | Suggested Action |
|-------|-------------|-----------------|
| `BATCH_PARTIAL_FAILURE` | "Swap #N failed. Remaining halted." | Review failed swap, re-run remaining |
| `INSUFFICIENT_BALANCE` | "Insufficient balance for full batch." | Reduce amounts |
| `SAFETY_AGGREGATE_LIMIT` | "Total batch exceeds daily limit." | Reduce total batch size |
