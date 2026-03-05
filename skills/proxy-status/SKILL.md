---
name: proxy-status
description: Check status of Proxy payment intents and transactions. Usage: /proxy-status [intent-id] or /proxy-status to see all recent.
disable-model-invocation: true
argument-hint: "[intent-id or blank for all]"
---

# Check Payment Status

View status of payment intents and transactions.

## Usage

```
/proxy-status              # Show all recent intents
/proxy-status int_abc123   # Show specific intent
```

## Instructions

### If $ARGUMENTS has intent ID:
```
Call: proxy.intents.get { intentId: "$ARGUMENTS" }
Show: status, merchant, amount, created time
If card issued: proxy.transactions.list_for_card
```

### If $ARGUMENTS is empty:
```
Call: proxy.intents.list
Group by status and display:
```

## Output Format

```
📊 Payment Status
─────────────────

⏳ Pending Approval (2)
  • $500.00 - Adobe Creative Cloud
  • $299.00 - Apple Store

✅ Active Cards (3)
  • $49.99 - Amazon (card ready)
  • $25.00 - Uber Eats (card ready)
  • $150.00 - Best Buy (used, $147.32 charged)

✓ Completed (5 this week)
  • $29.99 - Netflix - matched
  • $12.50 - Spotify - matched
  ...
```

## Status Legend

| Status | Icon | Meaning |
|--------|------|---------|
| pending | 🟢 | Card ready |
| pending_approval | ⏳ | Needs approval |
| card_issued | 💳 | Card active |
| matched | ✅ | Transaction completed |
| mismatched | ⚠️ | Amount/merchant mismatch |
| rejected | ❌ | Approval denied |
| expired | ⏰ | Intent expired |
