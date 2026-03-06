# Confidence Levels

Track certainty per preference. Escalate only through explicit user signals.

| Level | Meaning | Behavior |
|-------|---------|----------|
| **observed** | Seen 1x, not confirmed | Never assume, just note internally |
| **pattern** | Seen 2+x, not confirmed | Propose confirmation to user |
| **confirmed** | User said yes | Apply by default, stay alert to exceptions |
| **locked** | User said "always" | Apply without question |

## Escalation Rules

- `observed` → `pattern`: After 2+ consistent decisions in similar contexts
- `pattern` → `confirmed`: Only after explicit "yes" from user
- `confirmed` → `locked`: Only if user says "always" or "never ask again"
- Any level → `demoted`: If user overrides or expresses different preference

## Demotion

If user makes a choice that contradicts a stored preference:
1. Don't assume the preference changed
2. Ask: "I noticed you chose X instead of Y. Should I update your preference, or was this a one-time exception?"
3. Update level only after explicit response
