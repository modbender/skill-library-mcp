# Cost Tracking Log

This file tracks all subagent spawns and their costs. The Cost Governor skill reads multipliers from here.

**Note:** Replace references to `$WORKSPACE` with your actual workspace path, e.g. `~/.openclaw/workspace`

## Multipliers

These are applied to base token estimates. Adjust based on your actual ratios.

- **Creative:** 7.5x (open-ended writing, brainstorming, complex generation)
- **Research:** 3x (web search + synthesis, fact-finding)
- **Technical:** 2x (code, config, structured output)
- **Simple:** 1.5x (lookups, templates, short responses)

## Daily Budget (Optional)

Set your comfortable daily spend limit:
- **Daily:** $20.00
- **Weekly:** $100.00
- **Monthly:** $400.00

## Cost Log

| Date | Task | Model | Est. | Actual | Ratio | Notes |
|------|------|-------|------|--------|-------|-------|
| 2026-02-20 | PassiveIncomeResearcher | Opus | $3.50 | $4.20 | 1.2x | Research took longer than expected |
| 2026-02-20 | AIHardwareResearcher | Sonnet | $0.80 | $0.65 | 0.8x | Well-scoped query |

## How to Use

1. **Before spawning:** Cost Governor estimates cost, logs here
2. **After completion:** Update "Actual" column with real cost (from `/status` or provider dashboard)
3. **Weekly review:** Check "Ratio" column. If consistently off, update multipliers above.

## Tips

- **High ratios (>2x)?** Your tasks are running longer than estimated. Increase multipliers or scope tasks tighter.
- **Low ratios (<0.8x)?** You're overestimating. Decrease multipliers.
- **Wildly variable?** Task descriptions are too vague. Be more specific when spawning.

## Example Entry

```markdown
| 2026-02-21 | BookMoneyResearcher | Sonnet | $1.20 | $1.35 | 1.13x | Added market analysis mid-task |
```
