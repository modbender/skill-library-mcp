---
name: submit-limit-order
description: Submit a UniswapX Dutch auction limit order. Use when user wants to
  set a limit price, get MEV-protected execution, or submit an order that fills
  at the best available price. No gas cost until filled.
---


# Submit Limit Order

Submit a gasless UniswapX Dutch auction limit order.

## Activation

Use this skill when the user says any of:
- "Set a limit order"
- "Buy X at price Y"
- "Submit a UniswapX order"
- "Limit buy/sell"

## Input Extraction

| Parameter | Required | Default | Source |
|-----------|----------|---------|--------|
| `tokenIn` | Yes | — | Token name/symbol |
| `tokenOut` | Yes | — | Token name/symbol |
| `amount` | Yes | — | Numeric value |
| `chain` | No | ethereum | Chain name |
| `limitPrice` | No | market price | Target price |
| `expiry` | No | 5 minutes | Duration for Dutch auction decay |

## Workflow

1. **Validate inputs**: Check token allowlist, spending limits, and UniswapX support on the target chain.

2. **Get current market price**: Call `get_quote` to establish the baseline price.

3. **Submit order**: Call `submit_uniswapx_order` with:
   - tokenIn, tokenOut, amount, chain
   - orderType: "dutch" (default) or "priority"

4. **Monitor** (optional): Poll `get_uniswapx_order_status` until filled, expired, or cancelled.

5. **Report**:

```
Limit Order Submitted (UniswapX Dutch Auction)

  Input:   1,000 USDC
  Target:  0.310 WETH (limit: 1 WETH = $3,225)
  Decay:   $3,225 → $3,200 over 5 minutes
  Status:  PENDING
  Order:   0xORDER_HASH...

  Gas: $0.00 (gasless until filled)
  Monitoring: Will report when filled or expired.
```

## Error Handling

| Error | User Message | Suggested Action |
|-------|-------------|-----------------|
| `UNISWAPX_NOT_SUPPORTED` | "UniswapX not available on [chain]." | Use supported chain or execute-swap |
| `ORDER_EXPIRED` | "Order expired without fill." | Adjust limit price or increase expiry |
| `SAFETY_TOKEN_NOT_ALLOWED` | "TOKEN is not on allowlist." | Add token to config |
