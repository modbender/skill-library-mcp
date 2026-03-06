---
name: Restaurants
description: Build a personal restaurant system for tracking places to try, favorites, and dining memories.
metadata: {"clawdbot":{"emoji":"🍽️","os":["linux","darwin","win32"]}}
---

## Core Behavior
- User mentions restaurant → offer to save with notes
- User asks for recommendation → check their saved places first
- User returns from meal → help document experience
- Create `~/restaurants/` as workspace

## File Structure
```
~/restaurants/
├── to-try/
├── favorites/
├── visited/
│   └── 2024/
├── by-cuisine/
└── by-occasion/
```

## To-Try Entry
```markdown
# sushi-nakazawa.md
## Location
West Village, NYC

## Cuisine
Omakase sushi

## Source
Friend recommendation

## Price Range
$$$$

## Notes
Need reservation weeks ahead
```

## Visited Entry
```markdown
# la-mercerie-2024-03.md
## Date
March 15, 2024

## Occasion
Anniversary dinner

## What We Ordered
- Burrata (excellent)
- Duck breast (slightly dry)
- Chocolate soufflé (must order)

## Verdict
★★★★☆ — Would return for brunch
```

## Favorites
```markdown
# joes-pizza.md
## Go-To Order
Plain slice, extra crispy

## Best For
Quick lunch, late night

## Notes
Cash only, expect line
```

## By-Cuisine and By-Occasion
Simple lists linking to favorites:
```markdown
# date-night.md
- La Mercerie — beautiful space
- Via Carota — classic Village
- Carbone — never fails
```

## What To Track
- Location and neighborhood
- Cuisine type
- Price range: $ to $$$$
- Reservation: needed? how far ahead?
- Standout dishes
- Rating after visit

## Surfacing Recommendations
When user asks "where should we eat":
- Ask occasion and cuisine preference
- Check THEIR saved places first
- Suggest from their data before general knowledge

## What To Surface
- "You haven't tried that sushi place on your list"
- "Last Italian you loved was L'Artusi"
- "For date night you rated La Mercerie highest"

## Progressive Enhancement
- Start: add 5 places to try
- After meals: quick entry with verdict
- Build cuisine and occasion lists over time

## What NOT To Do
- Recommend unsaved places without asking
- Forget dietary restrictions
- Over-organize — simple notes work
