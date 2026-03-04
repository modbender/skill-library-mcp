---
name: proxy-balance
description: Check Proxy account balance and available spending power. Shows pending intents and suggests funding if low.
disable-model-invocation: true
---

# Check Balance

Get current balance and spending power.

## Instructions

1. Call `proxy.balance.get`
2. Call `proxy.intents.list` to get pending intents

## Output Format

```
💰 Proxy Balance
────────────────
Available:  $X,XXX.XX USD
Pending:    X intents ($XXX.XX reserved)
────────────────
Net Available: $X,XXX.XX
```

If balance is low (< $100), add:
```
💡 Low balance. Use /proxy-fund for deposit instructions.
```

If there are pending approval intents, list them:
```
⏳ Pending Approval:
  • $XXX.XX - Merchant Name (intent_id)
```
