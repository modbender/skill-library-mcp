# Memory Template — Meal Planner

Create `~/meal-planner/memory.md` with this structure:

```markdown
# Meal Planner Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | done | declined

## Household
<!-- Who you're cooking for -->

### Members
| Name | Age Group | Notes |
|------|-----------|-------|
| [Name] | adult | Primary cook |
| [Name] | adult | |
| [Name] | child (8) | Picky, no mixed foods |

### Guests
<!-- Regular visitors, frequency -->

## Dietary

### Restrictions (CRITICAL)
<!-- Allergies = life-threatening, intolerance = discomfort, preference = choice -->
| Person | Type | Severity | Notes |
|--------|------|----------|-------|
| [Name] | Shellfish | Allergy | Carries EpiPen |
| [Name] | Lactose | Intolerance | Can handle small amounts |
| [Name] | Red meat | Preference | Ethical choice |

### Dietary Approach
<!-- vegetarian, pescatarian, keto, etc. — whole household or per person -->

### Universal Dislikes
<!-- Foods NO ONE in household wants -->

## Preferences

### Cuisine
<!-- Italian, Mexican, Asian, comfort food, etc. -->

### Favorites
<!-- Specific meals that always work -->

### Tired Of
<!-- Things to avoid for now — rotate back later -->

### Cooking Style
skill-level: beginner | intermediate | advanced
weeknight-time: X minutes max
weekend-time: flexible | X minutes
batch-cooking: yes | no | sometimes
enjoys-cooking: yes | sometimes | no

## Budget

### Target
weekly-target: $XXX
tracking: active | passive | none

### Notes
<!-- Store preferences, brand preferences, bulk buying habits -->

## Logistics

### Shopping
preferred-store: [store name]
shopping-day: [day of week]
online-delivery: yes | no

### Kitchen Notes
<!-- Equipment limitations, storage capacity, etc. -->

## Patterns Observed
<!-- Things learned from behavior, not explicitly stated -->
<!-- "Always orders pizza on Fridays" → maybe plan easy Friday dinners -->
<!-- "Skips breakfast mentions" → don't plan breakfasts unless asked -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning preferences | Gather context, suggest gently |
| `complete` | Has solid understanding | Plan confidently |
| `paused` | User said "not now" | Work with what you have |
| `never_ask` | User said stop asking | Never probe for preferences |

## Key Principles

- **Restrictions are sacred** — always check before suggesting
- **Learn from feedback** — "that was too much work" → note time constraints
- **Observe patterns** — meal history tells you more than questions
- **Don't over-ask** — preferences emerge through cooking together
- Update `last` on each planning session
