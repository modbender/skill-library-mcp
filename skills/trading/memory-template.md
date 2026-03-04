# Memory Template

Copy this structure to `~/trading/memory.md` on first use.

```markdown
# Trading Memory

## Profile

Primary market: 
Trading style interest: 
Current stage: demo | live-small | scaling
Risk comfort: conservative | moderate | aggressive

## Learning Progress

### Mastered
<!-- Concepts user demonstrates understanding of -->

### Currently Learning
<!-- Active focus areas -->

### To Explore
<!-- Topics mentioned but not yet covered -->

## Preferences

<!-- Specific preferences learned from conversations -->

## Journal Notes

<!-- Key lessons from trading journal discussions -->
```

## Trade Journal Template

For `~/trading/journal.md`:

```markdown
# Trade Journal

<!-- Format for practice/demo trades:
## YYYY-MM-DD

### Trade 1
- Instrument: 
- Direction: Long / Short
- Entry: [price] at [time]
- Stop: [price] (risk: $X or X%)
- Target: [price] (R:R = X:1)
- Exit: [price] at [time]
- Result: +$X / -$X (X%)
- Notes: Why entered, what went well/poorly
-->
```

## Progress Tracking

For `~/trading/progress.md`:

```markdown
# Learning Progress

## Concepts Covered

| Topic | Date | Confidence |
|-------|------|------------|
| Position sizing | | 1-5 |
| Stop losses | | 1-5 |
| Risk/reward | | 1-5 |
| Chart patterns | | 1-5 |
| Indicators | | 1-5 |

## Milestones

- [ ] Completed demo trading period
- [ ] Consistent demo results (30+ trades)
- [ ] Transitioned to live trading
- [ ] First profitable month
```

## Initial Directory Structure

Create on first activation:

```bash
mkdir -p ~/trading
touch ~/trading/{memory.md,journal.md,progress.md}
```
