---
name: Meal Planner
slug: meal-planner
version: 1.0.0
homepage: https://clawic.com/skills/meal-planner
description: Plan meals with weekly menus, shopping lists, batch cooking, budget tracking, dietary preferences, and recipe management.
metadata: {"clawdbot":{"emoji":"🍽️","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` for onboarding guidelines. Start helping naturally without technical jargon — users can always ask about storage details if curious.

## When to Use

User wants to plan meals, generate shopping lists, track food budget, organize recipes, coordinate household eating, or reduce food waste. Agent handles the full meal lifecycle: planning, shopping, cooking, and reviewing.

## Architecture

Memory lives in `~/meal-planner/`. See `memory-template.md` for structure.

```
~/meal-planner/
├── memory.md              # Preferences + dietary info + household
├── weeks/                 # Weekly meal plans
│   └── YYYY-WXX.md        # Week 12 of 2026 = 2026-W12.md
├── recipes/               # Saved recipes
│   └── {recipe-name}.md
├── shopping/              # Shopping lists
│   └── YYYY-MM-DD.md
├── inventory/             # What's in pantry/fridge
│   ├── pantry.md
│   └── fridge.md
├── templates/             # Reusable meal templates
│   └── {template-name}.md
└── archive/               # Past weeks for reference
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |
| Shopping optimization | `shopping-guide.md` |
| Batch cooking | `meal-prep.md` |
| Budget tracking | `budget-tips.md` |

## Core Rules

### 1. Check Memory First
Before any meal planning, read `~/meal-planner/memory.md` for:
- Dietary restrictions and allergies (critical for safety)
- Household composition (adults, kids, guests)
- Cooking skill level and time constraints
- Budget targets and preferences
- Cuisine preferences and dislikes

### 2. Meal Planning Lifecycle
| Phase | Action |
|-------|--------|
| Plan | Create week file in `weeks/` with all meals |
| Shop | Generate shopping list from week plan |
| Prep | Suggest batch cooking opportunities |
| Cook | Reference recipes, adjust portions |
| Review | Note what worked, update preferences |

### 3. Weekly Planning Rhythm
When user asks to plan meals:
- Check inventory first (avoid buying duplicates)
- Balance nutrition across the week
- Cluster similar ingredients (reduce waste)
- Plan leftovers strategically (cook once, eat twice)
- Leave 1-2 flex slots for spontaneity or eating out

### 4. Shopping List Generation
For each shopping trip:
```markdown
## Shopping List — YYYY-MM-DD

### Produce
- [ ] Onions (3) — Mon stir-fry, Wed soup
- [ ] Spinach (1 bag) — Tue smoothie, Thu salad

### Proteins
- [ ] Chicken breast (1.5 lb) — Mon, Wed meals

### Pantry (only if low)
- [ ] Olive oil — check inventory first

**Budget estimate:** $XX
**Store suggestions:** [based on preferences]
```
Link items to meals so user knows why they're buying each thing.

### 5. Dietary Safety
For any dietary restrictions or allergies:
- Flag incompatible recipes BEFORE suggesting
- Check ingredient lists thoroughly
- Suggest substitutions when possible
- Never assume "a little bit is fine"
- Mark severity: preference vs. intolerance vs. allergy (life-threatening)

### 6. Household Coordination
When cooking for multiple people:
- Track individual restrictions per person
- Note kid-friendly vs. adult portions
- Plan meals everyone can eat (or easy modifications)
- Track who likes what (reduce "I don't want that" moments)

### 7. Budget Optimization
| Strategy | Typical Savings | When to Apply |
|----------|-----------------|---------------|
| Seasonal produce | 20-40% | Always check what's in season |
| Batch cooking | 30% time, 15% cost | Busy weeks |
| Protein rotation | 15-25% | Alternate expensive/cheap proteins |
| Pantry meals | 50%+ | End of budget cycle |
| Store brands | 10-30% | Most staples |

## Weekly Plan Format

```markdown
# Week YYYY-WXX

## Overview
- Budget target: $XXX
- Dietary focus: [any theme]
- Special events: [guests, holidays]

## Monday
**Breakfast:** [meal] | Prep: X min
**Lunch:** [meal] | Prep: X min
**Dinner:** [meal] | Prep: X min | Recipe: `recipes/meal.md`

## Tuesday
...

## Batch Prep (Sunday)
- [ ] Cook rice for Mon/Tue/Wed
- [ ] Chop vegetables for week
- [ ] Marinate Thu chicken

## Shopping Needed
[Auto-generated from meals above]
```

## Recipe Format

```markdown
# {Recipe Name}

**Time:** Prep X min | Cook Y min
**Serves:** X (easily doubled)
**Difficulty:** Easy | Medium | Advanced
**Dietary:** vegetarian, gluten-free, etc.

## Ingredients
- X cups ingredient — substitute: [alt]
- Y tbsp ingredient

## Instructions
1. Step one
2. Step two

## Notes
- Pairs well with: [sides]
- Storage: X days fridge, Y months freezer
- Kid modification: [if applicable]

## History
- YYYY-MM-DD: Made it, family loved it
- YYYY-MM-DD: Added more garlic next time
```

## Inventory Management

Proactively ask about inventory updates:
- After shopping trips: "Want to update what you bought?"
- When planning: "Checking pantry — last update was X days ago"
- For staples: track approximate quantities (full, half, low, out)

```markdown
## Pantry — Updated YYYY-MM-DD

### Grains & Pasta
| Item | Status | Notes |
|------|--------|-------|
| Rice | Full | 5 lb bag |
| Pasta | Half | |

### Canned Goods
...

### Spices
...
```

## Common Traps

- Planning without checking inventory → duplicate purchases, waste
- Overambitious meal plans → exhaustion, ordering takeout
- Ignoring prep time → not just cook time, total time matters
- Same proteins all week → meal fatigue, nutrition gaps
- No flex meals → rigid plans break under real life
- Forgetting leftovers → food waste
- Not tracking what worked → repeating failures

## Security & Privacy

**Data that stays local:**
- All meal plans, recipes, shopping lists stored in `~/meal-planner/`
- Dietary restrictions and household info in `~/meal-planner/memory.md`
- No cloud sync, no external services

**This skill does NOT:**
- Send any data to external servers
- Access health apps or fitness trackers
- Store payment information
- Read files outside `~/meal-planner/`

**User consent:**
- Files created only when user engages with meal planning
- User can view/edit all stored data directly (plain markdown)
- User can delete `~/meal-planner/` at any time to remove all data

## Scope

This skill ONLY:
- Manages meal planning in `~/meal-planner/`
- Reads/writes markdown files for plans, recipes, shopping
- Suggests based on preferences and inventory

This skill NEVER:
- Orders groceries (provides list for user to order)
- Accesses health apps or fitness trackers
- Stores payment information
- Reads files outside `~/meal-planner/`
- Provides medical nutrition advice (refer to dietitian for health conditions)

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `grocery` — detailed grocery management
- `cooking` — cooking techniques and tips
- `nutrition` — nutritional tracking and analysis
- `recipe` — recipe discovery and management
- `daily-planner` — daily task management

## Feedback

- If useful: `clawhub star meal-planner`
- Stay updated: `clawhub sync`
