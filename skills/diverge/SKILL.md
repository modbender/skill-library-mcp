---
name: Diverge
description: Spawn multiple perspectives to evaluate a problem before converging on a solution.
---

## When to Diverge

Diverge when a single viewpoint isn't enough:
- **Product decisions** — Different user types have conflicting needs
- **Safety-critical** — Need doctor, lawyer, security expert perspectives
- **Creative work** — Multiple aesthetic directions before choosing
- **Complex trade-offs** — No obvious "right" answer

Don't diverge for:
- Simple tasks with clear answers
- Speed-critical requests
- Tasks where you already have high confidence

## How Many Perspectives

| Complexity | Perspectives | Examples |
|------------|--------------|----------|
| Low | 2-3 | Quick sanity check |
| Medium | 3-5 | Product feature review |
| High | 5-7 | Safety-critical, legal |

**Rule:** Enough to cover blind spots, not so many you can't synthesize.

## Choosing Perspectives

Match perspectives to the problem:

- **Product:** Power user, casual user, churned user, new user
- **Medical:** Doctor, patient, caregiver, insurance
- **Legal:** Lawyer, affected party, regulator
- **Technical:** Security, performance, maintainability
- **Content:** Target audience, critic, competitor

Check `personas.md` for common perspective templates.

## Synthesis

After collecting perspectives:
1. **Identify conflicts** — Where do perspectives disagree?
2. **Find common ground** — What do all perspectives agree on?
3. **Weigh by stakes** — Safety concerns > preferences
4. **Decide** — Make a call, document trade-offs

Check `synthesis.md` for conflict resolution patterns.

## Learning User Preferences

Track when divergence helped vs. was overkill. Adapt:
- User who values speed → diverge less, ask before spawning
- User who values thoroughness → diverge more proactively

---

**Related:** For routing tasks to sub-agents, see `delegate`. For iterating until success, see `loop`.
