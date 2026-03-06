---
name: Meals
description: Build a personal meal planning system with weekly plans, shopping lists, and dietary tracking.
metadata: {"clawdbot":{"emoji":"🍽️","os":["linux","darwin","win32"]}}
---

## Core Behavior
- User plans their week → help organize meals
- Generate shopping lists → from planned meals
- Track what works → build personal meal database
- Create `~/meals/` as workspace

## When User Plans Meals
- Ask about the week: how many dinners, lunches to plan
- Consider constraints: busy nights need quick meals
- Balance variety: not pasta three nights in a row
- Note who's eating: family size, guests

## Meal Database
Build personal collection over time:
- Meals you actually make (not aspirational)
- Prep time and cook time
- Serves how many
- Dietary tags: vegetarian, gluten-free, dairy-free
- Difficulty: quick weeknight vs weekend project

## Weekly Plan Structure
```
~/meals/
├── plans/
│   └── 2024-week-11.md
├── meals/
│   ├── chicken-stir-fry.md
│   └── pasta-carbonara.md
├── shopping/
└── preferences.md
```

## Weekly Plan Format
Simple table or list:
- Monday: Chicken stir-fry
- Tuesday: Leftovers
- Wednesday: Pasta carbonara
- Thursday: Takeout (busy night)
- Friday: Pizza night
- Weekend: Flexible

## Shopping List Generation
- Aggregate ingredients from planned meals
- Combine quantities: 2 onions + 1 onion = 3 onions
- Group by store section: produce, dairy, meat, pantry
- Exclude pantry staples user always has

## Pantry Staples
Track what user always has:
- Salt, pepper, olive oil, garlic
- Rice, pasta, common spices
- Subtract from shopping lists automatically
- Update when they run out

## Meal Preferences
- Dietary restrictions: allergies, intolerances, choices
- Dislikes: "no mushrooms"
- Favorites: quick go-to meals
- Cuisine preferences: Mexican Mondays, etc.

## Progressive Enhancement
- Week 1: plan a few dinners, make shopping list
- Week 2: save meals that worked to database
- Month 2: use past meals to speed planning
- Month 3: pattern-based suggestions

## Quick Weeknight Filters
Tag meals by time:
- Under 30 minutes
- One-pot/sheet pan
- No-cook
- Make ahead
- Freezer-friendly

## Batch Cooking Support
- Sunday prep suggestions
- Meals that share ingredients
- Components that work multiple ways
- Proteins: cook once, use twice

## What To Surface
- "Last week you made tacos on Tuesday — repeat or vary?"
- "You have chicken planned twice — intentional?"
- "Haven't made salmon in 3 weeks"
- "That pasta dish was rated 5 stars last time"

## Leftovers Planning
- Big batch Sunday → leftovers Monday lunch
- Transform leftovers: roast chicken → chicken salad
- Note which meals keep well
- Freeze portions for future lazy nights

## Meal Ratings
After cooking:
- Quick rating: made again? yes/no/maybe
- What to adjust next time
- Family feedback
- Builds data for future suggestions

## Dietary Tracking (Optional)
- Not calorie counting — that's separate
- Balance across week: enough vegetables?
- Variety: different proteins, cuisines
- Special needs: iron-rich meals, high-protein days

## What NOT To Suggest
- Complex meal prep before simple planning works
- Calorie tracking in meal planner — different concern
- Ambitious recipes on busy nights
- New recipes every night — repeats are fine

## Integration Points
- Recipes: link to full recipe files
- Shopping: export list to preferred format
- Calendar: note dinner guests, events
- Budget: track spending if wanted

## Seasonal Awareness
- Summer: grilling, salads, no-cook
- Winter: soups, stews, comfort food
- Seasonal produce: what's good now
- Holiday meal planning
