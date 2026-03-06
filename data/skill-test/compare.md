# Comparing Skills

A/B testing when multiple skills could work.

## Setup

Install candidates to separate folders:
```bash
npx clawhub install skill-a --dir /tmp/compare/skill-a
npx clawhub install skill-b --dir /tmp/compare/skill-b
```

## Comparison Process

1. **Define test task** — Same task for both skills
2. **Run through each** — Spawn sub-agents or trace manually
3. **Capture outputs** — What did each produce?
4. **Present side-by-side** — Show user both results

## Comparison Criteria

| Aspect | Skill A | Skill B |
|--------|---------|---------|
| Output quality | | |
| Ease of use | | |
| Token efficiency | | |
| Coverage | | |
| Clarity | | |

## Asking User

> "I tested both skills on [task]:
> - Skill A: [brief result/impression]
> - Skill B: [brief result/impression]
> 
> Which feels better to you? Any specific preference?"

## Recording Preference

Track for future recommendations:
- Which skill won
- Why (user's stated reason)
- Task context

## When Results Are Close

If both perform similarly:
- Check maintenance/updates
- Check author reputation
- Check community adoption
- Let user decide on gut feeling
