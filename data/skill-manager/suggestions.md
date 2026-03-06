# Context-Based Skill Suggestions

Reference — when to suggest skills based on current task.

## Trigger: Current Task Context

Suggest a skill when the **current task** involves:

**Specific tools/services:**
- User mentions Stripe → "There's a stripe skill, want it?"
- User works with GitHub PRs → "github skill could help"
- User asks about AWS → check for aws skill

**Unfamiliar domains:**
- Legal document → "legal skill might help here"
- Medical terminology → "medical skill exists"

**Explicit request:**
- User says "is there a better way" → search for skills

## NOT Triggers

Do NOT suggest based on:
- Counting how many times user does something
- Inferring struggle from behavior
- Tracking suggestion frequency

## How to Suggest

**In context:**
> "Since you're working with [X], there's a skill for that. Want me to install it?"

**Brief:**
> "There's a [domain] skill that could help here. Interested?"

## After Suggestion

- User says yes → install and track in inventory
- User says no → ask reason, store in Declined section
- User ignores → do nothing

## Declined Skills

When user declines, store their stated reason in `~/skill-manager/inventory.md`:
```
## Declined
- slug — "reason user gave"
```

Don't re-suggest declined skills unless user explicitly asks.

## Difference from skill-finder

| skill-finder | skill-manager |
|--------------|---------------|
| User asks "find skill for X" | You notice context opportunity |
| Reactive search | Proactive suggestion |
| One-time lookup | Ongoing lifecycle |
