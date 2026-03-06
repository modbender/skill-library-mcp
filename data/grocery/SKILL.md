---
name: Grocery
slug: grocery
version: 1.0.0
description: Build and manage grocery lists with pantry inventory, household quantities, and dietary restriction safety.
metadata: {"clawdbot":{"emoji":"🛒","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User needs help with grocery shopping logistics — creating lists, tracking pantry inventory, remembering household quantities, or checking items against dietary restrictions. Focus: the shopping itself, not meal planning.

## Architecture

Memory lives in `~/grocery/`. See `memory-template.md` for setup.

```
~/grocery/
├── memory.md          # HOT: preferences, restrictions, current list
├── pantry.md          # WARM: what's at home, quantities, expiry
├── history.md         # COLD: past purchases, patterns
└── stores.md          # User's preferred stores, aisle layouts
```

## Quick Reference

| Topic | File |
|-------|------|
| Memory setup | `memory-template.md` |
| List operations | `lists.md` |

## Data Storage

All data stored in `~/grocery/`. Create on first use:
```bash
mkdir -p ~/grocery
```

## Scope

This skill ONLY:
- Maintains shopping lists from user input
- Tracks pantry inventory user reports
- Remembers dietary restrictions and preferences
- Suggests quantities based on household size

This skill NEVER:
- Accesses real store inventories or prices
- Makes purchases or places orders
- Scans barcodes or receipts
- Reads files outside `~/grocery/`

## Core Rules

### 1. Learn Household Context
| What to capture | Example |
|-----------------|---------|
| Household size | "2 adults, 1 picky toddler" |
| Dietary restrictions | "gluten-free, no shellfish" |
| Preferred stores | "Mercadona primary, Carrefour backup" |
| Typical quantities | "4L milk/week, not 1L" |

Store in memory.md on first mention. Never ask repeatedly.

### 2. Quantity Intelligence
- Default to household-appropriate portions (solo = small, family = bulk)
- Remember past quantities: "You usually get 2kg chicken"
- Flag unusual requests: "That's 3x your normal pasta amount — meal prep?"

### 3. Restriction Safety
- Always check new items against stored restrictions
- Know hidden names: caseína = dairy, gluten in soy sauce
- When uncertain: "Contains wheat — checking your restrictions: you're gluten-free. Skip?"

### 4. List Organization
- Group by store section when requested (produce, dairy, frozen)
- Support multiple active lists (weekly, party, camping)
- Deduplicate automatically, merge quantities

### 5. Pantry Awareness
When user reports what's home:
- Update pantry.md with quantities and dates
- Cross-check against list to avoid duplicates
- "You have 6 eggs at home — still adding 12 more?"

### 6. Recipe Input (Not Planning)
If user shares a recipe or meal:
- Extract ingredients to add to list
- Adjust for pantry stock
- Scale to household size
- Note: meal PLANNING belongs to `meals` skill — grocery just receives ingredient lists

## Common Traps

- Suggesting 4-person recipes to single person → check household size first
- Recommending exotic ingredients unavailable locally → stick to user's stores
- Forgetting restrictions between sessions → always load memory.md
- Ignoring "picky eater" family members → track per-person preferences

## Boundary with meals Skill

| grocery (this skill) | meals (different skill) |
|---------------------|------------------------|
| What to BUY | What to EAT |
| Pantry inventory | Weekly meal plan |
| Quantities, brands | Recipes, variety |
| Restriction safety | Dietary balance |
| Store organization | Meal scheduling |

If user asks "what should I eat this week?" → suggest `meals` skill.
This skill handles: "what do I need to buy?"
