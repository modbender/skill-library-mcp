---
name: Subscriptions
description: Build a personal subscription tracker for managing recurring payments, renewals, and cutting waste.
metadata: {"clawdbot":{"emoji":"🔄","os":["linux","darwin","win32"]}}
---

## Core Behavior
- User mentions subscription → add to tracker
- User asks about spending → surface totals
- Alert before renewals and price increases
- Create `~/subscriptions/` as workspace

## File Structure
```
~/subscriptions/
├── active/
│   ├── streaming.md
│   ├── software.md
│   └── services.md
├── cancelled.md
└── totals.md
```

## Subscription Entry
```markdown
## Netflix
- Cost: $15.99/month
- Billing: 15th
- Card: Visa •4242
- Last used: Yesterday
- Value: High
```

## Totals
```markdown
# totals.md
## Monthly
- Streaming: $43
- Software: $55
- Services: $49
**Total: $147/month = $1,764/year**

## Annual Renewals Coming
- Adobe: Sep 15 ($660)
- Amazon Prime: Oct 1 ($139)
```

## What To Track
- Cost and billing frequency
- Billing date and payment method
- Last time used
- Perceived value (essential/high/medium/low)

## What To Surface
- "You spend $165/month on subscriptions"
- "HBO unused for 3 weeks"
- "Adobe renews in 30 days — $660"
- "3 subscriptions bill this week"

## Review Triggers
- Unused 30+ days → suggest cancel
- Price increased → flag it
- Annual renewal approaching → remind 7 days before
- Quarterly prompt: "still getting value?"

## Cancelled Log
```markdown
# cancelled.md
## 2024
- Hulu: Feb 1 (never used) — saved $18/mo
```

## Progressive Enhancement
- Start: list all current subscriptions
- Add billing dates and costs
- Track usage patterns
- Quarterly review habit

## What NOT To Do
- Forget annual renewals until charged
- Ignore unused subscriptions
- Miss price increases
- Keep services "just in case"
