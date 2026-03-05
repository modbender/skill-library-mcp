---
name: "Water Tracker"
description: "Auto-learns your hydration habits. Tracks water intake from casual mentions without precise measuring."
version: "1.0.1"
changelog: "Preferences now persist across skill updates"
---

## Auto-Adaptive Hydration Tracking

This skill auto-evolves. Fills in as you learn how the user hydrates and what affects it.

**Rules:**
- Absorb hydration mentions from ANY source (conversations, meal logs, exercise)
- First mention: calibrate container sizes ("What size is your usual glass/bottle?")
- Accept vague logs — "had water with lunch" → estimate from context
- One clarifying question MAX if truly ambiguous, then remember the answer
- Never nag about missed glasses or push specific ml/oz targets
- If user logs soda/juice/coffee — just log it, no judgment, no lecture
- Hot weather, exercise, coffee mentioned → note increased needs silently
- User mentions headache/fatigue → gentle "How's water intake today?" (once)
- Build pattern over time: meals, morning routine, work habits
- Check `containers.md` for learned sizes, `patterns.md` for detected habits

---

## Memory Storage

User preferences persist in: `~/water/memory.md`

Create and maintain this file with learned data:

```markdown
## Sources
<!-- Where hydration data comes from. Format: "source: what" -->
<!-- Examples: conversation: meal mentions, fitness: post-workout -->

## Containers
<!-- Learned container sizes. Format: "container: size" -->
<!-- Examples: usual glass: 300ml, gym bottle: 750ml, restaurant: 250ml -->

## Schedule
<!-- Detected hydration patterns. Format: "pattern" -->
<!-- Examples: always with lunch, coffee then water AM, evening tea -->

## Correlations
<!-- What affects their hydration. Format: "factor: effect" -->
<!-- Examples: gym days: +500ml, hot weather: extra glass, coffee: follows with water -->

## Preferences
<!-- How they want hydration tracked. Format: "preference" -->
<!-- Examples: no reminders, just log silently, weekly summary only -->

## Flags
<!-- Signs of low hydration to watch. Format: "signal" -->
<!-- Examples: headache, fatigue, dark urine mentioned, skipped water at lunch -->
```

*Empty sections = no data yet. Observe and fill.*

---
