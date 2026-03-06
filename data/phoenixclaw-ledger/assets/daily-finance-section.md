# Daily Finance Section Template

Template for the finance section integrated into PhoenixClaw daily journals.

## Section Structure

```markdown
## 💰 Financial Summary

{{TRANSACTIONS}}

---
{{DAILY_SUMMARY}}
{{BUDGET_STATUS}}
{{INSIGHTS}}
```

## Full Template

```markdown
## 💰 Financial Summary

{{#each EXPENSES}}
> [!expense] {{icon}} {{time}} {{description}}
> {{details}} | **{{currency}}{{amount}}** | {{category}}
> *Source: {{source}}*

{{/each}}

{{#each RECEIPTS}}
> [!receipt] 💳 {{time}} {{platform}}
> ![[{{screenshot_path}}|300]]
> {{merchant}} | **{{currency}}{{amount}}** | {{category}}
> *Source: Screenshot*

{{/each}}

---
**Today:** {{CURRENCY}}{{DAILY_TOTAL}} spent
**This {{PERIOD}}:** {{CURRENCY}}{{PERIOD_TOTAL}} / {{CURRENCY}}{{BUDGET}} ({{PERCENT}}%)

{{#if BUDGET_ALERT}}
> [!warning] {{BUDGET_ALERT}}
{{/if}}

{{#if INSIGHT}}
> [!insight] 💡 {{INSIGHT}}
{{/if}}
```

## Variables

### Transaction Variables

| Variable | Description |
|----------|-------------|
| `{{EXPENSES}}` | Array of conversation-detected expenses |
| `{{RECEIPTS}}` | Array of screenshot-detected expenses |

### Summary Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{CURRENCY}}` | Currency symbol | ¥ |
| `{{DAILY_TOTAL}}` | Total spent today | 449.00 |
| `{{PERIOD}}` | Budget period name | month |
| `{{PERIOD_TOTAL}}` | Total spent in period | 3,280.00 |
| `{{BUDGET}}` | Budget limit | 5,000.00 |
| `{{PERCENT}}` | Percentage used | 66 |
| `{{BUDGET_ALERT}}` | Alert message (if any) | Budget at 80% |
| `{{INSIGHT}}` | Daily insight (if any) | Weekend spending up |

## Example Output

### Normal Day

```markdown
## 💰 Financial Summary

> [!expense] 🍜 12:30 Lunch
> Hotpot with colleagues | **¥150.00** | Food & Dining
> *Source: Conversation*

> [!receipt] 💳 14:32 WeChat Pay
> ![[assets/2026-02-02/receipt_001.jpg|300]]
> Luckin Coffee | **¥19.90** | Food & Dining
> *Source: Screenshot*

> [!expense] 🛒 18:00 Shopping
> New earbuds | **¥299.00** | Electronics
> *Source: Conversation*

---
**Today:** ¥468.90 spent
**This month:** ¥3,748.90 / ¥5,000.00 (75%)
```

### With Budget Warning

```markdown
## 💰 Financial Summary

> [!expense] 🍜 12:30 Lunch
> Restaurant | **¥85.00** | Food & Dining
> *Source: Conversation*

> [!expense] 🛒 15:00 Shopping
> Clothing | **¥450.00** | Shopping
> *Source: Conversation*

---
**Today:** ¥535.00 spent
**This month:** ¥4,283.00 / ¥5,000.00 (86%)

> [!warning] ⚠️ Budget at 86% with 8 days remaining
> Daily allowance: ¥89.63
```

### With Insight

```markdown
## 💰 Financial Summary

> [!receipt] 💳 19:30 Alipay
> ![[assets/2026-02-02/receipt_001.jpg|300]]
> Restaurant | **¥320.00** | Food & Dining
> *Source: Screenshot*

---
**Today:** ¥320.00 spent
**This month:** ¥2,100.00 / ¥5,000.00 (42%)

> [!insight] 💡 Weekend dining averages ¥280 vs ¥65 on weekdays
```

### No Spending Day

```markdown
## 💰 Financial Summary

*No expenses recorded today* ✨

---
**This month:** ¥2,100.00 / ¥5,000.00 (42%)
**Streak:** 2 no-spend days 🎉
```

### Income Day

```markdown
## 💰 Financial Summary

> [!income] 💰 10:00 Salary
> Monthly salary | **+¥15,000.00** | Income
> *Source: Conversation*

> [!expense] 🍜 12:30 Lunch
> Celebration lunch | **¥280.00** | Food & Dining
> *Source: Conversation*

---
**Today:** ¥280.00 spent | ¥15,000.00 received
**This month:** ¥2,380.00 / ¥5,000.00 (48%)
**Net:** +¥12,620.00
```

## Conditional Display

### Show Section If

- Any transactions today (expense or income)
- Budget alert is active
- Insight available

### Hide Section If

- No financial activity AND no alerts
- User has disabled finance section

### Collapse by Default If

- Only small transactions (total < daily average)
- All within normal range

## Section Order

In the journal, Financial Summary appears at order 45:

```
0-19:  Highlights
20-39: Moments
40-59: 💰 Financial Summary ← HERE
60-79: Reflections
80-89: Other plugins
90-100: Growth Notes
```

## Integration Notes

- Section uses PhoenixClaw Core's callout styling
- Images use Obsidian embed syntax
- Currency and language follow user config
- Amounts formatted with thousands separators
- Percentages rounded to whole numbers
